"""
scripts/16_regression_tables.py

Produces four LaTeX regression tables for the manuscript.

DV: city-level cluster_overlap = cosine(paper-cluster-freq-vec, project-cluster-freq-vec),
computed from all_artifacts.csv using the same MIN=8 threshold as notebook 01.
This matches the R^2=0.064 value reported in the manuscript.

Source: data/processed/all_artifacts.csv  (papers + projects, ~13k rows)
Controls: merged from data/processed/city_level.csv (n_papers, n_projects,
          cs_paper_share, cs_project_share, first_proj_year, proj_year_span)

Tables:
  tab_size_robust.tex   -- Table 1: progressive OLS, size-confound robustness
  tab_tercile.tex       -- Table 2: heterogeneity by corpus-size tercile
  tab_geo_robust.tex    -- Table 3: geographic robustness (sample splits)
  tab_cc_moderator.tex  -- Table 4: carbon-capture intensity as moderator

Note on SEs: only 19 countries in the dense sample, too few for reliable cluster SEs.
HC3 (heteroskedasticity-robust) is used throughout.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from pathlib import Path

ROOT   = Path(__file__).parent.parent
ART    = ROOT / "data" / "processed" / "all_artifacts.csv"
CITY   = ROOT / "data" / "processed" / "city_level.csv"
OUTDIR = ROOT / "manuscript"

OECD = {
    "AU","AT","BE","CA","CL","CO","CZ","DK","EE","FI","FR","DE","GR","HU",
    "IS","IE","IL","IT","JP","KR","LV","LT","LU","MX","NL","NZ","NO","PL",
    "PT","SK","SI","ES","SE","CH","TR","GB","US",
}

# -- Build DV: cluster_overlap (replicates notebook 01 section 8) -------------

art = pd.read_csv(ART, low_memory=False)
art["city_key"] = art["city"].astype(str).str.strip().str.lower()

clustered_valid = art[art["cluster_label"] >= 0].copy()
K_CLUSTERS = int(clustered_valid["cluster_label"].max()) + 1

def cluster_freq_vector(sub):
    """L2-normalised cluster-frequency vector, length K_CLUSTERS."""
    vec = np.zeros(K_CLUSTERS)
    for lab, cnt in sub["cluster_label"].value_counts().items():
        idx = int(lab)
        if 0 <= idx < K_CLUSTERS:
            vec[idx] = cnt
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else None

MIN_DOCS = 8   # minimum non-noise docs of each type per city (matches notebook 01)
rows = []
for ck, g in clustered_valid.groupby("city_key"):
    pg = g[g["type"] == "paper"]
    qg = g[g["type"] == "project"]
    if len(pg) < MIN_DOCS or len(qg) < MIN_DOCS:
        continue
    p = cluster_freq_vector(pg)
    q = cluster_freq_vector(qg)
    if p is None or q is None:
        continue
    rows.append({"city_key": ck,
                 "cluster_overlap": float(np.dot(p, q)),
                 "n_cl_papers": len(pg),
                 "n_cl_projects": len(qg)})

co_df = pd.DataFrame(rows)

# -- Merge city-level controls ------------------------------------------------

city = pd.read_csv(CITY)
df = co_df.merge(city, on="city_key", how="left")
df = df.dropna(subset=["cluster_overlap", "n_cl_papers", "n_cl_projects",
                        "cs_paper_share", "cs_project_share",
                        "first_proj_year", "proj_year_span"])

df["log_n_cl_papers"]   = np.log1p(df["n_cl_papers"])
df["log_n_cl_projects"] = np.log1p(df["n_cl_projects"])
df["log_papers"]        = np.log1p(df["n_papers"])
df["log_projects"]      = np.log1p(df["n_projects"])
df["log_total"]         = np.log1p(df["n_papers"] + df["n_projects"])
df["log_cl_papers2"]    = df["log_n_cl_papers"] ** 2
df["is_oecd"]           = df["country"].isin(OECD).astype(int)
df["tercile"]           = pd.qcut(df["log_total"], 3, labels=["Small", "Medium", "Large"])

# Centred variables for interaction table
df["log_p_c"]  = df["log_n_cl_papers"] - df["log_n_cl_papers"].mean()
df["cs_pp_c"]  = df["cs_paper_share"]  - df["cs_paper_share"].mean()
df["cs_prj_c"] = df["cs_project_share"] - df["cs_project_share"].mean()
df["int_pp"]   = df["log_p_c"] * df["cs_pp_c"]
df["int_prj"]  = df["log_p_c"] * df["cs_prj_c"]

print(f"Regression sample: {len(df)} cities, {df['country'].nunique()} countries")
print(f"cluster_overlap: mean={df['cluster_overlap'].mean():.4f} "
      f"sd={df['cluster_overlap'].std():.4f} "
      f"min={df['cluster_overlap'].min():.4f} max={df['cluster_overlap'].max():.4f}")
print(f"Tercile sizes: {df['tercile'].value_counts().sort_index().to_dict()}")

# -- Helpers ------------------------------------------------------------------

def _fmt(coef, se, pval):
    stars = "***" if pval < 0.001 else "**" if pval < 0.01 else \
            "*" if pval < 0.05 else r"$\dagger$" if pval < 0.10 else ""
    return f"{coef:.4f}{stars}", f"({se:.4f})"

def ols(formula, data):
    return smf.ols(formula, data=data).fit(cov_type="HC3")

def write_tex(path, lines):
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote {path}")

BASE = "cluster_overlap ~ log_n_cl_papers + log_n_cl_projects + proj_year_span + first_proj_year"


# =============================================================================
# TABLE 1  Size-confound robustness (progressive OLS)
# =============================================================================

specs1 = [
    ("(1)", "cluster_overlap ~ 1"),
    ("(2)", "cluster_overlap ~ log_n_cl_papers"),
    ("(3)", "cluster_overlap ~ log_n_cl_papers + log_n_cl_projects"),
    ("(4)", "cluster_overlap ~ log_n_cl_papers + log_n_cl_projects + proj_year_span"),
    ("(5)", BASE),
]

results1 = [(lbl, ols(f, df)) for lbl, f in specs1]

VARS1 = [
    ("log_n_cl_papers",   r"$\log(\text{clustered papers})$"),
    ("log_n_cl_projects", r"$\log(\text{clustered projects})$"),
    ("proj_year_span",    r"iGEM year span"),
    ("first_proj_year",   r"First iGEM year"),
]

lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    (r"\caption{Size-confound robustness. Dependent variable: city-level cluster overlap "
     r"(cosine between paper and project cluster-frequency vectors; sample restricted to "
     r"cities with $\geq 8$ non-noise documents of each type, following Section~8.1 of the "
     r"analysis). Specifications add controls sequentially. "
     r"HC3-robust standard errors in parentheses. "
     r"$N=60$ cities, 19 countries throughout. "
     r"$\dagger p<0.10$, $^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.}"),
    r"\label{tab:size_robust}",
    r"\begin{tabular}{lccccc}",
    r"\toprule",
    r"& (1) & (2) & (3) & (4) & (5) \\",
    r"\midrule",
]

for vkey, disp in VARS1:
    cs, ss = [], []
    for _, m in results1:
        if vkey in m.params.index:
            c, s = _fmt(m.params[vkey], m.bse[vkey], m.pvalues[vkey])
        else:
            c, s = "—", ""
        cs.append(c); ss.append(s)
    lines.append(f"{disp} & " + " & ".join(cs) + r" \\")
    lines.append(r"& " + " & ".join(ss) + r" \\[4pt]")

const_cs = []
for _, m in results1:
    if "Intercept" in m.params.index:
        c, _ = _fmt(m.params["Intercept"], m.bse["Intercept"], m.pvalues["Intercept"])
        const_cs.append(c)
    else:
        const_cs.append("—")

lines += [r"\midrule"]
lines.append(r"Constant & " + " & ".join(const_cs) + r" \\")
lines += [r"\midrule"]
lines.append(r"$N$ & "   + " & ".join(str(int(m.nobs)) for _, m in results1) + r" \\")
lines.append(r"$R^2$ & " + " & ".join(f"{m.rsquared:.3f}" for _, m in results1) + r" \\")
lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
write_tex(OUTDIR / "tab_size_robust.tex", lines)

print("\n=== TABLE 1 key numbers ===")
for lbl, m in results1[1:]:
    b = m.params.get("log_n_cl_papers", float("nan"))
    p = m.pvalues.get("log_n_cl_papers", float("nan"))
    print(f"  {lbl}: log_n_cl_papers b={b:.5f} p={p:.4f} R2={m.rsquared:.3f}")


# =============================================================================
# TABLE 2  Tercile heterogeneity + quadratic test
# =============================================================================

results2t = {}
for t in ["Small", "Medium", "Large"]:
    sub = df[df["tercile"] == t]
    results2t[t] = ols(BASE, sub)

m_full = ols(BASE, df)
m_quad = ols("cluster_overlap ~ log_n_cl_papers + log_cl_papers2 + log_n_cl_projects "
             "+ proj_year_span + first_proj_year", df)

all2 = [("Small",     results2t["Small"]),
        ("Medium",    results2t["Medium"]),
        ("Large",     results2t["Large"]),
        ("Full",      m_full),
        ("Quadratic", m_quad)]

ns = {t: df[df["tercile"] == t].shape[0] for t in ["Small", "Medium", "Large"]}

VARS2 = [
    ("log_n_cl_papers",   r"$\log(\text{cl.\ papers})$"),
    ("log_cl_papers2",    r"$\log(\text{cl.\ papers})^2$"),
    ("log_n_cl_projects", r"$\log(\text{cl.\ projects})$"),
    ("proj_year_span",    r"iGEM year span"),
    ("first_proj_year",   r"First iGEM year"),
]

lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    (rf"\caption{{Heterogeneity by corpus size. The sample is split by tercile of "
     rf"$\log(\text{{papers}} + \text{{projects}})$: "
     rf"Small ($n={ns['Small']}$), Medium ($n={ns['Medium']}$), Large ($n={ns['Large']}$). "
     r"Column~(4) pools all 60~cities. Column~(5) adds $\log(\text{cl.\ papers})^2$ to "
     r"test for a non-linear depth--alignment relationship. "
     r"HC3-robust standard errors. "
     r"$\dagger p<0.10$, $^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.}"),
    r"\label{tab:tercile}",
    r"\begin{tabular}{lccccc}",
    r"\toprule",
    r"& (1) Small & (2) Medium & (3) Large & (4) Full & (5) Quadratic \\",
    r"\midrule",
]

for vkey, disp in VARS2:
    cs, ss = [], []
    for _, m in all2:
        if vkey in m.params.index:
            c, s = _fmt(m.params[vkey], m.bse[vkey], m.pvalues[vkey])
        else:
            c, s = "—", ""
        cs.append(c); ss.append(s)
    lines.append(f"{disp} & " + " & ".join(cs) + r" \\")
    lines.append(r"& " + " & ".join(ss) + r" \\[4pt]")

lines += [r"\midrule"]
lines.append(r"$N$ & "   + " & ".join(str(int(m.nobs)) for _, m in all2) + r" \\")
lines.append(r"$R^2$ & " + " & ".join(f"{m.rsquared:.3f}" for _, m in all2) + r" \\")
lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
write_tex(OUTDIR / "tab_tercile.tex", lines)

print("\n=== TABLE 2 key numbers ===")
for lbl, m in all2:
    b = m.params.get("log_n_cl_papers", float("nan"))
    p = m.pvalues.get("log_n_cl_papers", float("nan"))
    print(f"  {lbl} (N={int(m.nobs)}): b={b:.5f} p={p:.4f} R2={m.rsquared:.3f}")


# =============================================================================
# TABLE 3  Geographic robustness (sample splits)
# =============================================================================

geo_specs = [
    ("All",        df),
    ("Drop US",    df[df["country"] != "US"]),
    ("Drop CN",    df[df["country"] != "CN"]),
    ("Drop US+CN", df[~df["country"].isin(["US", "CN"])]),
    ("OECD",       df[df["is_oecd"] == 1]),
    ("Non-OECD",   df[df["is_oecd"] == 0]),
]

results3 = []
for label, sub in geo_specs:
    if len(sub) < 10:
        continue
    m = ols(BASE, sub)
    results3.append((label, m, int(sub["country"].nunique()), int(len(sub))))

ncols3 = len(results3)
VARS3 = [
    ("log_n_cl_papers",   r"$\log(\text{cl.\ papers})$"),
    ("log_n_cl_projects", r"$\log(\text{cl.\ projects})$"),
]

lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\small",
    (r"\caption{Geographic robustness. Each column restricts the sample by country group. "
     r"OECD membership follows the 2024 member list. "
     r"All specifications include iGEM year span and first iGEM year as additional controls. "
     r"HC3-robust standard errors in parentheses. "
     r"$\dagger p<0.10$, $^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.}"),
    r"\label{tab:geo_robust}",
    r"\begin{tabular}{l" + "c" * ncols3 + "}",
    r"\toprule",
    "& " + " & ".join(r"\shortstack{" + lbl + "}" for lbl, *_ in results3) + r" \\",
    r"\midrule",
]

for vkey, disp in VARS3:
    cs, ss = [], []
    for _, m, *_ in results3:
        if vkey in m.params.index:
            c, s = _fmt(m.params[vkey], m.bse[vkey], m.pvalues[vkey])
        else:
            c, s = "—", ""
        cs.append(c); ss.append(s)
    lines.append(f"{disp} & " + " & ".join(cs) + r" \\")
    lines.append(r"& " + " & ".join(ss) + r" \\[4pt]")

lines += [r"\midrule"]
lines.append(r"Year controls & " + " & ".join("Yes" for _ in results3) + r" \\")
lines.append(r"$N$ & "       + " & ".join(str(n) for _, _, _, n in results3) + r" \\")
lines.append(r"$R^2$ & "     + " & ".join(f"{m.rsquared:.3f}" for _, m, *_ in results3) + r" \\")
lines.append(r"Countries & " + " & ".join(str(k) for _, _, k, _ in results3) + r" \\")
lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
write_tex(OUTDIR / "tab_geo_robust.tex", lines)

print("\n=== TABLE 3 key numbers ===")
for lbl, m, k, n in results3:
    b = m.params.get("log_n_cl_papers", float("nan"))
    p = m.pvalues.get("log_n_cl_papers", float("nan"))
    print(f"  {lbl} (N={n}, K={k}): b={b:.5f} p={p:.4f} R2={m.rsquared:.3f}")


# =============================================================================
# TABLE 4  Carbon-capture intensity as moderator
# =============================================================================

specs4 = [
    ("(1)", "cluster_overlap ~ log_p_c + cs_pp_c + proj_year_span + first_proj_year"),
    ("(2)", "cluster_overlap ~ log_p_c + cs_pp_c + int_pp + proj_year_span + first_proj_year"),
    ("(3)", "cluster_overlap ~ log_p_c + cs_prj_c + proj_year_span + first_proj_year"),
    ("(4)", "cluster_overlap ~ log_p_c + cs_prj_c + int_prj + proj_year_span + first_proj_year"),
    ("(5)", "cluster_overlap ~ log_p_c + cs_pp_c + cs_prj_c + int_pp + int_prj "
            "+ proj_year_span + first_proj_year"),
]

results4 = [(lbl, ols(f, df)) for lbl, f in specs4]

VARS4 = [
    ("log_p_c",         r"$\log(\text{cl.\ papers})$ (centred)"),
    ("cs_pp_c",         r"CC paper share (centred)"),
    ("int_pp",          r"$\quad \times$ CC paper share"),
    ("cs_prj_c",        r"CC project share (centred)"),
    ("int_prj",         r"$\quad \times$ CC project share"),
    ("proj_year_span",  r"iGEM year span"),
    ("first_proj_year", r"First iGEM year"),
]

lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    (r"\caption{Carbon-capture intensity as a moderator. Dependent variable: city-level "
     r"cluster overlap. Carbon-capture share measures the fraction of a city's clustered "
     r"papers (or projects) falling in the carbon-capture topic clusters. "
     r"All continuous regressors are mean-centred; interaction rows show "
     r"$\log(\text{cl.\ papers}) \times \text{CC share}$. "
     r"HC3-robust standard errors. "
     r"$\dagger p<0.10$, $^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.}"),
    r"\label{tab:cc_moderator}",
    r"\begin{tabular}{lccccc}",
    r"\toprule",
    r"& (1) & (2) & (3) & (4) & (5) \\",
    r"\midrule",
]

for vkey, disp in VARS4:
    cs, ss = [], []
    for _, m in results4:
        if vkey in m.params.index:
            c, s = _fmt(m.params[vkey], m.bse[vkey], m.pvalues[vkey])
        else:
            c, s = "—", ""
        cs.append(c); ss.append(s)
    lines.append(f"{disp} & " + " & ".join(cs) + r" \\")
    lines.append(r"& " + " & ".join(ss) + r" \\[4pt]")

lines += [r"\midrule"]
lines.append(r"$N$ & "   + " & ".join(str(int(m.nobs)) for _, m in results4) + r" \\")
lines.append(r"$R^2$ & " + " & ".join(f"{m.rsquared:.3f}" for _, m in results4) + r" \\")
lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
write_tex(OUTDIR / "tab_cc_moderator.tex", lines)

print("\n=== TABLE 4 key numbers ===")
for lbl, m in results4:
    for vkey in ["int_pp", "int_prj"]:
        if vkey in m.params:
            print(f"  {lbl} {vkey}: b={m.params[vkey]:.5f} p={m.pvalues[vkey]:.4f}")

print("\nDone.")
