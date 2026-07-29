/**
 * methods_map.js — Interactive tripartite world map
 *
 * One city-level map showing all three artifact types at once, with a side
 * panel of toggles to show or hide each type. Replaces the static three-panel
 * world_map.png on the Methods page.
 *
 * Data file (website/assets/data/):
 *   cities.json : [{city, country, lat, lon, count_papers, count_patents,
 *                   count_projects, count_carbon_capture}]
 *
 * Static-hosting compatible: all data is precomputed. Plotly scattergeo,
 * one trace per artifact type, toggled via checkboxes.
 *
 * Palette: Solarized Light, matching explorer.js / geo.js.
 */

(function () {
  const root = document.getElementById("methods-geo-map");
  if (!root) return;

  const SOL = {
    base03: "#002b36", base02: "#073642", base01: "#586e75", base00: "#657b83",
    base1: "#93a1a1", base2: "#eee8d5", base3: "#fdf6e3",
    blue: "#268bd2", orange: "#cb4b16", green: "#859900",
  };

  // One entry per artifact type, in draw order (bottom → top).
  const TYPES = [
    { key: "count_papers",   label: "Papers",   color: SOL.blue },
    { key: "count_projects", label: "Projects", color: SOL.green },
    { key: "count_patents",  label: "Patents",  color: SOL.orange },
  ];

  root.innerHTML = `<p style="padding:2em;color:${SOL.base1};">Loading map…</p>`;

  fetch("assets/data/cities.json")
    .then((r) => r.json())
    .then((cities) => {
      try { init(cities); }
      catch (err) {
        root.innerHTML = `<p style="padding:2em;color:#c00;font-family:monospace;">Map init error: ${err}</p>`;
        console.error("Methods map init error:", err);
      }
    })
    .catch((err) => {
      root.innerHTML =
        `<p style="padding:2em;color:#c00;">Could not load cities.json.</p>`;
      console.error("Methods map load error:", err);
    });

  function init(cities) {
    // Per-type totals, for the toggle labels.
    const totals = {};
    for (const t of TYPES) {
      totals[t.key] = cities.reduce((s, c) => s + (c[t.key] || 0), 0);
    }

    root.innerHTML = buildShell();
    const mapDiv = document.getElementById("mgeo-map");

    // One scattergeo trace per type; only cities that have that type.
    const traces = TYPES.map((t) => {
      const pts = cities.filter((c) => (c[t.key] || 0) > 0);
      return {
        type: "scattergeo",
        name: t.label,
        lat: pts.map((c) => c.lat),
        lon: pts.map((c) => c.lon),
        text: pts.map(
          (c) => `<b>${c.city}, ${c.country}</b><br>${t.label}: ${c[t.key]}`
        ),
        marker: {
          size: pts.map((c) => Math.sqrt(c[t.key]) * 2.1 + 3),
          color: t.color,
          opacity: 0.62,
          line: { width: 0.5, color: SOL.base3 },
        },
        hovertemplate: "%{text}<extra></extra>",
        showlegend: false,
      };
    });

    Plotly.newPlot(mapDiv, traces, layout(), {
      responsive: true,
      displayModeBar: false,
    });

    // Wire the side toggles to trace visibility.
    TYPES.forEach((t, i) => {
      const cb = document.getElementById(`mgeo-toggle-${i}`);
      cb.addEventListener("change", () => {
        Plotly.restyle(mapDiv, { visible: cb.checked ? true : false }, [i]);
      });
    });

    function toggleRow(t, i) {
      return `
        <label for="mgeo-toggle-${i}" style="
          display:flex;align-items:center;gap:9px;
          padding:9px 11px;margin-bottom:6px;cursor:pointer;
          border:1px solid ${SOL.base2};border-radius:6px;
          background:${SOL.base3};font-size:0.86rem;color:${SOL.base02};
        ">
          <input type="checkbox" id="mgeo-toggle-${i}" checked
                 style="accent-color:${t.color};width:15px;height:15px;cursor:pointer;">
          <span style="width:11px;height:11px;border-radius:50%;background:${t.color};flex-shrink:0;"></span>
          <span style="flex:1;font-weight:600;">${t.label}</span>
          <span style="color:${SOL.base1};font-size:0.78rem;">${totals[t.key].toLocaleString()}</span>
        </label>`;
    }

    function buildShell() {
      return `
        <div style="
          display:flex;gap:0;height:520px;
          border:1px solid ${SOL.base2};border-radius:6px;overflow:hidden;
          background:${SOL.base3};font-family:inherit;
        ">
          <div style="
            width:190px;min-width:160px;padding:14px 12px;
            border-right:1px solid ${SOL.base2};background:${SOL.base3};
          ">
            <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
                        text-transform:uppercase;color:${SOL.base1};margin-bottom:10px;">
              Artifact type
            </div>
            ${TYPES.map(toggleRow).join("")}
            <div style="margin-top:12px;font-size:0.72rem;color:${SOL.base1};line-height:1.5;">
              Toggle a type on or off. Bubble size scales with that type's count in the city.
            </div>
          </div>
          <div id="mgeo-map" style="flex:1;min-width:0;"></div>
        </div>`;
    }
  }

  function layout() {
    return {
      paper_bgcolor: SOL.base3,
      font: { color: SOL.base00 },
      geo: {
        showland: true, landcolor: SOL.base2,
        showocean: true, oceancolor: "#d4e8ef",
        showcoastlines: true, coastlinecolor: SOL.base1,
        showcountries: true, countrycolor: SOL.base1, countrywidth: 0.5,
        showsubunits: true, subunitcolor: "#c4cfcf", subunitwidth: 0.3,
        bgcolor: SOL.base3,
        projection: { type: "natural earth" },
      },
      margin: { t: 8, l: 0, r: 0, b: 0 },
    };
  }
})();
