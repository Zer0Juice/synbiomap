/**
 * alignment.js — the "90% closer to home" local-alignment scatter.
 *
 * Every dot is one iGEM project. We compare it, in SPECTER2 embedding space, to
 * the average paper of its OWN city and to the average paper of every OTHER city:
 *   • x = mean cosine similarity to other cities' papers,
 *   • y = cosine similarity to its own city's papers.
 * The dashed line is y = x — "no local advantage". A project ABOVE the line is
 * closer to its own city's papers than to a typical other city's. About 90% of
 * projects land above it: local alignment is real and strikingly consistent.
 *
 * This is the interactive twin of the manuscript's project_level_alignment.png
 * (see stage_embeddings in scripts/export_paper_assets.py for the identical math).
 * Two toggle views tell the same story: the own-vs-other scatter, and the
 * distribution of δ = own − other (90% of the mass is positive).
 *
 * Static-hosting friendly: reads one precomputed JSON, no server, no embeddings at
 * runtime. Palette: Solarized Light, matching centroid.js and the rest of the site.
 *
 * Data: assets/data/project_alignment.json
 *       [ {meta:true, n_projects, n_cities, frac_pos, mean_delta, min_city_papers},
 *         {title, city, country, year, own, other}, ... ]   (make_alignment_widget_data.py)
 */

(function () {
  const SOL = {
    base01: "#586e75", base00: "#657b83", base1: "#93a1a1",
    base2: "#eee8d5", base3: "#fdf6e3",
    orange: "#cb4b16", red: "#dc322f", blue: "#268bd2", green: "#859900",
  };
  const HOME = SOL.blue;    // projects closer to their own city (above the y = x line)
  const AWAY = SOL.orange;  // the minority closer to some other city (below the line)

  const root = document.getElementById("alignment-app");
  if (!root) return;
  root.innerHTML = `<p style="padding:1.5em;color:${SOL.base1};">Loading…</p>`;

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
    fetch("assets/data/project_alignment.json")
      .then(r => r.json())
      .then(init)
      .catch(err => {
        root.innerHTML =
          `<p style="padding:1.5em;color:#c00;font-family:monospace;">Data error: ${err}</p>`;
        console.error("alignment widget:", err);
      });
  });

  function init(rows) {
    // First element is a meta summary; the rest are one project each.
    const meta = rows[0] && rows[0].meta ? rows[0] : {};
    const projects = rows.filter(r => !r.meta);
    for (const p of projects) p.delta = p.own - p.other;

    const home = projects.filter(p => p.delta > 0);
    const away = projects.filter(p => p.delta <= 0);
    const fracPos = meta.frac_pos != null ? meta.frac_pos : home.length / projects.length;
    const pctHome = (fracPos * 100).toFixed(1);
    const nProj = meta.n_projects || projects.length;

    // Axis range shared by both x and y so the y = x line sits at a true 45°.
    const vals = projects.flatMap(p => [p.own, p.other]);
    const lo = Math.min(...vals), hi = Math.max(...vals);
    const pad = (hi - lo) * 0.04;
    const rng = [lo - pad, hi + pad];

    // ─── Shell ───────────────────────────────────────────────────────────────
    root.innerHTML = `
      <div style="font-family:inherit;">
        <div style="display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:2px;">
          <span style="font-size:0.72rem;font-weight:700;letter-spacing:0.06em;
                       text-transform:uppercase;color:${SOL.base1};">Each project vs. its own city's papers</span>
          <span style="font-size:0.72rem;font-weight:700;color:${HOME};
                       border:1px solid ${HOME};border-radius:5px;padding:1px 7px;">✓ ${pctHome}% closer to home</span>
        </div>
        <div id="al-plot" style="height:min(430px,48vh);min-height:280px;"></div>
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:8px 4px 2px;">
          <div id="al-toggle" style="display:inline-flex;border:1px solid ${SOL.base2};
               border-radius:6px;overflow:hidden;font-size:0.78rem;">
            <button data-view="scatter" style="border:0;padding:4px 12px;cursor:pointer;">Own vs. other</button>
            <button data-view="hist" style="border:0;padding:4px 12px;cursor:pointer;">Distribution of δ</button>
          </div>
          <span id="al-readout" style="font-size:0.82rem;color:${SOL.base01};"></span>
        </div>
      </div>`;

    const plot = document.getElementById("al-plot");
    const readout = document.getElementById("al-readout");
    const buttons = [...root.querySelectorAll("#al-toggle button")];

    const diag = {
      x: rng, y: rng, mode: "lines", type: "scatter", hoverinfo: "skip",
      line: { color: SOL.base1, width: 1.5, dash: "dash" }, showlegend: false,
    };

    function dots(grp, color, label) {
      return {
        x: grp.map(p => p.other), y: grp.map(p => p.own),
        customdata: grp.map(p => [p.title, p.city, p.country, p.year, p.delta]),
        mode: "markers", type: "scattergl", name: label,
        marker: { size: 5, color, opacity: 0.55, line: { width: 0 } },
        hovertemplate:
          "<b>%{customdata[0]}</b><br>%{customdata[1]}, %{customdata[2]} · %{customdata[3]}<br>" +
          "own %{y:.3f} · other %{x:.3f} · δ %{customdata[4]:+.3f}<extra></extra>",
      };
    }

    const scatterTraces = [
      diag,
      dots(away, AWAY, "closer to another city"),
      dots(home, HOME, "closer to home"),
    ];
    const scatterLayout = {
      margin: { l: 54, r: 12, t: 8, b: 44 },
      paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
      showlegend: false, hovermode: "closest",
      xaxis: { title: { text: "Similarity to other cities' papers", font: { size: 12 } },
               range: rng, gridcolor: SOL.base2, zeroline: false, tickfont: { size: 10 } },
      yaxis: { title: { text: "Similarity to own city's papers", font: { size: 12 } },
               range: rng, scaleanchor: "x", scaleratio: 1,
               gridcolor: SOL.base2, zeroline: false, tickfont: { size: 10 } },
      annotations: [{
        x: rng[0] + (rng[1] - rng[0]) * 0.72, y: rng[0] + (rng[1] - rng[0]) * 0.60,
        text: "y = x", showarrow: false, font: { size: 11, color: SOL.base1 },
      }],
      font: { color: SOL.base01 },
    };

    // δ histogram: the same result seen as a distribution — 90% of the mass is > 0.
    const deltas = projects.map(p => p.delta);
    const dMin = Math.min(...deltas), dMax = Math.max(...deltas);
    const bin = { start: dMin, end: dMax, size: (dMax - dMin) / 60 };
    const histTraces = [
      { x: away.map(p => p.delta), type: "histogram", name: "closer elsewhere",
        marker: { color: AWAY }, opacity: 0.85, xbins: bin, hoverinfo: "skip" },
      { x: home.map(p => p.delta), type: "histogram", name: "closer to home",
        marker: { color: HOME }, opacity: 0.85, xbins: bin, hoverinfo: "skip" },
    ];
    const histLayout = {
      margin: { l: 54, r: 12, t: 8, b: 44 }, barmode: "stack",
      paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)", showlegend: false,
      xaxis: { title: { text: "δ = similarity(own) − similarity(other)", font: { size: 12 } },
               gridcolor: SOL.base2, zeroline: false, tickfont: { size: 10 } },
      yaxis: { title: { text: "Projects", font: { size: 12 } },
               gridcolor: SOL.base2, zeroline: false, tickfont: { size: 10 } },
      shapes: [{ type: "line", x0: 0, x1: 0, yref: "paper", y0: 0, y1: 1,
                 line: { color: SOL.base01, width: 1.5, dash: "dash" } }],
      annotations: [{ x: 0, y: 1.02, yref: "paper", text: "δ = 0", showarrow: false,
                      font: { size: 11, color: SOL.base1 } }],
      font: { color: SOL.base01 },
    };

    let ready = false, view = "scatter";
    function draw() {
      const traces = view === "scatter" ? scatterTraces : histTraces;
      const layout = view === "scatter" ? scatterLayout : histLayout;
      if (!ready) {
        Plotly.newPlot(plot, traces, layout, { responsive: true, displayModeBar: false });
        ready = true;
      } else {
        Plotly.react(plot, traces, layout);
      }
      buttons.forEach(b => {
        const on = b.dataset.view === view;
        b.style.background = on ? HOME : SOL.base3;
        b.style.color = on ? "#fff" : SOL.base00;
        b.style.fontWeight = on ? "700" : "400";
      });
      readout.innerHTML =
        `<b style="color:${HOME};">${pctHome}%</b> of ${nProj.toLocaleString()} projects sit ` +
        (view === "scatter" ? "above the line" : "right of δ = 0") +
        ` — closer to their own city (mean δ ${(meta.mean_delta ?? 0) >= 0 ? "+" : ""}${(meta.mean_delta ?? 0).toFixed(4)})`;
    }

    buttons.forEach(b => b.addEventListener("click", () => { view = b.dataset.view; draw(); }));
    draw();

    // Plotly draws at 0×0 inside a hidden reveal slide; re-fit when we scroll in.
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(es => {
        es.forEach(e => { if (e.isIntersecting && plot.data) Plotly.Plots.resize(plot); });
      }, { threshold: 0.05 }).observe(root);
    }
  }
}());
