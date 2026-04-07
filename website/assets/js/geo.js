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
        color: "#4e79a7",
        opacity: 0.7,
        line: { width: 0.5, color: "white" },
      },
      hovertemplate: "%{text}<extra></extra>",
    };

    const layout = {
      title: "Synthetic Biology Activity by City",
      geo: {
        showland: true,
        landcolor: "#f0f0f0",
        showocean: true,
        oceancolor: "#e8f4f8",
        showcoastlines: true,
        coastlinecolor: "#ccc",
        showcountries: true,
        countrycolor: "#aaa",
        countrywidth: 0.75,
        showsubunits: true,
        subunitcolor: "#ccc",
        subunitwidth: 0.4,
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
