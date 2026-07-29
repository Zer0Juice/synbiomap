/**
 * centroid.js — the size-artifact story for the *centroid* relatedness measure.
 *
 * The centroid measure averages a city's project embeddings into one vector and
 * its papers into another, then takes the cosine between them (`semantic_overlap`
 * in city_level.csv). It looks like a relatedness score, but it mostly tracks how
 * much a city publishes: averaging many vectors drags both centroids toward the
 * field-wide mean, so heavy publishers score near 1.0 automatically. Across 385
 * cities, relatedness rises with paper count at r ≈ 0.70 — about half the variance.
 *
 * This widget makes that confound something you drive rather than read:
 *   • one dot per city — x = papers published (log), y = centroid relatedness;
 *   • an orange trend line showing the upward drift;
 *   • one "minimum papers" scrubber. Drag it right and the highlighted set narrows
 *     to the biggest publishers while its mean relatedness (the blue line + readout)
 *     climbs toward 1.0. The story: size is doing the work, not shared topics.
 *
 * It is deliberately labelled the measure we DISCARD, which sets up the switch to
 * topic-profile co-membership on the next slide (see relatedness.py).
 *
 * Static-hosting friendly: reads one precomputed JSON, no server, no embeddings at
 * runtime. Palette: Solarized Light, matching explorer.js and the rest of the site.
 *
 * Data: assets/data/centroid_relatedness.json
 *       [{city, country, papers, projects, overlap}]  (from make_centroid_widget_data.py)
 */

(function () {
  const SOL = {
    base01: "#586e75", base00: "#657b83", base1: "#93a1a1",
    base2: "#eee8d5", base3: "#fdf6e3",
    orange: "#cb4b16", red: "#dc322f", blue: "#268bd2", green: "#859900",
  };
  const DIM = "#c8cfd4";              // cities below the current threshold
  const HL = SOL.blue;                // cities kept by the scrubber

  const root = document.getElementById("centroid-app");
  if (!root) return;
  root.innerHTML = `<p style="padding:1.5em;color:${SOL.base1};">Loading…</p>`;

  // Plotly may already be on the page (the explorer slide loads it). If not, pull
  // it in so this widget also works standalone. Then boot.
  function withPlotly(cb) {
    if (window.Plotly) return cb();
    const s = document.createElement("script");
    s.src = "https://cdn.plot.ly/plotly-2.27.0.min.js";
    s.onload = cb;
    s.onerror = () => { root.innerHTML =
      `<p style="padding:1.5em;color:#c00;">Could not load Plotly.</p>`; };
    document.head.appendChild(s);
  }

  withPlotly(() => {
    fetch("assets/data/centroid_relatedness.json")
      .then(r => r.json())
      .then(init)
      .catch(err => {
        root.innerHTML =
          `<p style="padding:1.5em;color:#c00;font-family:monospace;">Data error: ${err}</p>`;
        console.error("centroid widget:", err);
      });
  });

  function init(cities) {
    // Pre-compute the fields we plot. x is log-scaled paper count.
    for (const c of cities) {
      c.lx = Math.log(c.papers);        // fit lives in log space
      c.docs = c.papers + c.projects;
    }
    const maxPapers = Math.max(...cities.map(c => c.papers));
    const overallMean = mean(cities.map(c => c.overlap));

    // Least-squares fit of relatedness on log(papers). On a log x-axis this plots
    // as a straight line, so two endpoints are enough to draw it.
    const fit = leastSquares(cities.map(c => c.lx), cities.map(c => c.overlap));
    const r = pearson(cities.map(c => c.lx), cities.map(c => c.overlap));
    const xEnds = [Math.min(...cities.map(c => c.papers)), maxPapers];
    const yEnds = xEnds.map(x => fit.a + fit.b * Math.log(x));

    // ─── Shell ───────────────────────────────────────────────────────────────
    root.innerHTML = `
      <div style="font-family:inherit;">
        <div style="display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:2px;">
          <span style="font-size:0.72rem;font-weight:700;letter-spacing:0.06em;
                       text-transform:uppercase;color:${SOL.base1};">Centroid relatedness vs. how much a city publishes</span>
          <span style="font-size:0.72rem;font-weight:700;color:${SOL.red};
                       border:1px solid ${SOL.red};border-radius:5px;padding:1px 7px;">✗ the measure we discard</span>
          <span style="font-size:0.72rem;color:${SOL.base00};">r = ${r.toFixed(2)} · 385 cities</span>
        </div>
        <div id="cen-plot" style="height:min(420px,46vh);min-height:280px;"></div>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;
                    padding:8px 4px 2px;">
          <label for="cen-slider" style="font-size:0.8rem;color:${SOL.base01};
                 font-weight:600;white-space:nowrap;">Keep cities publishing ≥</label>
          <input id="cen-slider" type="range" min="0" max="100" value="0"
                 style="flex:1 1 160px;accent-color:${HL};cursor:pointer;">
          <span id="cen-readout" style="font-size:0.82rem;color:${SOL.base01};
                min-width:270px;"></span>
        </div>
      </div>`;

    const plot = document.getElementById("cen-plot");
    const slider = document.getElementById("cen-slider");
    const readout = document.getElementById("cen-readout");

    // Static traces: trend line and the faint field-wide average line.
    const trendTrace = {
      x: xEnds, y: yEnds, mode: "lines", type: "scatter", hoverinfo: "skip",
      line: { color: SOL.orange, width: 2, dash: "solid" }, name: "trend",
    };
    const overallTrace = {
      x: xEnds, y: [overallMean, overallMean], mode: "lines", type: "scatter",
      hoverinfo: "skip", line: { color: SOL.base1, width: 1, dash: "dot" },
      name: "field average",
    };

    const layout = {
      margin: { l: 52, r: 12, t: 8, b: 42 },
      paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
      showlegend: false, hovermode: "closest",
      xaxis: {
        type: "log", title: { text: "Papers published (log scale)", font: { size: 12 } },
        gridcolor: SOL.base2, zeroline: false, tickfont: { size: 10 },
      },
      yaxis: {
        title: { text: "Centroid relatedness (cosine)", font: { size: 12 } },
        gridcolor: SOL.base2, zeroline: false, tickfont: { size: 10 },
      },
      font: { color: SOL.base01 },
    };

    let ready = false;
    function draw() {
      // Threshold is the slider mapped onto papers, log-spaced for fine control
      // among small cities where the action is.
      const t = +slider.value / 100;
      const threshold = Math.max(1, Math.round(Math.exp(t * Math.log(maxPapers))));
      const kept = cities.filter(c => c.papers >= threshold);
      const dropped = cities.filter(c => c.papers < threshold);
      const keptMean = kept.length ? mean(kept.map(c => c.overlap)) : overallMean;

      const dots = grp => ({
        x: grp.map(c => c.papers), y: grp.map(c => c.overlap),
        customdata: grp.map(c => [c.city, c.country, c.papers, c.projects]),
        mode: "markers", type: "scatter",
        marker: {
          size: grp.map(c => 5 + Math.sqrt(c.docs)),
          color: grp === dropped ? DIM : HL, opacity: grp === dropped ? 0.5 : 0.85,
          line: { width: 0 },
        },
        hovertemplate:
          "<b>%{customdata[0]}</b>, %{customdata[1]}<br>" +
          "%{customdata[2]} papers · %{customdata[3]} projects<br>" +
          "relatedness %{y:.3f}<extra></extra>",
      });

      // Moving line at the mean of the kept set — the number that climbs.
      const keptMeanTrace = {
        x: xEnds, y: [keptMean, keptMean], mode: "lines", type: "scatter",
        hoverinfo: "skip", line: { color: HL, width: 2 },
      };

      const traces = [overallTrace, trendTrace, keptMeanTrace, dots(dropped), dots(kept)];
      if (!ready) {
        Plotly.newPlot(plot, traces, layout, { responsive: true, displayModeBar: false });
        ready = true;
      } else {
        Plotly.react(plot, traces, layout);
      }

      readout.innerHTML =
        `<b style="color:${HL};">${kept.length}</b> of 385 cities · ` +
        `mean relatedness <b>${keptMean.toFixed(3)}</b>` +
        (threshold > 1 ? ` (≥ ${threshold} papers)` : ` (all cities)`);
    }

    slider.addEventListener("input", draw);
    draw();

    // Plotly draws at 0×0 inside a hidden reveal slide; re-fit when we scroll in.
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(es => {
        es.forEach(e => { if (e.isIntersecting && plot.data) Plotly.Plots.resize(plot); });
      }, { threshold: 0.05 }).observe(root);
    }
  }

  // ─── Small stats helpers ─────────────────────────────────────────────────────
  function mean(a) { return a.reduce((s, x) => s + x, 0) / a.length; }
  function leastSquares(xs, ys) {
    const n = xs.length, mx = mean(xs), my = mean(ys);
    let sxy = 0, sxx = 0;
    for (let i = 0; i < n; i++) { sxy += (xs[i] - mx) * (ys[i] - my); sxx += (xs[i] - mx) ** 2; }
    const b = sxy / sxx;
    return { a: my - b * mx, b };
  }
  function pearson(xs, ys) {
    const n = xs.length, mx = mean(xs), my = mean(ys);
    let sxy = 0, sx = 0, sy = 0;
    for (let i = 0; i < n; i++) {
      sxy += (xs[i] - mx) * (ys[i] - my);
      sx += (xs[i] - mx) ** 2; sy += (ys[i] - my) ** 2;
    }
    return sxy / Math.sqrt(sx * sy);
  }
}());
