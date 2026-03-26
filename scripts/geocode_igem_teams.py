"""
geocode_igem_teams.py — fill city, lat, lon for iGEM teams.

Two passes:
  Pass 1 — teams with no city (years 2009-2023):
    Geocodes by institution name. Constrains Nominatim to the team's country
    using the countrycodes parameter, which prevents cross-country false positives
    (e.g. "Osaka Univ." matching a city in Utah instead of Japan).
    Common abbreviations are expanded before querying (e.g. "Univ." → "University").
    If Nominatim returns null, falls back to OpenCage.
    Fills city, lat, and lon.

  Pass 2 — teams with city but no lat/lon (years 2024-2025):
    Geocodes by city + country. Fills lat and lon only.

Why countrycodes matters:
  Without a country constraint, Nominatim's free-text search can match any
  location globally. A short or abbreviated institution name like "Osaka Univ."
  may rank a small US city above Osaka, Japan. Constraining to the correct
  ISO2 country code eliminates this class of error entirely.

Caching:
  All results are cached in data/geo/igem_geocoding_cache.json.
  Cache keys embed the country code so results are unambiguous.
  Re-running the script skips anything already cached.

Usage:
    python scripts/geocode_igem_teams.py

Requires:
    OPENCAGE_API_KEY in .env (used as fallback when Nominatim returns null)
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import pycountry

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")

CSV_PATH   = REPO_ROOT / "data" / "raw" / "projects" / "igem_teams_with_descriptions_2004_2025.csv"
CACHE_PATH = REPO_ROOT / "data" / "geo" / "igem_geocoding_cache.json"

NOMINATIM_DELAY = 1.1   # seconds — Nominatim policy: max 1 req/s
OPENCAGE_DELAY  = 0.5   # OpenCage free tier: 1 req/s, paid: 15 req/s
USER_AGENT = "synbio-igem-geocoder"

# Address fields to try when extracting a city name from a Nominatim response.
# Nominatim uses different keys depending on the settlement type.
CITY_KEYS = ["city", "town", "village", "municipality", "county", "state_district"]

# Common abbreviations found in iGEM institution names.
# Applied as whole-word replacements before geocoding.
ABBREV_MAP = {
    r"\bUniv\b\.?":   "University",
    r"\bInst\b\.?":   "Institute",
    r"\bTech\b\.?":   "Technology",
    r"\bNatl\b\.?":   "National",
    r"\bIntl\b\.?":   "International",
    r"\bDept\b\.?":   "Department",
    r"\bCol\b\.?":    "College",
    r"\bSci\b\.?":    "Science",
    r"\bEng\b\.?":    "Engineering",
    r"\bMed\b\.?":    "Medical",
    r"\bAcad\b\.?":   "Academy",
    r"\bLab\b\.?s?":  "Laboratory",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def iso3_to_iso2(iso3: str) -> str | None:
    """Convert an ISO 3166-1 alpha-3 country code to alpha-2 (e.g. 'JPN' → 'JP')."""
    try:
        return pycountry.countries.get(alpha_3=iso3).alpha_2.lower()
    except AttributeError:
        return None


def country_name(iso3: str) -> str:
    """Return the English country name for an ISO3 code (e.g. 'JPN' → 'Japan')."""
    try:
        return pycountry.countries.get(alpha_3=iso3).name
    except AttributeError:
        return ""


def expand_abbreviations(name: str) -> str:
    """Replace common abbreviations with full words."""
    for pattern, replacement in ABBREV_MAP.items():
        name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)
    return name.strip()


def extract_city(raw_address: dict) -> str:
    """Pick the best city-level name from a Nominatim address dict."""
    return next((raw_address[k] for k in CITY_KEYS if k in raw_address), "")


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
# Geocoders
# ---------------------------------------------------------------------------

def _build_nominatim():
    from geopy.geocoders import Nominatim
    return Nominatim(user_agent=USER_AGENT)


def _build_opencage():
    from geopy.geocoders import OpenCage
    api_key = os.getenv("OPENCAGE_API_KEY", "")
    if not api_key:
        return None
    return OpenCage(api_key=api_key)


def geocode_institution(nominatim, opencage, institution: str, iso3: str, cache: dict) -> dict | None:
    """
    Geocode an institution name constrained to its country.

    Strategy:
      1. Expand abbreviations in the institution name.
      2. Query Nominatim with countrycodes=<iso2> to prevent cross-country matches.
      3. If Nominatim returns null, fall back to OpenCage with country name appended.

    Returns {"city": str, "lat": float, "lon": float} or None.
    """
    if not institution or institution.startswith("http"):
        return None

    iso2 = iso3_to_iso2(iso3)
    cache_key = f"inst:{institution}:{iso3}"
    if cache_key in cache:
        return cache[cache_key]

    expanded = expand_abbreviations(institution)
    result = None

    # --- Nominatim (primary) ---
    time.sleep(NOMINATIM_DELAY)
    try:
        kwargs = {"addressdetails": True, "language": "en"}
        if iso2:
            kwargs["country_codes"] = iso2
        loc = nominatim.geocode(expanded, **kwargs)
        if loc:
            addr = loc.raw.get("address", {})
            result = {
                "city": extract_city(addr),
                "lat": loc.latitude,
                "lon": loc.longitude,
            }
    except Exception as e:
        print(f"  Nominatim error for '{expanded}': {e}", flush=True)

    # --- OpenCage fallback ---
    if result is None and opencage is not None:
        cname = country_name(iso3)
        query = f"{expanded}, {cname}".strip(", ")
        time.sleep(OPENCAGE_DELAY)
        try:
            loc = opencage.geocode(query, language="en")
            if loc:
                # OpenCage embeds address components in loc.raw["components"]
                components = loc.raw.get("components", {})
                city = (
                    components.get("city")
                    or components.get("town")
                    or components.get("village")
                    or components.get("municipality")
                    or ""
                )
                result = {"city": city, "lat": loc.latitude, "lon": loc.longitude}
        except Exception as e:
            print(f"  OpenCage error for '{query}': {e}", flush=True)

    cache[cache_key] = result
    return result


def geocode_city_country(nominatim, city: str, country_iso3: str, cache: dict) -> dict | None:
    """
    Geocode city + country for Pass 2 (fill lat/lon on teams that already have city).
    Returns {"lat": float, "lon": float} or None.
    """
    iso2 = iso3_to_iso2(country_iso3) or ""
    cache_key = f"city:{city}:{country_iso3}"
    if cache_key in cache:
        return cache[cache_key]

    query = city
    time.sleep(NOMINATIM_DELAY)
    try:
        kwargs = {"language": "en"}
        if iso2:
            kwargs["country_codes"] = iso2
        loc = nominatim.geocode(query, **kwargs)
        result = {"lat": loc.latitude, "lon": loc.longitude} if loc else None
    except Exception as e:
        print(f"  Nominatim error for '{query}': {e}", flush=True)
        result = None

    cache[cache_key] = result
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import pandas as pd

    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} teams from {CSV_PATH.name}")

    cache   = load_cache()
    nom     = _build_nominatim()
    oc      = _build_opencage()
    if oc is None:
        print("WARNING: OPENCAGE_API_KEY not found — Nominatim only, no fallback")

    # ------------------------------------------------------------------
    # Pass 1: institution → city + lat/lon (no-city rows)
    # ------------------------------------------------------------------
    no_city = df["city"].isna()
    pass1_df = df[no_city][["institution", "country"]].drop_duplicates()
    # Drop rows with URL-only or empty institution names
    pass1_df = pass1_df[
        pass1_df["institution"].notna() &
        ~pass1_df["institution"].str.startswith("http", na=False)
    ]

    already_cached = sum(
        1 for _, r in pass1_df.iterrows()
        if f"inst:{r['institution']}:{r['country']}" in cache
    )
    todo = len(pass1_df) - already_cached
    print(f"\nPass 1: {no_city.sum()} teams need city, {len(pass1_df)} unique institution+country pairs")
    print(f"  Cached: {already_cached}  |  To fetch: {todo}")

    done = 0
    for _, row in pass1_df.iterrows():
        geocode_institution(nom, oc, row["institution"], row["country"], cache)
        done += 1
        if done % 100 == 0:
            save_cache(cache)
            print(f"  {done}/{len(pass1_df)} done…", flush=True)
    save_cache(cache)

    # Apply Pass 1 to DataFrame
    filled_city = filled_coords = 0
    for _, row in pass1_df.iterrows():
        result = cache.get(f"inst:{row['institution']}:{row['country']}")
        if not result:
            continue
        mask = no_city & (df["institution"] == row["institution"]) & (df["country"] == row["country"])
        if result.get("city"):
            df.loc[mask, "city"] = result["city"]
            filled_city += mask.sum()
        df.loc[mask, "lat"] = result["lat"]
        df.loc[mask, "lon"] = result["lon"]
        filled_coords += mask.sum()

    print(f"  Filled city for {filled_city} rows, lat/lon for {filled_coords} rows")

    # ------------------------------------------------------------------
    # Pass 2: city + country → lat/lon (have city, missing coords)
    # ------------------------------------------------------------------
    needs_latlon = df["city"].notna() & df["lat"].isna()
    pass2_df = df[needs_latlon][["city", "country"]].drop_duplicates()

    already_p2 = sum(
        1 for _, r in pass2_df.iterrows()
        if f"city:{r['city']}:{r['country']}" in cache
    )
    print(f"\nPass 2: {needs_latlon.sum()} teams need lat/lon, {len(pass2_df)} unique city+country pairs")
    print(f"  Cached: {already_p2}  |  To fetch: {len(pass2_df) - already_p2}")

    done2 = 0
    for _, row in pass2_df.iterrows():
        geocode_city_country(nom, row["city"], row["country"], cache)
        done2 += 1
        if done2 % 100 == 0:
            save_cache(cache)
            print(f"  {done2}/{len(pass2_df)} done…", flush=True)
    save_cache(cache)

    # Apply Pass 2
    filled_p2 = 0
    for _, row in pass2_df.iterrows():
        result = cache.get(f"city:{row['city']}:{row['country']}")
        if not result:
            continue
        mask = needs_latlon & (df["city"] == row["city"]) & (df["country"] == row["country"])
        df.loc[mask, "lat"] = result["lat"]
        df.loc[mask, "lon"] = result["lon"]
        filled_p2 += mask.sum()
    print(f"  Filled lat/lon for {filled_p2} rows")

    # ------------------------------------------------------------------
    # Summary and save
    # ------------------------------------------------------------------
    print(f"\n=== Final coverage ===")
    print(f"  city non-null : {df['city'].notna().sum()}/{len(df)}")
    print(f"  lat  non-null : {df['lat'].notna().sum()}/{len(df)}")
    print(f"  lon  non-null : {df['lon'].notna().sum()}/{len(df)}")

    df.to_csv(CSV_PATH, index=False)
    print(f"\nSaved to {CSV_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
