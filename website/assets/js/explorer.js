/**
 * explorer.js — Linked Semantic-Space + Map Explorer
 *
 * A single widget with two panels that talk to each other:
 *
 *   Left  — the shared semantic space (UMAP of every project, paper, patent),
 *           coloured by artifact type, with the larger topic clusters labelled.
 *   Right — a world map of the same artifacts, aggregated into city bubbles.
 *
 * The two views are linked:
 *   • Click an artifact in the semantic space  → its city lights up on the map.
 *   • Click a city on the map                  → all of that city's artifacts
 *                                                light up in the semantic space.
 *   • Toolbar toggles show/hide each artifact type and narrow to carbon-capture
 *     work; both panels respond together.
 *
 * Data files (in website/assets/data/):
 *   artifacts.json   — [{id, type, title, year, city, country, lat, lon,
 *                        case_study_flag, cluster_label, cluster_name}]
 *   projections.json — [{id, x, y, cluster, label}]   (UMAP coordinates)
 *   abstracts.json   — {id: abstractText}  (large; loaded lazily on first click)
 *
 * Static-hosting compatible: everything is precomputed, no server needed.
 * Palette: Solarized Light (Ethan Schoonover, 2011), matching the rest of site.
 */

(function () {

  // ─── Palette ─────────────────────────────────────────────────────────────
  const SOL = {
    base03: "#002b36", base02: "#073642", base01: "#586e75", base00: "#657b83",
    base1:  "#93a1a1", base2:  "#eee8d5", base3:  "#fdf6e3",
    yellow: "#b58900", orange: "#cb4b16", red: "#dc322f", magenta: "#d33682",
    blue:   "#268bd2", cyan:   "#2aa198", green: "#859900",
  };

  const TYPE_COLOR = {
    paper: SOL.blue, patent: SOL.orange, project: SOL.green, part: SOL.magenta,
  };
  const TYPE_LABEL = {
    paper: "Papers", patent: "Patents", project: "iGEM Projects", part: "iGEM Parts",
  };
  // Artifact types shown, in a fixed draw order (bottom → top on the map).
  const TYPE_ORDER = ["paper", "project", "patent"];

  const DIM_COLOR = "#c8cfd4";              // greyed-out points
  const CC_COLOR  = SOL.red;                // carbon-capture accent
  const MAX_CLUSTER_LABELS = 22;            // label only the larger clusters

  // ─── Bootstrap ───────────────────────────────────────────────────────────
  const root = document.getElementById("explorer-app");
  if (!root) return;
  root.innerHTML = `<p style="padding:2em;color:${SOL.base1};">Loading data…</p>`;

  // abstracts.json is large (~20 MB). Load once, lazily, on first artifact click.
  let abstractsCache = null, abstractsLoading = null;
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
    .then(([artifacts, projections]) => {
      try { init(artifacts, projections); }
      catch (err) {
        root.innerHTML = `<p style="padding:2em;color:#c00;font-family:monospace;">Init error: ${err}</p>`;
        console.error("Explorer init error:", err);
      }
    })
    .catch(err => {
      root.innerHTML =
        `<p style="padding:2em;color:#c00;font-family:monospace;">Explorer error: ${err}<br><br>` +
        `<small>Check the browser console (F12) for details.</small></p>`;
      console.error("Explorer load error:", err);
    });


  // ─── Main init ───────────────────────────────────────────────────────────
  function init(artifacts, projections) {
    // Join each artifact to its UMAP coordinates by id.
    const projMap = {};
    for (const p of projections) projMap[p.id] = p;

    const items = artifacts
      .filter(a => projMap[a.id] && a.lat != null && a.lon != null)
      .map(a => ({
        id: a.id, type: a.type, title: a.title, year: a.year,
        city: (a.city || "Unknown").trim(), country: (a.country || "").trim(),
        lat: a.lat, lon: a.lon,
        cc: !!a.case_study_flag,
        cluster: projMap[a.id].cluster,
        clusterName: a.cluster_name || projMap[a.id].label || "",
        x: projMap[a.id].x, y: projMap[a.id].y,
        ckey: `${(a.city || "Unknown").trim()}||${(a.country || "").trim()}`,
      }));

    const itemById = {};
    for (const it of items) itemById[it.id] = it;

    // City index — aggregate artifacts into city bubbles.
    const cityIndex = buildCityIndex(items);

    // Which types are actually present, in the fixed order.
    const TYPES = TYPE_ORDER.filter(t => items.some(it => it.type === t));
    const typeTotals = {};
    for (const t of TYPES) typeTotals[t] = items.filter(it => it.type === t).length;

    // Cluster label annotations (computed once; stable across selections).
    const clusterAnnotations = buildClusterAnnotations(items);

    // ─── Shell ──────────────────────────────────────────────────────────────
    root.innerHTML = buildShell(TYPES, typeTotals);
    const umapDiv   = document.getElementById("exp-umap");
    const mapDiv    = document.getElementById("exp-map");
    const detailDiv = document.getElementById("exp-detail");

    // ─── State ──────────────────────────────────────────────────────────────
    const state = {
      types: Object.fromEntries(TYPES.map(t => [t, true])),
      ccOnly: false,
      cityKey: null,      // a city is in focus (dims the semantic space to it)
      artifactId: null,   // a single artifact is pinned (ring + city highlight)
    };
    let umapReady = false, mapReady = false;

    // ─── Filtering ──────────────────────────────────────────────────────────
    function passesFilter(it) {
      if (!state.types[it.type]) return false;
      if (state.ccOnly && !it.cc) return false;
      return true;
    }
    function filteredItems() { return items.filter(passesFilter); }

    // Which city bubble should carry the "selected" ring.
    function highlightCityKey() {
      if (state.cityKey) return state.cityKey;
      if (state.artifactId && itemById[state.artifactId]) return itemById[state.artifactId].ckey;
      return null;
    }

    // ─── Draw everything ────────────────────────────────────────────────────
    function redraw() { drawUMAP(); drawMap(); renderDetail(); }

    function drawUMAP() {
      const traces = umapTraces(filteredItems(), state, itemById);
      const layout = umapLayout(clusterAnnotations);
      if (!umapReady) {
        Plotly.newPlot(umapDiv, traces, layout,
          { responsive: true, displayModeBar: false, scrollZoom: true });
        umapDiv.on("plotly_click", ev => {
          const pt = ev.points && ev.points[0];
          if (pt && pt.customdata) onArtifactSelect(pt.customdata);
        });
        umapReady = true;
      } else {
        Plotly.react(umapDiv, traces, layout);
      }
    }

    function drawMap() {
      const traces = mapTraces(cityIndex, filteredItems(), TYPES, highlightCityKey());
      const layout = mapLayout();
      if (!mapReady) {
        Plotly.newPlot(mapDiv, traces, layout,
          { responsive: true, displayModeBar: false });
        mapDiv.on("plotly_click", ev => {
          const pt = ev.points && ev.points[0];
          if (pt && pt.customdata) onCitySelect(pt.customdata);
        });
        mapReady = true;
      } else {
        Plotly.react(mapDiv, traces, layout);
      }
    }

    // ─── Selection handlers ─────────────────────────────────────────────────
    function onCitySelect(cityKey) {
      if (state.cityKey === cityKey) { state.cityKey = null; state.artifactId = null; }
      else { state.cityKey = cityKey; state.artifactId = null; }
      redraw();
    }

    function onArtifactSelect(id) {
      if (state.artifactId === id) { state.artifactId = null; renderDetail(); drawUMAP(); drawMap(); return; }
      state.artifactId = id;
      renderDetail();          // show card immediately (abstract may still load)
      drawUMAP(); drawMap();
      getAbstracts().then(() => { if (state.artifactId === id) renderDetail(); });
    }

    function clearSelection() { state.cityKey = null; state.artifactId = null; redraw(); }

    // ─── Detail strip ───────────────────────────────────────────────────────
    function renderDetail() {
      if (state.artifactId && itemById[state.artifactId]) {
        detailDiv.innerHTML = artifactCard(itemById[state.artifactId], abstractsCache, !!state.cityKey);
        const close = detailDiv.querySelector("#exp-detail-close");
        if (close) close.addEventListener("click", () => { state.artifactId = null; renderDetail(); drawUMAP(); drawMap(); });
        return;
      }
      if (state.cityKey && cityIndex[state.cityKey]) {
        detailDiv.innerHTML = cityCard(cityIndex[state.cityKey], passesFilter);
        detailDiv.querySelectorAll(".exp-art-row").forEach(el =>
          el.addEventListener("click", () => onArtifactSelect(el.dataset.id)));
        return;
      }
      detailDiv.innerHTML = `
        <div style="padding:16px 18px;color:${SOL.base1};font-size:0.88rem;line-height:1.6;">
          Click a point in the semantic space to pin an artifact and find its city, or click a city
          on the map to light up everything it contributed. Toggles above show or hide each type.
        </div>`;
    }

    // ─── Wire toolbar ─────────────────────────────────────────────────────────
    TYPES.forEach(t => {
      const cb = document.getElementById(`exp-toggle-${t}`);
      cb.addEventListener("change", () => { state.types[t] = cb.checked; redraw(); });
    });
    const ccBox = document.getElementById("exp-toggle-cc");
    ccBox.addEventListener("change", () => { state.ccOnly = ccBox.checked; redraw(); });
    document.getElementById("exp-clear").addEventListener("click", clearSelection);

    // First paint.
    redraw();
  }


  // ─── City index ──────────────────────────────────────────────────────────
  function buildCityIndex(items) {
    const index = {};
    for (const it of items) {
      if (!index[it.ckey]) {
        index[it.ckey] = { key: it.ckey, label: it.city, country: it.country,
                           lat: it.lat, lon: it.lon, items: [] };
      }
      index[it.ckey].items.push(it);
    }
    return index;
  }


  // ─── Cluster label annotations ─────────────────────────────────────────────
  // Label only the larger clusters (median position of their points) so the
  // semantic space stays readable rather than swamped by 80 overlapping tags.
  function buildClusterAnnotations(items) {
    const byCluster = {};
    for (const it of items) {
      if (it.cluster == null || it.cluster < 0 || !it.clusterName) continue;
      (byCluster[it.cluster] = byCluster[it.cluster] || { name: it.clusterName, xs: [], ys: [] });
      byCluster[it.cluster].xs.push(it.x);
      byCluster[it.cluster].ys.push(it.y);
    }
    const top = Object.values(byCluster)
      .sort((a, b) => b.xs.length - a.xs.length)
      .slice(0, MAX_CLUSTER_LABELS);
    return top.map(c => ({
      x: median(c.xs), y: median(c.ys), text: c.name,
      showarrow: false, font: { size: 9.5, color: SOL.base01 },
      bgcolor: "rgba(253,246,227,0.6)", borderpad: 1,
      captureevents: false,
    }));
  }


  // ─── Semantic-space traces ─────────────────────────────────────────────────
  function umapTraces(vis, state, itemById) {
    const traces = [];
    const cityFocus = !!state.cityKey;

    if (cityFocus) {
      // Everything else fades to context; the selected city's points stay lit.
      const bgX = [], bgY = [];
      const focus = {};   // type -> {x,y,text,ids}
      for (const it of vis) {
        if (it.ckey === state.cityKey) {
          const b = (focus[it.type] = focus[it.type] || { x: [], y: [], text: [], ids: [] });
          b.x.push(it.x); b.y.push(it.y);
          b.text.push(`${esc(it.title || it.id)} (${it.year || "?"})`);
          b.ids.push(it.id);
        } else { bgX.push(it.x); bgY.push(it.y); }
      }
      traces.push(bgTrace(bgX, bgY, 3));
      for (const t of TYPE_ORDER) {
        if (!focus[t]) continue;
        traces.push(pointTrace(focus[t], t, 8));
      }
    } else {
      // No city in focus: colour every visible point by type.
      const byType = {};
      for (const it of vis) {
        const b = (byType[it.type] = byType[it.type] || { x: [], y: [], text: [], ids: [] });
        b.x.push(it.x); b.y.push(it.y);
        b.text.push(`${esc(it.title || it.id)} (${it.year || "?"})`);
        b.ids.push(it.id);
      }
      for (const t of TYPE_ORDER) {
        if (!byType[t]) continue;
        traces.push(pointTrace(byType[t], t, 5));
      }
    }

    // Pinned-artifact ring (only if the artifact is currently visible).
    if (state.artifactId && itemById[state.artifactId]) {
      const a = itemById[state.artifactId];
      const shown = cityFocus ? a.ckey === state.cityKey : true;
      if (shown && state.types[a.type] && (!state.ccOnly || a.cc)) {
        traces.push({
          x: [a.x], y: [a.y], type: "scatter", mode: "markers",
          name: "Selected", showlegend: false, hoverinfo: "skip",
          marker: { size: 18, color: "rgba(0,0,0,0)",
                    line: { color: SOL.base02, width: 2.5 } },
        });
      }
    }
    return traces;
  }

  function bgTrace(x, y, size) {
    return {
      x, y, type: "scattergl", mode: "markers", name: "Other",
      showlegend: false, hoverinfo: "skip",
      marker: { color: DIM_COLOR, size, opacity: 0.35 },
    };
  }

  function pointTrace(b, type, size) {
    return {
      x: b.x, y: b.y, type: "scattergl", mode: "markers",
      name: TYPE_LABEL[type] || type,
      marker: { color: TYPE_COLOR[type] || SOL.cyan, size, opacity: 0.85,
                line: { width: 0.4, color: SOL.base3 } },
      text: b.text, customdata: b.ids,
      hovertemplate: "%{text}<extra></extra>",
    };
  }

  function umapLayout(annotations) {
    return {
      paper_bgcolor: SOL.base3, plot_bgcolor: SOL.base3,
      font: { color: SOL.base01, size: 11 },
      xaxis: { showgrid: false, zeroline: false, showticklabels: false, ticks: "" },
      yaxis: { showgrid: false, zeroline: false, showticklabels: false, ticks: "" },
      legend: { bgcolor: SOL.base2, bordercolor: "#d4cbb7", borderwidth: 1,
                font: { size: 11 }, orientation: "h", x: 0, xanchor: "left",
                y: 1.02, yanchor: "bottom" },
      annotations,
      margin: { t: 6, l: 6, r: 6, b: 6 },
      hovermode: "closest",
    };
  }


  // ─── Map traces ────────────────────────────────────────────────────────────
  function mapTraces(cityIndex, vis, TYPES, hlKey) {
    // Aggregate the currently-visible artifacts back into per-city, per-type counts.
    const agg = {};   // ckey -> {city, country, lat, lon, counts:{type:n}}
    for (const it of vis) {
      const c = (agg[it.ckey] = agg[it.ckey] ||
        { city: it.city, country: it.country, lat: it.lat, lon: it.lon, counts: {} });
      c.counts[it.type] = (c.counts[it.type] || 0) + 1;
    }
    const cities = Object.entries(agg).map(([key, c]) => ({ key, ...c }));

    const traces = TYPES.map(t => {
      const pts = cities.filter(c => (c.counts[t] || 0) > 0);
      return {
        type: "scattergeo", name: TYPE_LABEL[t] || t,
        lat: pts.map(c => c.lat), lon: pts.map(c => c.lon),
        customdata: pts.map(c => c.key),
        text: pts.map(c => `<b>${esc(c.city)}, ${esc(c.country)}</b><br>${TYPE_LABEL[t]}: ${c.counts[t]}`),
        marker: { size: pts.map(c => Math.sqrt(c.counts[t]) * 2.2 + 4),
                  color: TYPE_COLOR[t] || SOL.cyan, opacity: 0.6,
                  line: { width: 0.5, color: SOL.base3 } },
        hovertemplate: "%{text}<extra></extra>", showlegend: false,
      };
    });

    // Selected-city ring on top.
    if (hlKey && cityIndex[hlKey]) {
      const c = cityIndex[hlKey];
      traces.push({
        type: "scattergeo", name: "Selected", lat: [c.lat], lon: [c.lon],
        text: [`<b>${esc(c.label)}, ${esc(c.country)}</b>`],
        marker: { size: 20, color: "rgba(0,0,0,0)", symbol: "circle-open",
                  line: { width: 3, color: SOL.red } },
        hovertemplate: "%{text}<extra></extra>", showlegend: false,
      });
    }
    return traces;
  }

  function mapLayout() {
    return {
      paper_bgcolor: SOL.base3, font: { color: SOL.base00 },
      geo: {
        showland: true, landcolor: SOL.base2,
        showocean: true, oceancolor: "#d4e8ef",
        showcoastlines: true, coastlinecolor: SOL.base1,
        showcountries: true, countrycolor: SOL.base1, countrywidth: 0.5,
        showsubunits: true, subunitcolor: "#c4cfcf", subunitwidth: 0.3,
        bgcolor: SOL.base3, projection: { type: "natural earth" },
      },
      margin: { t: 6, l: 0, r: 0, b: 0 },
    };
  }


  // ─── Shell HTML ────────────────────────────────────────────────────────────
  function buildShell(TYPES, typeTotals) {
    const toggles = TYPES.map(t => `
      <label for="exp-toggle-${t}" style="
        display:inline-flex;align-items:center;gap:7px;
        padding:6px 10px;cursor:pointer;
        border:1px solid ${SOL.base2};border-radius:6px;background:${SOL.base3};
        font-size:0.82rem;color:${SOL.base02};
      ">
        <input type="checkbox" id="exp-toggle-${t}" checked
               style="accent-color:${TYPE_COLOR[t]};width:15px;height:15px;cursor:pointer;">
        <span style="width:10px;height:10px;border-radius:50%;background:${TYPE_COLOR[t]};flex-shrink:0;"></span>
        <span style="font-weight:600;">${TYPE_LABEL[t]}</span>
        <span style="color:${SOL.base1};font-size:0.76rem;">${typeTotals[t].toLocaleString()}</span>
      </label>`).join("");

    const ccToggle = `
      <label for="exp-toggle-cc" style="
        display:inline-flex;align-items:center;gap:7px;
        padding:6px 10px;cursor:pointer;
        border:1px solid ${SOL.base2};border-radius:6px;background:${SOL.base3};
        font-size:0.82rem;color:${SOL.base02};
      ">
        <input type="checkbox" id="exp-toggle-cc"
               style="accent-color:${CC_COLOR};width:15px;height:15px;cursor:pointer;">
        <span style="width:10px;height:10px;border-radius:50%;background:${CC_COLOR};flex-shrink:0;"></span>
        <span style="font-weight:600;">Carbon capture only</span>
      </label>`;

    const panel = (id, title, sub) => `
      <div style="
        flex:1 1 420px;min-width:300px;display:flex;flex-direction:column;
        border:1px solid ${SOL.base2};border-radius:6px;overflow:hidden;background:${SOL.base3};
      ">
        <div style="padding:8px 12px;border-bottom:1px solid ${SOL.base2};">
          <div style="font-size:0.7rem;font-weight:700;letter-spacing:0.08em;
                      text-transform:uppercase;color:${SOL.base1};">${title}</div>
          <div style="font-size:0.74rem;color:${SOL.base00};margin-top:1px;">${sub}</div>
        </div>
        <div id="${id}" style="height:520px;min-height:0;"></div>
      </div>`;

    return `
      <div style="font-family:inherit;">
        <div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px;
                    padding:10px 12px;margin-bottom:10px;
                    border:1px solid ${SOL.base2};border-radius:6px;background:${SOL.base3};">
          <span style="font-size:0.7rem;font-weight:700;letter-spacing:0.07em;
                       text-transform:uppercase;color:${SOL.base1};margin-right:2px;">Show</span>
          ${toggles}
          ${ccToggle}
          <button id="exp-clear" style="
            margin-left:auto;padding:6px 12px;cursor:pointer;
            border:1px solid ${SOL.base2};border-radius:6px;background:${SOL.base3};
            color:${SOL.base01};font-size:0.8rem;font-weight:600;">
            Clear selection
          </button>
        </div>

        <div style="display:flex;flex-wrap:wrap;gap:10px;">
          ${panel("exp-umap", "Semantic space", "Click a point to pin an artifact")}
          ${panel("exp-map",  "World map",      "Click a city to light up its work")}
        </div>

        <div id="exp-detail" style="
          margin-top:10px;border:1px solid ${SOL.base2};border-radius:6px;
          background:${SOL.base3};min-height:80px;"></div>
      </div>`;
  }


  // ─── City detail card ──────────────────────────────────────────────────────
  function cityCard(city, passesFilter) {
    const arts   = city.items.filter(passesFilter);
    const counts = countByType(arts);
    const ccCount = arts.filter(a => a.cc).length;

    const statCards = [
      ["Papers", counts.paper || 0, SOL.blue],
      ["Patents", counts.patent || 0, SOL.orange],
      ["iGEM Projects", counts.project || 0, SOL.green],
      ["Carbon capture", ccCount, CC_COLOR],
    ].map(([label, val, color]) => `
      <div style="flex:1;min-width:70px;padding:9px 12px;background:${SOL.base3};
                  border:1px solid ${SOL.base2};border-radius:5px;text-align:center;">
        <div style="font-size:1.3rem;font-weight:700;color:${color};">${val}</div>
        <div style="font-size:0.68rem;color:${SOL.base1};margin-top:2px;">${label}</div>
      </div>`).join("");

    const sorted = [...arts].sort((a, b) => (b.year || 0) - (a.year || 0));
    const rows = sorted.slice(0, 120).map(a => {
      const dot = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;
        background:${TYPE_COLOR[a.type] || SOL.cyan};margin-right:7px;flex-shrink:0;margin-top:3px;"></span>`;
      const cc = a.cc ? `<span style="font-size:0.62rem;background:${CC_COLOR};color:#fff;
        padding:1px 4px;border-radius:3px;margin-left:5px;white-space:nowrap;">CC</span>` : "";
      return `<div class="exp-art-row" data-id="${esc(a.id)}"
        style="display:flex;align-items:flex-start;padding:6px 16px;cursor:pointer;
               border-bottom:1px solid ${SOL.base2};font-size:0.8rem;color:${SOL.base02};"
        onmouseenter="this.style.background='${SOL.base2}'"
        onmouseleave="this.style.background='transparent'">
        ${dot}<span style="flex:1;min-width:0;"><strong>${esc(a.title || a.id)}</strong>${cc}</span>
        <span style="margin-left:8px;color:${SOL.base1};font-size:0.75rem;white-space:nowrap;flex-shrink:0;">${a.year || "?"}</span>
      </div>`;
    }).join("");

    const more = arts.length > 120
      ? `<div style="padding:8px 16px;font-size:0.75rem;color:${SOL.base1};">Showing 120 of ${arts.length}.</div>`
      : "";

    return `
      <div style="padding:14px 16px 8px;">
        <div style="font-size:1.05rem;font-weight:700;color:${SOL.base02};">
          ${esc(city.label)}
          <span style="font-size:0.8rem;font-weight:400;color:${SOL.base1};margin-left:5px;">${esc(city.country)}</span>
        </div>
        <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">${statCards}</div>
      </div>
      <div style="padding:6px 16px 4px;font-size:0.68rem;font-weight:600;letter-spacing:0.07em;
                  text-transform:uppercase;color:${SOL.base1};">Artifacts — click to open</div>
      ${rows}${more}`;
  }


  // ─── Artifact detail card ───────────────────────────────────────────────────
  function artifactCard(a, abstracts, inCity) {
    const color     = TYPE_COLOR[a.type] || SOL.cyan;
    const typeLabel = (TYPE_LABEL[a.type] || a.type).replace(/s$/, "");
    const abstract  = abstracts ? (abstracts[a.id] || "") : null;   // null = loading
    const link      = buildLink(a);
    const cityLine  = [a.city, a.country].filter(Boolean).join(", ");
    const clusterLine = a.clusterName
      ? `<span style="font-size:0.72rem;color:${SOL.base1};">Cluster: ${esc(a.clusterName)}</span>` : "";

    const ccBadge = a.cc
      ? `<span style="font-size:0.66rem;background:${CC_COLOR};color:#fff;padding:1px 6px;border-radius:3px;margin-left:6px;">Carbon capture</span>` : "";

    const linkBtn = link
      ? `<a href="${esc(link.url)}" target="_blank" rel="noopener"
           style="display:inline-block;margin-top:10px;padding:5px 12px;border-radius:4px;
                  background:${color};color:#fff;font-size:0.78rem;font-weight:600;text-decoration:none;">${esc(link.label)}</a>` : "";

    return `
      <div style="padding:14px 16px;">
        <div style="display:flex;align-items:baseline;flex-wrap:wrap;gap:6px;margin-bottom:8px;">
          <span style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                       letter-spacing:0.07em;color:${color};">${esc(typeLabel)}</span>
          ${ccBadge}
          <span style="margin-left:auto;font-size:0.75rem;color:${SOL.base1};">${a.year || ""}</span>
          <button id="exp-detail-close" title="Close"
            style="margin-left:8px;border:none;background:transparent;color:${SOL.base1};
                   font-size:1.1rem;line-height:1;cursor:pointer;">✕</button>
        </div>
        <div style="font-size:0.95rem;font-weight:600;color:${SOL.base02};margin-bottom:4px;">${esc(a.title || a.id)}</div>
        <div style="display:flex;flex-wrap:wrap;gap:12px;margin-bottom:8px;">
          ${cityLine ? `<span style="font-size:0.75rem;color:${SOL.base1};">📍 ${esc(cityLine)}${inCity ? " · highlighted on map" : ""}</span>` : ""}
          ${clusterLine}
        </div>
        ${abstract === null
          ? `<div style="font-size:0.78rem;color:${SOL.base1};border-top:1px solid #d4cbb7;padding-top:8px;">Loading abstract…</div>`
          : abstract
            ? `<div style="font-size:0.82rem;color:${SOL.base01};line-height:1.6;max-height:160px;
                 overflow-y:auto;border-top:1px solid #d4cbb7;padding-top:8px;">${esc(abstract)}</div>`
            : ""}
        ${linkBtn}
      </div>`;
  }


  // ─── Link generation ─────────────────────────────────────────────────────
  /**
   * Papers:   id is an OpenAlex URL → link straight to OpenAlex (shows DOI).
   * Patents:  id is an opaque internal hash (Paul Oldham's set), not publicly
   *           resolvable, so we return no link rather than a broken one.
   * Projects: id is "igem_{team}_{year}" → https://{year}.igem.org/Team:{team}
   */
  function buildLink(a) {
    if (a.type === "paper" && a.id && a.id.startsWith("https://")) {
      return { url: a.id, label: "View on OpenAlex →" };
    }
    if (a.type === "project" && a.id && a.id.startsWith("igem_")) {
      const url = igem_wiki_url(a.id);
      if (url) return { url, label: "iGEM Wiki →" };
    }
    return null;
  }

  function igem_wiki_url(id) {
    const m = id.slice("igem_".length).match(/^(.+)_(\d{4})$/);
    if (!m) return null;
    return `https://${m[2]}.igem.org/Team:${encodeURIComponent(m[1])}`;
  }


  // ─── Helpers ─────────────────────────────────────────────────────────────
  function countByType(arts) {
    const c = {};
    for (const a of arts) c[a.type] = (c[a.type] || 0) + 1;
    return c;
  }

  function median(arr) {
    if (!arr.length) return 0;
    const s = [...arr].sort((a, b) => a - b);
    const m = Math.floor(s.length / 2);
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  }

  function esc(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

})();
