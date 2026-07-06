"""
crossmodal.py — does a second, non-text signal agree with the semantic space?

The whole analysis rests on text: SPECTER2 reads titles and abstracts. A fair
worry is that we are only ever measuring the text, not the work. BioBrick parts
give us a way out. Every iGEM team registers physical DNA parts, and each part
carries a functional type (promoter, coding sequence, terminator, and so on).
Those type labels are not text the model read; they come from the registry. So
if two cities that build similar kinds of parts also look similar in the semantic
space, the space has recovered real structure that the parts confirm from outside
the text.

We test that with a Mantel test (Mantel 1967): the correlation between two
city-by-city distance tables, one from each modality, judged against a
permutation null because the pairwise distances are not independent.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def city_part_type_props(
    parts: pd.DataFrame,
    team_city: dict,
    min_parts: int = 10,
    type_col: str = "biobrick_part_type",
) -> pd.DataFrame:
    """
    Per-city distribution over BioBrick part types.

    Each part is registered by a team; team_city maps a team to its city. We count
    parts by city and type, keep cities with at least min_parts (below that the
    proportions are too noisy), and divide each row by its total so every city is a
    distribution over part types that sums to one.
    """
    p = parts.dropna(subset=["team_id", type_col]).copy()
    p["city_key"] = p["team_id"].map(team_city)
    p = p.dropna(subset=["city_key"])
    counts = p.groupby(["city_key", type_col]).size().unstack(fill_value=0)
    counts = counts[counts.sum(axis=1) >= min_parts]
    return counts.div(counts.sum(axis=1), axis=0)


def _cosine_distance(M: np.ndarray) -> np.ndarray:
    """1 - cosine similarity between every pair of rows."""
    n = np.linalg.norm(M, axis=1, keepdims=True)
    sim = (M @ M.T) / (n * n.T + 1e-12)
    return 1.0 - sim


def mantel_test(
    vecs_a: dict,
    vecs_b: dict,
    cities: list,
    n_perm: int = 2000,
    seed: int = 0,
) -> dict:
    """
    Mantel correlation between two per-city vector sets over the shared cities.

    Build a distance table from each side (cosine distance between city vectors),
    take the correlation of their upper triangles, then permute the city labels of
    one table n_perm times to get a null. Returns the observed correlation, the
    permutation p-value, and the null distribution (for plotting).
    """
    from scipy.stats import pearsonr

    A = np.vstack([vecs_a[c] for c in cities])
    B = np.vstack([vecs_b[c] for c in cities])
    Da, Db = _cosine_distance(A), _cosine_distance(B)
    iu = np.triu_indices(len(cities), 1)
    da, db = Da[iu], Db[iu]

    r, _ = pearsonr(da, db)
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for t in range(n_perm):
        perm = rng.permutation(len(cities))
        null[t] = pearsonr(da, Db[np.ix_(perm, perm)][iu])[0]

    p = (np.sum(null >= r) + 1) / (n_perm + 1)
    return {
        "r": float(r), "p_value": float(p), "n_cities": len(cities),
        "null_mean": float(null.mean()), "sem_dist": da, "part_dist": db, "null": null,
    }
