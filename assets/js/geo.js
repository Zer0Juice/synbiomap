/**
 * geo.js — Geographic View
 *
 * Renders a city-level map of synthetic biology activity using
 * precomputed city-level aggregate data.
 *
 * Data file expected in website/assets/data/:
 *   - cities.json : array of {city, country, lat, lon, count_papers,
 *                   count_patents, count_projects, count_parts,
 *                   count_carbon_capture} objects
 *
 * Uses Plotly.js choropleth/scatter_geo for a static-hosting-compatible map.
 *
 * TODO: Wire up city selection and cluster composition display.
 */

(function () {
  const container = document.getElementById("geo-explorer");
  if (!container) return;

  fetch("assets/data/cities.json")
    .then((r) => r.json())
    .then((cities) => {
      renderGeoView(container, cities);
    })
    .catch((err) => {
      container.innerHTML =
        '<p style="padding:2em; color:#c00;">Could not load cities.json. ' +
        "Run the pipeline first to generate this file.</p>";
      console.error("Geo data load error:", err);
    });

  function renderGeoView(container, cities) {
    const totalCount = cities.map(
      (c) =>
        (c.count_papers || 0) +
        (c.count_patents || 0) +
        (c.count_projects || 0) +
        (c.count_parts || 0)
    );

    const trace = {
      type: "scattergeo",
      lat: cities.map((c) => c.lat),
      lon: cities.map((c) => c.lon),
      text: cities.map(
        (c) =>
          `${c.city}, ${c.country}<br>` +
          `Papers: ${c.count_papers || 0}<br>` +
          `Patents: ${c.count_patents || 0}<br>` +
          `Projects: ${c.count_projects || 0}<br>` +
          `Carbon capture: ${c.count_carbon_capture || 0}`
      ),
      marker: {
        size: totalCount.map((n) => Math.sqrt(n) * 3 + 4),
        color: "#268bd2",   // solarized blue
        opacity: 0.75,
        line: { width: 0.75, color: "#fdf6e3" },
      },
      hovertemplate: "%{text}<extra></extra>",
    };

    const layout = {
      title: { text: "Synthetic Biology Activity by City", font: { color: "#073642" } },
      paper_bgcolor: "#fdf6e3",
      font: { color: "#657b83" },
      geo: {
        showland: true,
        landcolor: "#eee8d5",
        showocean: true,
        oceancolor: "#d4e8ef",
        showcoastlines: true,
        coastlinecolor: "#93a1a1",
        showcountries: true,
        countrycolor: "#93a1a1",
        countrywidth: 0.75,
        showsubunits: true,
        subunitcolor: "#b8c5c5",
        subunitwidth: 0.4,
        bgcolor: "#fdf6e3",
        projection: { type: "natural earth" },
      },
      margin: { t: 40, l: 0, r: 0, b: 0 },
    };

    if (typeof Plotly !== "undefined") {
      Plotly.newPlot(container, [trace], layout, { responsive: true });
    } else {
      container.innerHTML =
        '<p style="padding:2em; color:#888;">Plotly.js is not loaded.</p>';
    }
  }
})();
