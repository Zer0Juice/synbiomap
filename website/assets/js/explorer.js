/**
 * explorer.js — City Panel Explorer
 *
 * Two-panel interface:
 *   Left  — searchable list of cities, sorted by total artifact count
 *   Right — UMAP (city highlighted) + stat cards + artifact list
 *           Clicking an artifact shows its abstract, city, and a link
 *
 * Data files (in website/assets/data/):
 *   artifacts.json   — [{id, type, title, text, year, city, country,
 *                        case_study_flag, cluster_label}]
 *   projections.json — [{id, x, y, cluster}]
 *
 * Static-hosting compatible: all data is precomputed; no server needed.
 *
 * Color palette: Solarized Light (Ethan Schoonover, 2011)
 */

(function () {

  // ─── Solarized palette ───────────────────────────────────────────────────
  const SOL = {
    base02:  "#073642",
    base01:  "#586e75",
    base00:  "#657b83",
    base1:   "#93a1a1",
    base2:   "#eee8d5",
    base3:   "#fdf6e3",
    yellow:  "#b58900",
    orange:  "#cb4b16",
    red:     "#dc322f",
    magenta: "#d33682",
    blue:    "#268bd2",
    cyan:    "#2aa198",
    green:   "#859900",
  };

  const TYPE_COLOR = {
    paper:   SOL.blue,
    patent:  SOL.orange,
    project: SOL.green,
    part:    SOL.magenta,
  };

  const TYPE_LABEL = {
    paper: "Paper", patent: "Patent", project: "iGEM Project", part: "iGEM Part",
  };

  const DIM_COLOR = "#c8cfd4";

  // ─── Bootstrap ───────────────────────────────────────────────────────────
  const root = document.getElementById("city-explorer");
  if (!root) return;

  root.innerHTML = `<p style="padding:2em;color:${SOL.base1};">Loading data…</p>`;

  // abstracts.json is large (~16 MB uncompressed). Load it once lazily —
  // only when the user first clicks an artifact — then cache the result.
  let abstractsCache = null;
  let abstractsLoading = null;

  function getAbstracts() {
    if (abstractsCache) return Promise.resolve(abstractsCache);
    if (abstractsLoading) return abstractsLoading;
    abstractsLoading = fetch("assets/data/abstracts.json")
      .then(r => r.json())
      .then(data => { abstractsCache = data; return data; });
    return abstractsLoading;
  }

  Promise.all([
    fetch("assets/data/artifacts.json").then(r => r.json()),
    fetch("assets/data/projections.json").then(r => r.json()),
  ])
    .then(([artifacts, projections]) => init(artifacts, projections))
    .catch(err => {
      root.innerHTML =
        `<p style="padding:2em;color:#c00;">Could not load data files. ` +
        `Run the pipeline first to generate <code>artifacts.json</code> and ` +
        `<code>projections.json</code>.</p>`;
      console.error("Explorer load error:", err);
    });


  // ─── Main init ───────────────────────────────────────────────────────────
  function init(artifacts, projections) {
    const projMap = {};
    for (const p of projections) projMap[p.id] = p;

    const joined = artifacts
      .filter(a => projMap[a.id])
      .map(a => ({ ...a, x: projMap[a.id].x, y: projMap[a.id].y }));

    const cityIndex = buildCityIndex(joined);
    const citiesSorted = Object.values(cityIndex)
      .sort((a, b) => b.artifacts.length - a.artifacts.length);

    root.innerHTML = buildShell();

    const searchInput = document.getElementById("exp-city-search");
    const cityList    = document.getElementById("exp-city-list");
    const detailPanel = document.getElementById("exp-detail");
    const plotDiv     = document.getElementById("exp-umap");

    renderUMAP(plotDiv, joined, null);
    renderCityList(cityList, citiesSorted, null, onCitySelect);

    searchInput.addEventListener("input", () => {
      const q = searchInput.value.trim().toLowerCase();
      const filtered = q
        ? citiesSorted.filter(c => c.label.toLowerCase().includes(q))
        : citiesSorted;
      renderCityList(cityList, filtered, state.cityKey, onCitySelect);
    });

    // Shared mutable state
    const state = { cityKey: null, artifactId: null };

    function onCitySelect(cityKey) {
      state.cityKey    = cityKey;
      state.artifactId = null;
      const city = cityIndex[cityKey];

      const q = searchInput.value.trim().toLowerCase();
      const filtered = q
        ? citiesSorted.filter(c => c.label.toLowerCase().includes(q))
        : citiesSorted;
      renderCityList(cityList, filtered, cityKey, onCitySelect);
      updateUMAP(plotDiv, joined, city);
      renderDetail(detailPanel, city, null, null, onArtifactSelect);
    }

    function onArtifactSelect(artifactId) {
      if (state.artifactId === artifactId) {
        state.artifactId = null;
        renderDetail(detailPanel, cityIndex[state.cityKey], null, null, onArtifactSelect);
        return;
      }
      state.artifactId = artifactId;
      const city = cityIndex[state.cityKey];

      // Show card immediately without abstract while abstracts.json loads
      renderDetail(detailPanel, city, artifactId, null, onArtifactSelect);

      getAbstracts().then(abstracts => {
        // Only update if the user hasn't clicked away to something else
        if (state.artifactId === artifactId) {
          renderDetail(detailPanel, city, artifactId, abstracts, onArtifactSelect);
        }
      });
    }
  }


  // ─── City index ──────────────────────────────────────────────────────────
  function buildCityIndex(joined) {
    const index = {};
    for (const a of joined) {
      const city    = (a.city    || "Unknown").trim();
      const country = (a.country || "").trim();
      const key     = `${city}||${country}`;
      if (!index[key]) index[key] = { key, label: city, country, artifacts: [] };
      index[key].artifacts.push(a);
    }
    return index;
  }


  // ─── HTML shell ──────────────────────────────────────────────────────────
  function buildShell() {
    return `
      <div id="exp-shell" style="
        display:flex; gap:0; height:720px;
        border:1px solid ${SOL.base2}; border-radius:6px;
        overflow:hidden; font-family:inherit; background:${SOL.base3};
      ">
        <!-- Left: city selector -->
        <div style="
          width:240px; min-width:200px; display:flex; flex-direction:column;
          border-right:1px solid ${SOL.base2}; background:${SOL.base3};
        ">
          <div style="padding:12px 12px 8px; border-bottom:1px solid ${SOL.base2};">
            <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.08em;
                        text-transform:uppercase;color:${SOL.base1};margin-bottom:6px;">
              Cities
            </div>
            <input id="exp-city-search" type="search" placeholder="Search cities…"
              style="
                width:100%;box-sizing:border-box;padding:6px 8px;
                border:1px solid ${SOL.base2};border-radius:4px;
                background:${SOL.base3};color:${SOL.base02};
                font-size:0.82rem;outline:none;
              ">
          </div>
          <div id="exp-city-list" style="flex:1;overflow-y:auto;padding:4px 0;"></div>
        </div>

        <!-- Right: UMAP + detail -->
        <div style="flex:1;display:flex;flex-direction:column;min-width:0;">
          <div id="exp-umap" style="flex:0 0 340px;min-height:0;"></div>
          <div id="exp-detail" style="
            flex:1;overflow-y:auto;
            border-top:1px solid ${SOL.base2};
          ">
            <div style="padding:2em;color:${SOL.base1};font-size:0.9rem;">
              Select a city on the left to see its activity.
            </div>
          </div>
        </div>
      </div>`;
  }


  // ─── City list ───────────────────────────────────────────────────────────
  function renderCityList(container, cities, activeKey, onSelect) {
    if (!cities.length) {
      container.innerHTML =
        `<div style="padding:12px;font-size:0.82rem;color:${SOL.base1};">No cities found.</div>`;
      return;
    }

    container.innerHTML = cities.slice(0, 300).map(c => {
      const isActive = c.key === activeKey;
      const bg = isActive ? SOL.base2 : "transparent";
      const fg = isActive ? SOL.base02 : SOL.base00;
      return `<div class="exp-city-item" data-key="${esc(c.key)}"
        style="
          display:flex;justify-content:space-between;align-items:center;
          padding:7px 12px;cursor:pointer;
          background:${bg};color:${fg};
          font-size:0.82rem;border-bottom:1px solid transparent;
        "
        onmouseenter="this.style.background='${SOL.base2}'"
        onmouseleave="this.style.background='${isActive ? SOL.base2 : "transparent"}'"
      >
        <span style="flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
          ${esc(c.label)}
          <span style="font-size:0.72rem;color:${SOL.base1};margin-left:3px;">${esc(c.country)}</span>
        </span>
        <span style="
          margin-left:8px;padding:1px 6px;
          background:${isActive ? SOL.base3 : SOL.base2};
          color:${SOL.base01};border-radius:10px;
          font-size:0.72rem;font-weight:600;
        ">${c.artifacts.length}</span>
      </div>`;
    }).join("");

    container.querySelectorAll(".exp-city-item").forEach(el => {
      el.addEventListener("click", () => onSelect(el.dataset.key));
    });
  }


  // ─── UMAP ────────────────────────────────────────────────────────────────
  function renderUMAP(div, joined, selectedCity) {
    if (typeof Plotly === "undefined") return;
    Plotly.newPlot(div, buildUMAPTraces(joined, selectedCity), umapLayout(),
      { responsive: true, displayModeBar: false });
  }

  function updateUMAP(div, joined, selectedCity) {
    if (typeof Plotly === "undefined") return;
    Plotly.react(div, buildUMAPTraces(joined, selectedCity), umapLayout());
  }

  function buildUMAPTraces(joined, selectedCity) {
    const selectedIds = selectedCity
      ? new Set(selectedCity.artifacts.map(a => a.id))
      : null;

    const bgX = [], bgY = [];
    for (const a of joined) {
      if (!selectedIds || !selectedIds.has(a.id)) { bgX.push(a.x); bgY.push(a.y); }
    }

    const traces = [{
      x: bgX, y: bgY, mode: "markers", type: "scatter",
      name: "Other", showlegend: false,
      marker: { color: DIM_COLOR, size: selectedIds ? 3 : 4, opacity: 0.4 },
      hoverinfo: "skip",
    }];

    if (selectedIds) {
      const byType = {};
      for (const a of selectedCity.artifacts) {
        if (!byType[a.type]) byType[a.type] = { x: [], y: [], text: [] };
        byType[a.type].x.push(a.x);
        byType[a.type].y.push(a.y);
        byType[a.type].text.push(`${a.title || a.id} (${a.year || "?"})`);
      }
      for (const [type, pts] of Object.entries(byType)) {
        traces.push({
          x: pts.x, y: pts.y, mode: "markers", type: "scatter",
          name: TYPE_LABEL[type] || type,
          marker: { color: TYPE_COLOR[type] || SOL.cyan, size: 7, opacity: 0.9,
                    line: { width: 0.5, color: SOL.base3 } },
          text: pts.text,
          hovertemplate: "%{text}<extra></extra>",
        });
      }
    }
    return traces;
  }

  function umapLayout() {
    return {
      paper_bgcolor: SOL.base3, plot_bgcolor: SOL.base3,
      font: { color: SOL.base01, size: 11 },
      xaxis: { title: "UMAP 1", showgrid: false, zeroline: false, color: SOL.base1 },
      yaxis: { title: "UMAP 2", showgrid: false, zeroline: false, color: SOL.base1 },
      legend: { bgcolor: SOL.base2, bordercolor: "#d4cbb7", borderwidth: 1,
                font: { size: 11 }, x: 1, xanchor: "right", y: 1 },
      margin: { t: 12, l: 50, r: 10, b: 40 },
    };
  }


  // ─── Detail panel ────────────────────────────────────────────────────────
  // abstracts: the full {id: abstractText} map, or null if not yet loaded.
  function renderDetail(container, city, selectedId, abstracts, onArtifactSelect) {
    const arts     = city.artifacts;
    const counts   = countByType(arts);
    const ccCount  = arts.filter(a => a.case_study_flag).length;

    const statCards = [
      ["Papers",         counts.paper   || 0, SOL.blue],
      ["Patents",        counts.patent  || 0, SOL.orange],
      ["iGEM Projects",  counts.project || 0, SOL.green],
      ["Carbon capture", ccCount,             SOL.red],
    ].map(([label, val, color]) => `
      <div style="
        flex:1;min-width:70px;padding:10px 12px;
        background:${SOL.base3};border:1px solid ${SOL.base2};
        border-radius:5px;text-align:center;
      ">
        <div style="font-size:1.4rem;font-weight:700;color:${color};">${val}</div>
        <div style="font-size:0.7rem;color:${SOL.base1};margin-top:2px;">${label}</div>
      </div>`).join("");

    // Artifact detail card (shown when an artifact is selected)
    let detailCard = "";
    if (selectedId) {
      const a = arts.find(x => x.id === selectedId);
      if (a) detailCard = buildArtifactCard(a, abstracts);
    }

    // Artifact list — most recent first, up to 100
    const sorted = [...arts].sort((a, b) => (b.year || 0) - (a.year || 0));
    const rows = sorted.slice(0, 100).map(a => {
      const isSelected = a.id === selectedId;
      const dot = `<span style="
        display:inline-block;width:8px;height:8px;border-radius:50%;
        background:${TYPE_COLOR[a.type] || SOL.cyan};
        margin-right:6px;flex-shrink:0;margin-top:3px;
      "></span>`;
      const cc = a.case_study_flag
        ? `<span style="font-size:0.65rem;background:${SOL.red};color:#fff;
                        padding:1px 4px;border-radius:3px;margin-left:4px;
                        white-space:nowrap;">CC</span>`
        : "";
      return `<div class="exp-artifact-row" data-id="${esc(a.id)}"
        style="
          display:flex;align-items:flex-start;
          padding:7px 16px;cursor:pointer;
          border-bottom:1px solid ${SOL.base2};
          font-size:0.8rem;
          background:${isSelected ? SOL.base2 : "transparent"};
          color:${SOL.base02};
        "
        onmouseenter="if(this.dataset.id!=='${esc(selectedId || "")}')this.style.background='${SOL.base2}'"
        onmouseleave="if(this.dataset.id!=='${esc(selectedId || "")}')this.style.background='transparent'"
      >
        ${dot}
        <span style="flex:1;min-width:0;">
          <strong>${esc(a.title || a.id)}</strong>${cc}
        </span>
        <span style="margin-left:8px;color:${SOL.base1};font-size:0.75rem;
                     white-space:nowrap;flex-shrink:0;">${a.year || "?"}</span>
      </div>`;
    }).join("");

    const moreNote = arts.length > 100
      ? `<div style="padding:8px 16px;font-size:0.75rem;color:${SOL.base1};">
           Showing 100 of ${arts.length} artifacts.</div>`
      : "";

    container.innerHTML = `
      <div style="padding:14px 16px 8px;">
        <div style="font-size:1.05rem;font-weight:700;color:${SOL.base02};">
          ${esc(city.label)}
          <span style="font-size:0.8rem;font-weight:400;color:${SOL.base1};margin-left:5px;">${esc(city.country)}</span>
        </div>
        <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">${statCards}</div>
      </div>
      ${detailCard}
      <div style="padding:6px 16px 4px;font-size:0.7rem;font-weight:600;
                  letter-spacing:0.07em;text-transform:uppercase;color:${SOL.base1};">
        Artifacts — click to expand
      </div>
      ${rows}
      ${moreNote}`;

    container.querySelectorAll(".exp-artifact-row").forEach(el => {
      el.addEventListener("click", () => onArtifactSelect(el.dataset.id));
    });
  }


  // ─── Artifact detail card ─────────────────────────────────────────────────
  // abstracts: {id: abstractText} map (null while loading)
  function buildArtifactCard(a, abstracts) {
    const color     = TYPE_COLOR[a.type] || SOL.cyan;
    const typeLabel = TYPE_LABEL[a.type] || a.type;

    // abstracts.json is loaded lazily; show a placeholder until it arrives.
    const abstract = abstracts
      ? (abstracts[a.id] || "")
      : null;  // null = still loading

    // Build link
    const link = buildLink(a);

    const cityLine = [a.city, a.country].filter(Boolean).join(", ");

    const ccBadge = a.case_study_flag
      ? `<span style="font-size:0.68rem;background:${SOL.red};color:#fff;
                      padding:1px 6px;border-radius:3px;margin-left:6px;">
           Carbon capture
         </span>`
      : "";

    const linkBtn = link
      ? `<a href="${esc(link.url)}" target="_blank" rel="noopener"
           style="
             display:inline-block;margin-top:10px;
             padding:5px 12px;border-radius:4px;
             background:${color};color:#fff;
             font-size:0.78rem;font-weight:600;
             text-decoration:none;
           ">${esc(link.label)}</a>`
      : "";

    return `
      <div style="
        margin:0 16px 4px;padding:12px 14px;
        background:${SOL.base2};border-radius:5px;
        border-left:3px solid ${color};
      ">
        <div style="display:flex;align-items:baseline;flex-wrap:wrap;gap:4px;margin-bottom:8px;">
          <span style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                       letter-spacing:0.07em;color:${color};">${esc(typeLabel)}</span>
          ${ccBadge}
          <span style="margin-left:auto;font-size:0.75rem;color:${SOL.base1};">${a.year || ""}</span>
        </div>
        <div style="font-size:0.85rem;font-weight:600;color:${SOL.base02};margin-bottom:4px;">
          ${esc(a.title || a.id)}
        </div>
        ${cityLine ? `<div style="font-size:0.75rem;color:${SOL.base1};margin-bottom:8px;">
          📍 ${esc(cityLine)}</div>` : ""}
        ${abstract === null
          ? `<div style="font-size:0.75rem;color:${SOL.base1};border-top:1px solid #d4cbb7;padding-top:8px;">
               Loading abstract…</div>`
          : abstract
            ? `<div style="
                font-size:0.78rem;color:${SOL.base01};line-height:1.55;
                max-height:120px;overflow-y:auto;
                border-top:1px solid #d4cbb7;padding-top:8px;
              ">${esc(abstract)}</div>`
            : ""}
        ${linkBtn}
      </div>`;
  }


  // ─── Link generation ─────────────────────────────────────────────────────
  /**
   * Derives the canonical external link for an artifact.
   *
   * Papers:   id is an OpenAlex URL → link directly to OpenAlex, which
   *           shows the DOI and links to the publisher page.
   * Patents:  id is a Lens.org lens_id → link to lens.org/{id}.
   * Projects: id is "igem_{team}_{year}" → iGEM wiki URL.
   *           Format: https://{year}.igem.org/Team:{team}
   */
  function buildLink(a) {
    if (a.type === "paper" && a.id && a.id.startsWith("https://")) {
      return { url: a.id, label: "View on OpenAlex →" };
    }

    if (a.type === "patent" && a.id && !a.id.startsWith("http")) {
      // Lens IDs look like "000-123-456-789-X"
      return { url: `https://lens.org/${encodeURIComponent(a.id)}`, label: "View on Lens.org →" };
    }

    if ((a.type === "project" || a.type === "part") && a.id && a.id.startsWith("igem_")) {
      const url = igem_wiki_url(a.id);
      if (url) return { url, label: "iGEM Wiki →" };
    }

    return null;
  }

  /**
   * Converts "igem_{team}_{year}" to "https://{year}.igem.org/Team:{team}".
   * The year is always the last segment (4 digits). Everything between
   * "igem_" and "_{year}" is the team name.
   */
  function igem_wiki_url(id) {
    const withoutPrefix = id.slice("igem_".length);  // "Aberdeen_Scotland_2009"
    const m = withoutPrefix.match(/^(.+)_(\d{4})$/);
    if (!m) return null;
    const team = m[1];   // "Aberdeen_Scotland"
    const year = m[2];   // "2009"
    return `https://${year}.igem.org/Team:${encodeURIComponent(team)}`;
  }


  // ─── Helpers ─────────────────────────────────────────────────────────────
  function countByType(artifacts) {
    const counts = {};
    for (const a of artifacts) counts[a.type] = (counts[a.type] || 0) + 1;
    return counts;
  }

  function esc(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

})();
