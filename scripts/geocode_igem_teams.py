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
REQUEST_DELAY   = 0.6   # OpenAlex / ROR polite delay
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

    time.sleep(REQUEST_DELAY)
    try:
        r = requests.get(OPENALEX_BASE, params=params, timeout=15,
                         headers={"User-Agent": "synbio-igem-geocoder"})
        r.raise_for_status()
        results = r.json().get("results", [])
    except Exception as e:
        print(f"  OpenAlex error for '{institution}': {e}", flush=True)
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
        r = requests.get(ROR_BASE, params={"query": institution, "page_size": 5},
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
            "city": gd.get("city_name", ""),
            "lat":  gd["lat"],
            "lon":  gd["lng"],
        }
        cache[key] = result
        return result

    cache[key] = None
    return None


# ---------------------------------------------------------------------------
# Tier 3 — Ollama LLM extraction → Nominatim
# ---------------------------------------------------------------------------

def _build_nominatim():
    from geopy.geocoders import Nominatim
    return Nominatim(user_agent="synbio-igem-geocoder")


def batch_llm_extract(pairs: list[tuple[str, str]], cache: dict) -> dict:
    """
    Use a local Ollama model to extract city + country from institution names.

    Called only for institution+country pairs that OpenAlex and ROR both failed
    to match. Processes in batches for efficiency.

    Returns a dict mapping (institution, iso3) → {"city": str, "country": str}.
    """
    import ollama

    # Filter to pairs not already cached
    todo = [(inst, iso3) for inst, iso3 in pairs
            if f"llm:{inst}:{iso3}" not in cache]
    if not todo:
        return {}

    print(f"  Ollama: extracting city from {len(todo)} institution names…", flush=True)
    results = {}

    for batch_start in range(0, len(todo), OLLAMA_BATCH):
        batch = todo[batch_start : batch_start + OLLAMA_BATCH]

        # Build numbered list for the prompt
        lines = "\n".join(
            f'{i+1}. "{inst}" (country ISO3: {iso3})'
            for i, (inst, iso3) in enumerate(batch)
        )
        prompt = (
            "You are a geocoding assistant. For each institution below, return "
            "the city it is located in and the country name in English.\n"
            "Reply ONLY with a valid JSON array — no explanation, no markdown.\n"
            "Each element: {\"city\": \"...\", \"country\": \"...\"}\n"
            "If you are unsure, make your best guess.\n\n"
            f"Institutions:\n{lines}"
        )

        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0},
            )
            raw = response["message"]["content"].strip()
            # Extract outermost JSON array from the response
            match = re.search(r'\[.*\]', raw, re.DOTALL)
            parsed = json.loads(match.group(0)) if match else []
            # Flatten if the model returned [[{...}], [{...}]] instead of [{...}, {...}]
            parsed = [
                item[0] if isinstance(item, list) and item else item
                for item in parsed
            ]
        except Exception as e:
            print(f"  Ollama error on batch {batch_start}: {e}", flush=True)
            parsed = []

        for i, (inst, iso3) in enumerate(batch):
            entry = parsed[i] if i < len(parsed) else {}
            city    = entry.get("city", "")
            country = entry.get("country", "")
            result  = {"city": city, "country": country}
            cache[f"llm:{inst}:{iso3}"] = result
            results[(inst, iso3)] = result

        print(f"  Ollama: {min(batch_start + OLLAMA_BATCH, len(todo))}/{len(todo)} done",
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

    # ------------------------------------------------------------------
    # Pass 1: institution → city + lat/lon  (teams where city is null)
    # ------------------------------------------------------------------
    no_city = df["city"].isna()
    pairs_df = (
        df[no_city & df["institution"].notna() &
           ~df["institution"].str.startswith("http", na=False)]
        [["institution", "country"]]
        .drop_duplicates()
    )
    pairs = list(zip(pairs_df["institution"], pairs_df["country"]))
    print(f"Pass 1: {no_city.sum()} teams without city → {len(pairs)} unique institution+country pairs")

    # --- Tier 1: OpenAlex ---
    oa_miss = []
    oa_hits = 0
    oa_cached = sum(1 for inst, iso3 in pairs if f"openalex:{inst}:{iso3}" in cache)
    print(f"  OpenAlex: {oa_cached} cached, {len(pairs)-oa_cached} to fetch")
    for i, (inst, iso3) in enumerate(pairs):
        result = lookup_openalex(inst, iso3, cache)
        if result:
            oa_hits += 1
        else:
            oa_miss.append((inst, iso3))
        if (i + 1) % 200 == 0:
            save_cache(cache)
            print(f"    {i+1}/{len(pairs)} OpenAlex done…", flush=True)
    save_cache(cache)
    print(f"  OpenAlex: {oa_hits} found, {len(oa_miss)} still missing")

    # --- Tier 2: ROR ---
    ror_miss = []
    ror_hits = 0
    ror_cached = sum(1 for inst, iso3 in oa_miss if f"ror:{inst}:{iso3}" in cache)
    print(f"  ROR: {ror_cached} cached, {len(oa_miss)-ror_cached} to fetch")
    for i, (inst, iso3) in enumerate(oa_miss):
        result = lookup_ror(inst, iso3, cache)
        if result:
            ror_hits += 1
        else:
            ror_miss.append((inst, iso3))
        if (i + 1) % 100 == 0:
            save_cache(cache)
            print(f"    {i+1}/{len(oa_miss)} ROR done…", flush=True)
    save_cache(cache)
    print(f"  ROR: {ror_hits} found, {len(ror_miss)} still missing")

    # --- Tier 3: Ollama → Nominatim ---
    if ror_miss:
        llm_results = batch_llm_extract(ror_miss, cache)
        save_cache(cache)

        nom_hits = 0
        for (inst, iso3), llm in llm_results.items():
            city = llm.get("city", "")
            if not city:
                continue
            geo = geocode_city_nominatim(nom, city, iso3, cache)
            if geo:
                # Store result under the institution key so apply-step can find it
                cache[f"openalex:{inst}:{iso3}"] = geo   # reuse openalex key for apply step
                nom_hits += 1
        save_cache(cache)
        print(f"  Ollama+Nominatim: {nom_hits}/{len(ror_miss)} resolved")

    # --- Apply Pass 1 results ---
    filled_city = filled_coords = 0
    for inst, iso3 in pairs:
        result = (
            cache.get(f"openalex:{inst}:{iso3}") or
            cache.get(f"ror:{inst}:{iso3}")
        )
        if not result:
            continue
        mask = no_city & (df["institution"] == inst) & (df["country"] == iso3)
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

    df.to_csv(CSV_PATH, index=False)
    print(f"\nSaved to {CSV_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
