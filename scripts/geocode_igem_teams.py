"""
geocode_igem_teams.py — fill city, lat, lon for iGEM teams.

Two passes:
  Pass 1 — teams with no city (years 2009-2023):
    Geocode by institution name using Nominatim.
    Extracts the city name from the address in the geocoder response, then
    fills city, lat, and lon.

  Pass 2 — teams with city but no lat/lon (years 2024-2025):
    Geocode by city + country using Nominatim.
    Fills lat and lon only.

Caching:
  Pass 1 results are cached by institution name.
  Pass 2 results are cached by "city, country" string.
  Both caches are stored in data/geo/igem_geocoding_cache.json and are
  keyed separately so they don't collide. Re-running the script skips
  any location already in the cache.

Rate limiting:
  Nominatim allows 1 request per second. We wait 1.1s between requests.
  With ~1,904 unique institutions + ~200 unique city/country pairs, this
  takes roughly 40 minutes. Re-runs finish in seconds (all cached).

Usage:
    python scripts/geocode_igem_teams.py
"""

import json
import sys
import time
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

CSV_PATH  = REPO_ROOT / "data" / "raw" / "projects" / "igem_teams_with_descriptions_2004_2025.csv"
CACHE_PATH = REPO_ROOT / "data" / "geo" / "igem_geocoding_cache.json"

NOMINATIM_DELAY = 1.1  # seconds between requests (Nominatim policy: max 1 req/s)
USER_AGENT = "synbio-igem-geocoder"

# When extracting city from a Nominatim address, try these keys in order.
# Nominatim uses different keys depending on the settlement type.
CITY_KEYS = ["city", "town", "village", "municipality", "county", "state_district"]


# ---------------------------------------------------------------------------
# Cache helpers
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
# Geocoding
# ---------------------------------------------------------------------------

def _build_nominatim():
    from geopy.geocoders import Nominatim
    return Nominatim(user_agent=USER_AGENT)


def geocode_institution(geocoder, institution: str, cache: dict) -> dict | None:
    """
    Geocode an institution name. Returns {"city": str, "lat": float, "lon": float}
    or None if not found. Checks cache first; writes result back to cache.
    """
    key = f"institution:{institution}"
    if key in cache:
        return cache[key]

    time.sleep(NOMINATIM_DELAY)
    try:
        loc = geocoder.geocode(institution, addressdetails=True, language="en")
    except Exception as e:
        print(f"  WARNING: geocode error for '{institution}': {e}", flush=True)
        cache[key] = None
        return None

    if not loc:
        cache[key] = None
        return None

    addr = loc.raw.get("address", {})
    city = next((addr[k] for k in CITY_KEYS if k in addr), None)
    result = {"city": city or "", "lat": loc.latitude, "lon": loc.longitude}
    cache[key] = result
    return result


def geocode_city_country(geocoder, city: str, country: str, cache: dict) -> dict | None:
    """
    Geocode a city + country string. Returns {"lat": float, "lon": float}
    or None. Checks cache first; writes result back to cache.
    """
    query = f"{city}, {country}".strip(", ")
    key = f"city:{query}"
    if key in cache:
        return cache[key]

    time.sleep(NOMINATIM_DELAY)
    try:
        loc = geocoder.geocode(query)
    except Exception as e:
        print(f"  WARNING: geocode error for '{query}': {e}", flush=True)
        cache[key] = None
        return None

    if not loc:
        cache[key] = None
        return None

    result = {"lat": loc.latitude, "lon": loc.longitude}
    cache[key] = result
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} teams from {CSV_PATH.name}")

    cache = load_cache()
    geocoder = _build_nominatim()

    # ------------------------------------------------------------------
    # Pass 1: institution → city + lat/lon (teams with no city)
    # ------------------------------------------------------------------
    no_city = df["city"].isna()
    institutions = df.loc[no_city, "institution"].dropna().unique()
    institutions = [i for i in institutions if i and not i.startswith("http")]
    # URL-only institution names (5 teams) can't be geocoded meaningfully
    print(f"\nPass 1: {no_city.sum()} teams with no city, {len(institutions)} unique institutions to geocode")

    cached_before = sum(1 for i in institutions if f"institution:{i}" in cache)
    print(f"  Already cached: {cached_before}, need to fetch: {len(institutions) - cached_before}")

    done = 0
    for inst in institutions:
        result = geocode_institution(geocoder, inst, cache)
        done += 1
        if done % 100 == 0:
            save_cache(cache)
            print(f"  {done}/{len(institutions)} institutions geocoded…", flush=True)

    save_cache(cache)

    # Apply Pass 1 results to the DataFrame
    filled_city = 0
    filled_coords_p1 = 0
    for inst in df.loc[no_city, "institution"].unique():
        if not inst or str(inst).startswith("http"):
            continue
        key = f"institution:{inst}"
        result = cache.get(key)
        if not result:
            continue
        mask = no_city & (df["institution"] == inst)
        if result.get("city"):
            df.loc[mask, "city"] = result["city"]
            filled_city += mask.sum()
        df.loc[mask, "lat"] = result["lat"]
        df.loc[mask, "lon"] = result["lon"]
        filled_coords_p1 += mask.sum()

    print(f"  Filled city for {filled_city} teams, lat/lon for {filled_coords_p1} teams")

    # ------------------------------------------------------------------
    # Pass 2: city + country → lat/lon (teams with city but no lat/lon)
    # ------------------------------------------------------------------
    needs_latlon = df["city"].notna() & df["lat"].isna()
    pairs = df.loc[needs_latlon, ["city", "country"]].drop_duplicates()
    print(f"\nPass 2: {needs_latlon.sum()} teams with city but no lat/lon, {len(pairs)} unique city/country pairs")

    cached_before_p2 = sum(
        1 for _, row in pairs.iterrows()
        if f"city:{row['city']}, {row['country']}".strip(", ") in cache
        or f"city:{row['city']}, {row['country']}" in cache
    )
    print(f"  Already cached: {cached_before_p2}, need to fetch: {len(pairs) - cached_before_p2}")

    done2 = 0
    for _, row in pairs.iterrows():
        geocode_city_country(geocoder, row["city"], row["country"], cache)
        done2 += 1
        if done2 % 100 == 0:
            save_cache(cache)
            print(f"  {done2}/{len(pairs)} city/country pairs geocoded…", flush=True)

    save_cache(cache)

    # Apply Pass 2 results
    filled_coords_p2 = 0
    for _, row in pairs.iterrows():
        city, country = row["city"], row["country"]
        query = f"{city}, {country}".strip(", ")
        key = f"city:{query}"
        result = cache.get(key)
        if not result:
            continue
        mask = needs_latlon & (df["city"] == city) & (df["country"] == country)
        df.loc[mask, "lat"] = result["lat"]
        df.loc[mask, "lon"] = result["lon"]
        filled_coords_p2 += mask.sum()

    print(f"  Filled lat/lon for {filled_coords_p2} teams")

    # ------------------------------------------------------------------
    # Summary and save
    # ------------------------------------------------------------------
    print(f"\n=== Final coverage ===")
    print(f"  city non-null:  {df['city'].notna().sum()}/{len(df)}")
    print(f"  lat  non-null:  {df['lat'].notna().sum()}/{len(df)}")
    print(f"  lon  non-null:  {df['lon'].notna().sum()}/{len(df)}")

    df.to_csv(CSV_PATH, index=False)
    print(f"\nSaved to {CSV_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
