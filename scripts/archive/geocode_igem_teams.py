"""
geocode_igem_teams.py — fill city, lat, lon for iGEM teams using a three-tier pipeline.

Why not plain Nominatim?
  Nominatim is a place database, not an institution database. Querying it with
  institution names like "Osaka Univ." can return the wrong country entirely.
  The APIs below are purpose-built for research organisations.

Three-tier pipeline for teams that have no city (years 2009-2023):

  Tier 1 — OpenAlex institutions API
    Covers ~100k research organisations with structured geo data.
    Filters by country code to prevent cross-country false positives.

  Tier 2 — ROR (Research Organization Registry)
    Broader coverage than OpenAlex (includes high schools, community labs).
    Used as fallback when OpenAlex returns no result.

  Tier 3 — Ollama (qwen2.5:3b, running locally)
    For names that neither database can match (abbreviations, unusual formats).
    The model extracts city + country, which is then geocoded with Nominatim.

Pass 2 (teams with city but no lat/lon):
    Geocodes existing city + country directly with Nominatim.

Caching:
    All results cached in data/geo/igem_geocoding_cache.json with tier-prefixed
    keys so each tier's data is distinguishable. Re-runs skip cached entries.

Usage:
    python scripts/geocode_igem_teams.py
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import pandas as pd
import pycountry
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

CSV_PATH   = REPO_ROOT / "data" / "raw" / "projects" / "igem_teams_with_descriptions_2004_2025.csv"
CACHE_PATH = REPO_ROOT / "data" / "geo" / "igem_geocoding_cache.json"

OPENALEX_BASE = "https://api.openalex.org/institutions"
ROR_BASE      = "https://api.ror.org/v2/organizations"
OLLAMA_MODEL  = "qwen2.5:3b"
NOMINATIM_DELAY = 1.1
REQUEST_DELAY   = 1.0   # OpenAlex / ROR polite delay (OpenAlex rate-limits at ~1 req/s)
OLLAMA_BATCH    = 30    # institutions per LLM call

# Keys to try when extracting a city name from a Nominatim address dict
CITY_KEYS = ["city", "town", "village", "municipality", "county", "state_district"]


# ---------------------------------------------------------------------------
# Country code helpers
# ---------------------------------------------------------------------------

def _iso3_to_iso2(iso3: str) -> str | None:
    try:
        return pycountry.countries.get(alpha_3=iso3).alpha_2
    except AttributeError:
        return None


def _country_name(iso3: str) -> str:
    try:
        return pycountry.countries.get(alpha_3=iso3).name
    except AttributeError:
        return ""


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def load_cache() -> dict:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CACHE_PATH.exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def save_cache(cache: dict) -> None:
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


# ---------------------------------------------------------------------------
# Tier 1 — OpenAlex institutions
# ---------------------------------------------------------------------------

def lookup_openalex(institution: str, iso3: str, cache: dict) -> dict | None:
    """
    Search the OpenAlex institutions API for an organisation by name.

    OpenAlex covers ~100k research institutions worldwide and supports
    country_code filtering to avoid cross-country false positives.
    Reference: Priem et al. (2022) "OpenAlex: A fully-open index of the world's
    research output." arXiv:2205.01833.
    """
    iso2 = _iso3_to_iso2(iso3)
    key = f"openalex:{institution}:{iso3}"
    if key in cache:
        return cache[key]

    params = {"search": institution, "per_page": 1}
    if iso2:
        params["filter"] = f"country_code:{iso2}"

    # Retry once on 429 (rate limit) with a longer back-off before giving up.
    for attempt in range(2):
        time.sleep(REQUEST_DELAY if attempt == 0 else 5.0)
        try:
            r = requests.get(OPENALEX_BASE, params=params, timeout=15,
                             headers={"User-Agent": "synbio-igem-geocoder"})
            if r.status_code == 429:
                if attempt == 0:
                    continue   # retry after back-off
                cache[key] = None
                return None
            r.raise_for_status()
            results = r.json().get("results", [])
            break
        except Exception as e:
            print(f"  OpenAlex error for '{institution}': {e}", flush=True)
            cache[key] = None
            return None
    else:
        cache[key] = None
        return None

    if not results:
        cache[key] = None
        return None

    geo = results[0].get("geo") or {}
    if not geo.get("latitude"):
        cache[key] = None
        return None

    result = {
        "city": geo.get("city", ""),
        "lat":  geo["latitude"],
        "lon":  geo["longitude"],
    }
    cache[key] = result
    return result


# ---------------------------------------------------------------------------
# Tier 2 — ROR
# ---------------------------------------------------------------------------

def lookup_ror(institution: str, iso3: str, cache: dict) -> dict | None:
    """
    Search the Research Organization Registry (ROR) for an organisation.

    ROR covers ~100k organisations including non-university institutions
    (high schools, community labs, companies) that may not appear in OpenAlex.
    Reference: Lammey (2020) "ROR: The Research Organization Registry."
    Science Editing 7(1), pp. 67-71.
    """
    iso2 = _iso3_to_iso2(iso3)
    key = f"ror:{institution}:{iso3}"
    if key in cache:
        return cache[key]

    time.sleep(REQUEST_DELAY)
    try:
        # Note: ROR v2 does not accept a page_size parameter; default returns 20 results
        r = requests.get(ROR_BASE, params={"query": institution},
                         timeout=15, headers={"User-Agent": "synbio-igem-geocoder"})
        r.raise_for_status()
        items = r.json().get("items", [])
    except Exception as e:
        print(f"  ROR error for '{institution}': {e}", flush=True)
        cache[key] = None
        return None

    # Filter to correct country then take the first matching result
    for item in items:
        locs = item.get("locations") or []
        if not locs:
            continue
        gd = locs[0].get("geonames_details") or {}
        if iso2 and gd.get("country_code", "").upper() != iso2.upper():
            continue
        if not gd.get("lat"):
            continue
        result = {
            "city": gd.get("name", ""),   # ROR v2 uses "name", not "city_name"
            "lat":  gd["lat"],
            "lon":  gd["lng"],
        }
        cache[key] = result
        return result

    cache[key] = None
    return None


# ---------------------------------------------------------------------------
# Tier 3 — Claude Haiku LLM extraction → Nominatim
# ---------------------------------------------------------------------------

def _build_nominatim():
    from geopy.geocoders import Nominatim
    return Nominatim(user_agent="synbio-igem-geocoder")


def _load_api_key() -> str:
    """Read ANTHROPIC_API_KEY from environment or .env file."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        env_path = REPO_ROOT / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    break
    return key


def batch_llm_extract(pairs: list[tuple[str, str, str]], cache: dict) -> dict:
    """
    Use Claude Haiku to extract city + country from institution names.

    Called only for institution+country pairs that OpenAlex and ROR both failed
    to match. Processes in batches for efficiency.

    Each entry is (institution, iso3, team_name). The team name is included in
    the prompt as extra context — many iGEM institutions have vague names like
    "Department of Microbiology" but the team name (e.g. "CBNU-Korea") encodes
    the parent university, which the model can use to infer the city.

    Benchmarks vs Ollama qwen2.5:3b on 20 iGEM test cases:
      Claude Haiku: 20/20 (100%), 0.12s/item
      Ollama:        7/20  (35%), 0.89s/item

    Returns a dict mapping (institution, iso3, team_name) → {"city": str, "country": str}.
    """
    import anthropic

    api_key = _load_api_key()
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not found. Set it in .env or as an environment variable."
        )
    client = anthropic.Anthropic(api_key=api_key)

    # When institution is blank, key by team name to avoid collisions
    def _llm_key(inst, iso3, team):
        return f"llm:{inst}:{iso3}" if inst else f"llm:{team}:{iso3}"

    # Filter to pairs not already cached
    todo = [(inst, iso3, team) for inst, iso3, team in pairs
            if _llm_key(inst, iso3, team) not in cache]
    if not todo:
        return {}

    print(f"  Haiku: extracting city from {len(todo)} institution names…", flush=True)
    results = {}

    for batch_start in range(0, len(todo), OLLAMA_BATCH):
        batch = todo[batch_start : batch_start + OLLAMA_BATCH]

        # Include team name alongside institution name for context.
        # This helps when the institution alone is too generic (e.g. a department
        # name) but the team name encodes the parent university abbreviation.
        lines = "\n".join(
            (f'{i+1}. Institution: "{inst}" | Team name: "{team}" | Country ISO3: {iso3}'
             if inst else
             f'{i+1}. Team name: "{team}" | Country ISO3: {iso3} (institution unknown)')
            for i, (inst, iso3, team) in enumerate(batch)
        )
        prompt = (
            "You are a geocoding assistant. For each entry below, use both the "
            "institution name AND the team name as clues to identify the city "
            "the institution is located in.\n"
            "Reply ONLY with a valid JSON array — no explanation, no markdown.\n"
            'Each element: {"city": "...", "country": "..."}\n'
            "If you are unsure, make your best guess.\n\n"
            f"Entries:\n{lines}"
        )

        try:
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text.strip()
            match = re.search(r'\[.*\]', raw, re.DOTALL)
            parsed = json.loads(match.group(0)) if match else []
        except Exception as e:
            print(f"  Haiku error on batch {batch_start}: {e}", flush=True)
            parsed = []

        for i, (inst, iso3, team) in enumerate(batch):
            entry = parsed[i] if i < len(parsed) else {}
            city    = entry.get("city", "")
            country = entry.get("country", "")
            result  = {"city": city, "country": country}
            cache[_llm_key(inst, iso3, team)] = result
            results[(inst, iso3, team)] = result

        print(f"  Haiku: {min(batch_start + OLLAMA_BATCH, len(todo))}/{len(todo)} done",
              flush=True)

    return results


def geocode_city_nominatim(nominatim, city: str, iso3: str, cache: dict) -> dict | None:
    """Geocode a clean city string with Nominatim, constrained to country."""
    from geopy.geocoders import Nominatim  # noqa
    iso2 = _iso3_to_iso2(iso3)
    key = f"city:{city}:{iso3}"
    if key in cache:
        return cache[key]

    time.sleep(NOMINATIM_DELAY)
    try:
        kwargs = {"addressdetails": True, "language": "en"}
        if iso2:
            kwargs["country_codes"] = iso2
        loc = nominatim.geocode(city, **kwargs)
        if not loc:
            cache[key] = None
            return None
        addr = loc.raw.get("address", {})
        resolved_city = next((addr[k] for k in CITY_KEYS if k in addr), city)
        result = {"city": resolved_city, "lat": loc.latitude, "lon": loc.longitude}
    except Exception as e:
        print(f"  Nominatim error for '{city}': {e}", flush=True)
        result = None

    cache[key] = result
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} teams from {CSV_PATH.name}\n")

    cache = load_cache()
    nom   = _build_nominatim()

    # One-time fix: purge ROR cache entries where city is empty-string.
    # These were produced by a bug that read "city_name" instead of "name"
    # from the ROR geonames_details object. Re-fetching will now return
    # the correct city name using the fixed field.
    bad_ror = [k for k, v in cache.items()
               if k.startswith("ror:") and isinstance(v, dict) and v.get("city") == ""]
    if bad_ror:
        for k in bad_ror:
            del cache[k]
        save_cache(cache)
        print(f"Purged {len(bad_ror)} bad ROR cache entries (empty city bug). Re-fetching…\n")

    # ------------------------------------------------------------------
    # Pass 1: institution → city + lat/lon  (teams where city is null)
    # ------------------------------------------------------------------
    no_city = df["city"].isna()

    # Pairs where institution is known (skip URL-only entries)
    inst_pairs_df = (
        df[no_city & df["institution"].notna() &
           ~df["institution"].str.startswith("http", na=False) &
           (df["institution"].str.strip() != "")]
        [["institution", "country", "name"]]
        .drop_duplicates(subset=["institution", "country"])
        .reset_index(drop=True)
    )

    # Pairs where institution is blank — go straight to Haiku using team name
    blank_inst_df = (
        df[no_city & (df["institution"].isna() | (df["institution"].str.strip() == ""))]
        [["name", "country"]]
        .assign(institution="")
        [["institution", "country", "name"]]
        .drop_duplicates(subset=["name", "country"])
        .reset_index(drop=True)
    )

    pairs_df = pd.concat([inst_pairs_df, blank_inst_df], ignore_index=True)
    pairs = list(zip(pairs_df["institution"], pairs_df["country"], pairs_df["name"]))
    print(f"Pass 1: {no_city.sum()} teams without city → {len(pairs)} unique pairs "
          f"({len(inst_pairs_df)} with institution, {len(blank_inst_df)} team-name-only)")

    # --- Tier 1: OpenAlex ---
    oa_miss = []
    oa_hits = 0
    oa_cached = sum(1 for inst, iso3, _ in pairs if f"openalex:{inst}:{iso3}" in cache)
    print(f"  OpenAlex: {oa_cached} cached, {len(pairs)-oa_cached} to fetch")
    for i, (inst, iso3, team_name) in enumerate(pairs):
        if not inst:
            oa_miss.append((inst, iso3, team_name))  # no institution → skip to Haiku
            continue
        result = lookup_openalex(inst, iso3, cache)
        if result:
            oa_hits += 1
        else:
            oa_miss.append((inst, iso3, team_name))
        if (i + 1) % 200 == 0:
            save_cache(cache)
            print(f"    {i+1}/{len(pairs)} OpenAlex done…", flush=True)
    save_cache(cache)
    print(f"  OpenAlex: {oa_hits} found, {len(oa_miss)} still missing")

    # ROR (Research Organization Registry) was removed from the pipeline because
    # its fuzzy search returned wrong institutions for abbreviated names
    # (e.g. "Osaka Univ." → Shizuoka, "US Naval Academy" → New York).
    # OpenAlex misses go directly to Haiku, which is more accurate (100% vs ROR ~65%).
    ror_miss = oa_miss

    # --- Tier 2: Haiku → Nominatim ---
    if ror_miss:
        llm_results = batch_llm_extract(ror_miss, cache)
        save_cache(cache)

        nom_hits = 0
        for (inst, iso3, team), llm in llm_results.items():
            city = llm.get("city", "")
            if not city:
                continue
            geo = geocode_city_nominatim(nom, city, iso3, cache)
            if geo:
                # Key by team name when institution is blank
                nom_key = f"nom:{inst}:{iso3}" if inst else f"nom:{team}:{iso3}"
                cache[nom_key] = geo
                nom_hits += 1
        save_cache(cache)
        print(f"  Ollama+Nominatim: {nom_hits}/{len(ror_miss)} resolved")

    # --- Apply Pass 1 results ---
    filled_city = filled_coords = 0
    for inst, iso3, team_name in pairs:
        if inst:
            result = (
                cache.get(f"openalex:{inst}:{iso3}") or
                cache.get(f"nom:{inst}:{iso3}")
            )
            mask = no_city & (df["institution"] == inst) & (df["country"] == iso3)
        else:
            result = cache.get(f"nom:{team_name}:{iso3}")
            mask = (no_city &
                    df["institution"].isna() &
                    (df["name"] == team_name) &
                    (df["country"] == iso3))
        if not result:
            continue
        if result.get("city"):
            df.loc[mask, "city"] = result["city"]
            filled_city += mask.sum()
        df.loc[mask, "lat"] = result["lat"]
        df.loc[mask, "lon"] = result["lon"]
        filled_coords += mask.sum()
    print(f"\nPass 1 applied: city filled for {filled_city} rows, lat/lon for {filled_coords} rows")

    # ------------------------------------------------------------------
    # Pass 2: city + country → lat/lon  (teams with city but no coords)
    # ------------------------------------------------------------------
    needs_latlon = df["city"].notna() & df["lat"].isna()
    p2_pairs = (
        df[needs_latlon][["city", "country"]]
        .drop_duplicates()
    )
    print(f"\nPass 2: {needs_latlon.sum()} teams with city but no lat/lon → {len(p2_pairs)} unique pairs")
    p2_cached = sum(1 for _, r in p2_pairs.iterrows() if f"city:{r['city']}:{r['country']}" in cache)
    print(f"  Cached: {p2_cached}, to fetch: {len(p2_pairs)-p2_cached}")

    for i, (_, row) in enumerate(p2_pairs.iterrows()):
        geocode_city_nominatim(nom, row["city"], row["country"], cache)
        if (i + 1) % 100 == 0:
            save_cache(cache)
            print(f"  {i+1}/{len(p2_pairs)} done…", flush=True)
    save_cache(cache)

    filled_p2 = 0
    for _, row in p2_pairs.iterrows():
        result = cache.get(f"city:{row['city']}:{row['country']}")
        if not result:
            continue
        mask = needs_latlon & (df["city"] == row["city"]) & (df["country"] == row["country"])
        df.loc[mask, "lat"] = result["lat"]
        df.loc[mask, "lon"] = result["lon"]
        filled_p2 += mask.sum()
    print(f"Pass 2 applied: lat/lon filled for {filled_p2} rows")

    # ------------------------------------------------------------------
    # Pass 3: hard-code country-level regions that Nominatim can't resolve
    # ------------------------------------------------------------------
    # HKG and MAC are country-level ISO codes — Nominatim has no sub-national
    # city to match when constrained by country_codes=HK or MO.
    # Country-level ISO codes where Nominatim has no sub-national city to match
    HARDCODED_COUNTRY = {
        "HKG": {"city": "Hong Kong", "lat": 22.3193, "lon": 114.1694},
        "MAC": {"city": "Macau",     "lat": 22.1987, "lon": 113.5439},
    }
    filled_p3 = 0
    for iso3, geo in HARDCODED_COUNTRY.items():
        mask = df["city"].isna() & (df["country"] == iso3)
        df.loc[mask, "city"] = geo["city"]
        df.loc[mask, "lat"]  = geo["lat"]
        df.loc[mask, "lon"]  = geo["lon"]
        filled_p3 += mask.sum()
        if mask.sum():
            print(f"Pass 3: filled {mask.sum()} {iso3} teams → {geo['city']}")

    # Teams with URL-only institutions or wrong country codes in the source data
    HARDCODED_TEAMS = {
        # team name                city               lat        lon
        "ArtScienceBangalore": ("Bangalore",       12.9716,   77.5946),  # Srishti Institute; IND
        "TzuChiU_Formosa":     ("Hualien",         23.9711,  121.6016),  # Tzu Chi Univ, Taiwan; src country=USA
        "SUSTC-Shenzhen-A":    ("Shenzhen",        22.5431,  114.0579),  # SUSTech; src country=USA
        "SUSTC-Shenzhen-B":    ("Shenzhen",        22.5431,  114.0579),  # SUSTech; src country=USA
        "LIKA-CESAR-Brasil":   ("Recife",          -8.0476,  -34.8770),  # UFPE LIKA; URL-only institution
        "Nagahama":            ("Nagahama",        35.3686,  136.2727),  # Nagahama Inst Bio-Science; src country=JEY
        "Tel-Hai":             ("Kiryat Shmona",   33.2075,   35.5689),  # Tel-Hai College; URL-only institution
        "Virginia":            ("Charlottesville", 38.0336,  -78.5080),  # Univ of Virginia; URL-only institution
        "SBS_NY":              ("Stony Brook",     40.9176,  -73.1276),  # The Stony Brook School; src country=CHN
        "UPRM":                ("Mayagüez",        18.2011,  -67.1397),  # Univ of Puerto Rico Mayagüez
        "The_Webb_Schools":    ("Claremont",       34.0967, -117.7198),  # The Webb Schools CA; src country=CHN
        "RUM-UPRM":            ("Mayagüez",        18.2011,  -67.1397),  # Univ of Puerto Rico Mayagüez
    }
    for team, (city, lat, lon) in HARDCODED_TEAMS.items():
        mask = df["city"].isna() & (df["name"] == team)
        df.loc[mask, "city"] = city
        df.loc[mask, "lat"]  = lat
        df.loc[mask, "lon"]  = lon
        filled_p3 += mask.sum()

    if filled_p3:
        print(f"Pass 3 applied: {filled_p3} rows filled")

    # ------------------------------------------------------------------
    # Summary and save
    # ------------------------------------------------------------------
    print(f"\n=== Final coverage ===")
    print(f"  city non-null : {df['city'].notna().sum()}/{len(df)}")
    print(f"  lat  non-null : {df['lat'].notna().sum()}/{len(df)}")
    print(f"  lon  non-null : {df['lon'].notna().sum()}/{len(df)}")

    still_missing = df[df["city"].isna()]["institution"].dropna().unique()
    print(f"\n  {len(still_missing)} institutions still unresolved:")
    for inst in still_missing[:20]:
        print(f"    - {inst}")
    if len(still_missing) > 20:
        print(f"    … and {len(still_missing)-20} more")

    # Normalize whitespace: replace any runs of \r \n \t with a single space.
    # iGEM institution descriptions sometimes embed raw newlines and tabs.
    import re as _re
    for col in df.select_dtypes(include="str").columns:
        df[col] = df[col].apply(
            lambda v: _re.sub(r'[\r\n\t]+', ' ', v).strip() if isinstance(v, str) else v
        )

    df.to_csv(CSV_PATH, index=False)
    print(f"\nSaved to {CSV_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
