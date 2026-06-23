"""
geocode.py — convert city/country names to latitude/longitude coordinates.

We use Nominatim (the OpenStreetMap geocoder) by default because it is free
and requires no API key. For higher throughput or reliability, OpenCage
is an alternative (requires API key in .env).

Caching:
  Geocoding is slow and has rate limits. We cache all results in a JSON
  file so that repeated runs skip already-geocoded locations.
  Cache key = "city, country" → {"lat": float, "lon": float}

Rate limiting:
  Nominatim requires at most 1 request per second for free use.
  We enforce this automatically.

Reference: OpenStreetMap Nominatim usage policy:
  https://operations.osmfoundation.org/policies/nominatim/
"""

from __future__ import annotations
import json
import logging
import time
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Nominatim rate limit: 1 request per second
NOMINATIM_DELAY = 1.1

# Per-request network timeout (seconds). geopy's default is only 1s, which
# causes spurious timeouts on Nominatim under load; those would otherwise be
# cached as permanent "not found" misses. 10s is comfortably above normal
# Nominatim latency.
GEOCODE_TIMEOUT = 10

# Sentinel returned by _geocode_one when a lookup fails for a *transient*
# reason (network timeout, connection error) rather than a genuine "no such
# place". The caller must NOT cache this — the location should be retried on a
# later run instead of being recorded as a permanent miss.
_GEOCODE_ERROR = object()


def load_geocoding_cache(cache_file: str | Path) -> dict:
    """Load the geocoding cache from disk, or return an empty dict."""
    cache_file = Path(cache_file)
    if cache_file.exists():
        with open(cache_file, "r") as f:
            return json.load(f)
    return {}


def save_geocoding_cache(cache: dict, cache_file: str | Path):
    """Save the geocoding cache to disk."""
    cache_file = Path(cache_file)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w") as f:
        json.dump(cache, f, indent=2)


def geocode_dataframe(
    df: pd.DataFrame,
    cache_file: str | Path,
    city_col: str = "city",
    country_col: str = "country",
    provider: str = "nominatim",
    user_agent: str = "synbio-patents-papers-parts",
) -> pd.DataFrame:
    """
    Add lat/lon columns to df by geocoding city + country pairs.

    Rows where city and country are both missing are skipped.
    Results are cached to avoid re-geocoding on subsequent runs.

    Parameters
    ----------
    df : DataFrame with city and country columns
    cache_file : path to JSON cache file
    city_col, country_col : column names in df
    provider : "nominatim" (default, free) or "opencage" (requires API key)
    user_agent : identifier string for Nominatim (required by usage policy)

    Returns
    -------
    df with "lat" and "lon" columns filled in where possible
    """
    cache = load_geocoding_cache(cache_file)
    geocoder = _build_geocoder(provider, user_agent)

    df = df.copy()
    if "lat" not in df.columns:
        df["lat"] = None
    if "lon" not in df.columns:
        df["lon"] = None

    # Collect unique location strings to avoid redundant lookups
    locations = df[[city_col, country_col]].drop_duplicates()

    for _, loc_row in locations.iterrows():
        city = loc_row.get(city_col) or ""
        country = loc_row.get(country_col) or ""
        if not city and not country:
            continue

        key = f"{city}, {country}".strip(", ")
        if key in cache:
            result = cache[key]
        else:
            result = _geocode_one(geocoder, key, provider)
            if result is not _GEOCODE_ERROR:
                # Cache successes and genuine misses (None) so we don't retry
                # them; transient errors are left uncached for a later retry.
                cache[key] = result
                save_geocoding_cache(cache, cache_file)

        if result and result is not _GEOCODE_ERROR:
            mask = (
                (df[city_col].fillna("") == city) &
                (df[country_col].fillna("") == country)
            )
            df.loc[mask, "lat"] = result["lat"]
            df.loc[mask, "lon"] = result["lon"]

    return df


def _geocode_one(geocoder, location_string: str, provider: str):
    """
    Geocode a single location string.

    Returns:
      {"lat": float, "lon": float}  on success,
      None                          if the place genuinely could not be found,
      _GEOCODE_ERROR                if the lookup failed for a transient reason
                                    (timeout / network) and should be retried.
    """
    from geopy.exc import GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError

    try:
        if provider == "nominatim":
            time.sleep(NOMINATIM_DELAY)  # respect rate limit
        location = geocoder.geocode(location_string)
        if location:
            logger.debug(f"Geocoded '{location_string}' → ({location.latitude}, {location.longitude})")
            return {"lat": location.latitude, "lon": location.longitude}
        else:
            logger.warning(f"Could not geocode '{location_string}'")
            return None
    except (GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError) as e:
        # Transient: don't cache, let a later run retry this location.
        logger.warning(f"Transient geocoding error for '{location_string}': {e}")
        return _GEOCODE_ERROR
    except Exception as e:
        logger.error(f"Geocoding error for '{location_string}': {e}")
        return None


def _build_geocoder(provider: str, user_agent: str):
    """Build a geopy geocoder for the given provider."""
    import os
    from geopy.geocoders import Nominatim, OpenCage

    if provider == "nominatim":
        return Nominatim(user_agent=user_agent, timeout=GEOCODE_TIMEOUT)
    elif provider == "opencage":
        api_key = os.getenv("OPENCAGE_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "OPENCAGE_API_KEY is not set. Add it to your .env file, "
                "or set provider='nominatim' to use the free geocoder."
            )
        return OpenCage(api_key=api_key, timeout=GEOCODE_TIMEOUT)
    else:
        raise ValueError(f"Unknown geocoding provider: '{provider}'. Choose 'nominatim' or 'opencage'.")
