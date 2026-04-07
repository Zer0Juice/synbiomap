/**
 * explorer.js — City Panel Explorer
 *
 * Two-panel interface:
 *   Left  — searchable list of cities, sorted by total artifact count
 *   Right — city detail: stat cards, UMAP with city highlighted, artifact list
 *
 * Data files (in website/assets/data/):
 *   artifacts.json   — [{id, type, title, year, city, country, case_study_flag, cluster_label, ...}]
 *   projections.json — [{id, x, y, cluster}]
 *
 * Static-hosting compatible: all data is precomputed; no server needed.
 *
 * Color palette: Solarized Light (Ethan Schoonover, 2011)
 */

(function () {

  // ─── Solarized palette ───────────────────────────────────────────────────
  const SOL = {
    base03:  "#002b36",
    base02:  "#073642",
    base01:  "#586e75",
    base00:  "#657b83",
    base0:   "#839496",
    base1:   "#93a1a1",
    base2:   "#eee8d5",
    base3:   "#fdf6e3",
    yellow:  "#b58900",
    orange:  "#cb4b16",
    red:     "#dc322f",
    magenta: "#d33682",
    violet:  "#6c71c4",
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

  const DIM_COLOR = "#c8cfd4";  // muted grey for unselected points

  // ─── Bootstrap ───────────────────────────────────────────────────────────
  const root = document.getElementById("city-explorer");
  if (!root) return;

  root.innerHTML = `<p style="padding:2em;color:${SOL.base1};">Loading data…</p>`;

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

    // Join projections onto artifacts
    const projMap = {};
    for (const p of projections) projMap[p.id] = p;

    const joined = artifacts
      .filter(a => projMap[a.id])
      .map(a => ({ ...a, x: projMap[a.id].x, y: projMap[a.id].y }));

    // Build city index: city_key → { label, country, artifacts[] }
    const cityIndex = buildCityIndex(joined);
    const citiesSorted = Object.values(cityIndex)
      .sort((a, b) => b.artifacts.length - a.artifacts.length);

    // Render shell
    root.innerHTML = buildShell();

    const searchInput  = document.getElementById("exp-city-search");
    const cityList     = document.getElementById("exp-city-list");
    const detailPanel  = document.getElementById("exp-detail");
    const plotDiv      = document.getElementById("exp-umap");

    // Pre-render the UMAP once (city selection just updates traces, no full re-render)
    renderUMAP(plotDiv, joined, null);

    // Render full city list
    renderCityList(cityList, citiesSorted, null, onCitySelect);

    // Search filter
    searchInput.addEventListener("input", () => {
      const q = searchInput.value.trim().toLowerCase();
      const filtered = q
        ? citiesSorted.filter(c => c.label.toLowerCase().includes(q))
        : citiesSorted;
      renderCityList(cityList, filtered, currentCity, onCitySelect);
    });

    let currentCity = null;

    function onCitySelect(cityKey) {
      currentCity = cityKey;
      const city = cityIndex[cityKey];

      // Re-render list to show active state
      const q = searchInput.value.trim().toLowerCase();
      const filtered = q
        ? citiesSorted.filter(c => c.label.toLowerCase().includes(q))
        : citiesSorted;
      renderCityList(cityList, filtered, cityKey, onCitySelect);

      // Update UMAP highlight
      updateUMAP(plotDiv, joined, city);

      // Render detail cards + artifact list
      renderDetail(detailPanel, city);
    }
  }


  // ─── City index ──────────────────────────────────────────────────────────
  function buildCityIndex(joined) {
    const index = {};
    for (const a of joined) {
      const city    = (a.city    || "Unknown").trim();
      const country = (a.country || "").trim();
      const key     = `${city}||${country}`;
      if (!index[key]) {
        index[key] = { key, label: city, country, artifacts: [] };
      }
      index[key].artifacts.push(a);
    }
    return index;
  }


  // ─── HTML shell ──────────────────────────────────────────────────────────
  function buildShell() {
    return `
      <div id="exp-shell" style="
        display: flex;
        gap: 0;
        height: 720px;
        border: 1px solid ${SOL.base2};
        border-radius: 6px;
        overflow: hidden;
        font-family: inherit;
        background: ${SOL.base3};
      ">
        <!-- Left: city selector -->
        <div style="
          width: 240px;
          min-width: 200px;
          display: flex;
          flex-direction: column;
          border-right: 1px solid ${SOL.base2};
          background: ${SOL.base3};
        ">
          <div style="padding:12px 12px 8px; border-bottom:1px solid ${SOL.base2};">
            <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.08em;
                        text-transform:uppercase;color:${SOL.base1};margin-bottom:6px;">
              Cities
            </div>
            <input id="exp-city-search" type="search" placeholder="Search cities…"
              style="
                width: 100%; box-sizing: border-box;
                padding: 6px 8px;
                border: 1px solid ${SOL.base2};
                border-radius: 4px;
                background: ${SOL.base3};
                color: ${SOL.base02};
                font-size: 0.82rem;
                outline: none;
              ">
          </div>
          <div id="exp-city-list" style="
            flex: 1; overflow-y: auto;
            padding: 4px 0;
          "></div>
        </div>

        <!-- Right: detail -->
        <div id="exp-detail-wrap" style="flex:1; display:flex; flex-direction:column; min-width:0;">
          <!-- UMAP always visible -->
          <div id="exp-umap" style="flex:0 0 380px; min-height:0;"></div>
          <!-- City detail below UMAP -->
          <div id="exp-detail" style="
            flex:1; overflow-y:auto;
            border-top:1px solid ${SOL.base2};
            padding:0;
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
    if (cities.length === 0) {
      container.innerHTML = `<div style="padding:12px;font-size:0.82rem;color:${SOL.base1};">No cities found.</div>`;
      return;
    }

    container.innerHTML = cities.slice(0, 300).map(c => {
      const total   = c.artifacts.length;
      const isActive = c.key === activeKey;
      const bg = isActive ? SOL.base2 : "transparent";
      const fg = isActive ? SOL.base02 : SOL.base00;

      return `<div
        class="exp-city-item"
        data-key="${esc(c.key)}"
        style="
          display:flex; justify-content:space-between; align-items:center;
          padding:7px 12px; cursor:pointer;
          background:${bg}; color:${fg};
          font-size:0.82rem; border-bottom:1px solid ${isActive ? SOL.base2 : "transparent"};
          transition:background 0.1s;
        "
        onmouseenter="if(!this.classList.contains('active')){this.style.background='${SOL.base2}';}"
        onmouseleave="if(!this.classList.contains('active')){this.style.background='${isActive ? SOL.base2 : "transparent"}';}"
        onclick="this.dispatchEvent(new CustomEvent('city-select',{bubbles:true,detail:'${esc(c.key)}'}))">
          <span style="flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
            ${esc(c.label)}
            <span style="font-size:0.72rem;color:${SOL.base1};margin-left:3px;">${esc(c.country)}</span>
          </span>
          <span style="
            margin-left:8px; padding:1px 6px;
            background:${isActive ? SOL.base3 : SOL.base2};
            color:${SOL.base01};
            border-radius:10px; font-size:0.72rem; font-weight:600;
          ">${total}</span>
      </div>`;
    }).join("");

    // Wire up click events via delegation
    container.querySelectorAll(".exp-city-item").forEach(el => {
      el.addEventListener("city-select", e => onSelect(e.detail));
    });
  }


  // ─── UMAP ────────────────────────────────────────────────────────────────
  function renderUMAP(div, joined, selectedCity) {
    if (typeof Plotly === "undefined") return;

    const traces = buildUMAPTraces(joined, selectedCity);
    const layout = umapLayout();
    Plotly.newPlot(div, traces, layout, { responsive: true, displayModeBar: false });
  }

  function updateUMAP(div, joined, selectedCity) {
    if (typeof Plotly === "undefined") return;
    const traces = buildUMAPTraces(joined, selectedCity);
    Plotly.react(div, traces, umapLayout());
  }

  function buildUMAPTraces(joined, selectedCity) {
    const selectedIds = selectedCity
      ? new Set(selectedCity.artifacts.map(a => a.id))
      : null;

    // Background: all unselected points
    const bgX = [], bgY = [];
    for (const a of joined) {
      if (!selectedIds || !selectedIds.has(a.id)) {
        bgX.push(a.x);
        bgY.push(a.y);
      }
    }

    const traces = [{
      x: bgX, y: bgY,
      mode: "markers",
      type: "scatter",
      name: "Other",
      showlegend: false,
      marker: { color: DIM_COLOR, size: selectedIds ? 3 : 4, opacity: 0.4 },
      hoverinfo: "skip",
    }];

    // Highlighted points for selected city, coloured by type
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
          x: pts.x, y: pts.y,
          mode: "markers",
          type: "scatter",
          name: type.charAt(0).toUpperCase() + type.slice(1) + "s",
          marker: { color: TYPE_COLOR[type] || SOL.violet, size: 7, opacity: 0.9,
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
      paper_bgcolor: SOL.base3,
      plot_bgcolor:  SOL.base3,
      font: { color: SOL.base01, size: 11 },
      xaxis: { title: "UMAP 1", showgrid: false, zeroline: false, color: SOL.base1 },
      yaxis: { title: "UMAP 2", showgrid: false, zeroline: false, color: SOL.base1 },
      legend: {
        bgcolor: SOL.base2, bordercolor: "#d4cbb7", borderwidth: 1,
        font: { size: 11 }, x: 1, xanchor: "right", y: 1,
      },
      margin: { t: 20, l: 50, r: 10, b: 40 },
    };
  }


  // ─── City detail panel ───────────────────────────────────────────────────
  function renderDetail(container, city) {
    const arts     = city.artifacts;
    const counts   = countByType(arts);
    const ccCount  = arts.filter(a => a.case_study_flag).length;

    const statCards = [
      ["Papers",   counts.paper   || 0, SOL.blue],
      ["Patents",  counts.patent  || 0, SOL.orange],
      ["Projects", counts.project || 0, SOL.green],
      ["Carbon capture", ccCount, SOL.red],
    ].map(([label, val, color]) => `
      <div style="
        flex:1; min-width:80px;
        padding:10px 12px;
        background:${SOL.base3};
        border:1px solid ${SOL.base2};
        border-radius:5px; text-align:center;
      ">
        <div style="font-size:1.4rem;font-weight:700;color:${color};">${val}</div>
        <div style="font-size:0.72rem;color:${SOL.base1};margin-top:2px;">${label}</div>
      </div>`).join("");

    // Artifact list — most recent first, limit 80
    const sorted = [...arts].sort((a, b) => (b.year || 0) - (a.year || 0));
    const rows   = sorted.slice(0, 80).map(a => {
      const dot = `<span style="
        display:inline-block;width:8px;height:8px;border-radius:50%;
        background:${TYPE_COLOR[a.type] || SOL.violet};margin-right:6px;vertical-align:middle;">
      </span>`;
      const cc = a.case_study_flag
        ? `<span style="font-size:0.68rem;background:${SOL.red};color:#fff;
                        padding:1px 5px;border-radius:3px;margin-left:5px;">CC</span>`
        : "";
      return `<div style="
        padding:7px 16px; border-bottom:1px solid ${SOL.base2};
        font-size:0.8rem; color:${SOL.base02};
      ">
        ${dot}<strong>${esc(a.title || a.id)}</strong>${cc}
        <span style="float:right;color:${SOL.base1};font-size:0.75rem;">${a.year || "?"}</span>
      </div>`;
    }).join("");

    const moreNote = arts.length > 80
      ? `<div style="padding:8px 16px;font-size:0.75rem;color:${SOL.base1};">
           Showing 80 of ${arts.length} artifacts.</div>`
      : "";

    container.innerHTML = `
      <div style="padding:14px 16px 8px;">
        <div style="font-size:1.1rem;font-weight:700;color:${SOL.base02};">
          ${esc(city.label)}
          <span style="font-size:0.8rem;font-weight:400;color:${SOL.base1};margin-left:5px;">${esc(city.country)}</span>
        </div>
        <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">${statCards}</div>
      </div>
      <div style="padding:8px 16px 4px;font-size:0.72rem;font-weight:600;
                  letter-spacing:0.07em;text-transform:uppercase;color:${SOL.base1};">
        Artifacts
      </div>
      ${rows}
      ${moreNote}`;
  }


  // ─── Helpers ─────────────────────────────────────────────────────────────
  function countByType(artifacts) {
    const counts = {};
    for (const a of artifacts) {
      counts[a.type] = (counts[a.type] || 0) + 1;
    }
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
