/**
 * topic_profile.js — a worked example of the topic-profiling relatedness measure.
 *
 * The centroid measure (previous slide) was a size artifact. The fix: stop averaging
 * embeddings and instead describe each city as a DISTRIBUTION over the 80 topic
 * clusters — one share-vector per artifact type. Relatedness between two types is the
 * cosine of their two share-vectors:
 *
 *     overlap = Σ_topics (project share) × (paper share) / (‖proj‖ ‖paper‖)
 *
 * high when the two types pile into the SAME topics, low when they scatter.
 *
 * This widget makes that concrete for one real city at a time. For the chosen city we
 * show its top topics by combined share as back-to-back bars — projects growing left,
 * papers growing right. A topic both types invest in is a two-sided "bowtie" and is
 * exactly what the cosine rewards; a one-sided spur contributes nothing. The printed
 * overlap is the true cosine over ALL 80 clusters, not just the ~10 shown (the rest are
 * near-zero and cropped only for legibility).
 *
 * It is a DEFINITION aid, not a result — the result (co-membership overlap across all
 * cities, with permutation p-values) is the next slide. Default city is a legible mid
 * example; the selector shows the method generalises.
 *
 * Static-hosting friendly: reads the same precomputed artifacts.json the explorer uses
 * (per-artifact city + topic-cluster name), computes the profiles in the browser. No
 * server, no embeddings at runtime. Palette: Solarized Light, matching the deck.
 *
 * Data: assets/data/artifacts.json  [{type, city, cluster_label, cluster_name}, ...]
 */

(function () {
  const SOL = {
    base01: "#586e75", base00: "#657b83", base1: "#93a1a1",
    base2: "#eee8d5", base3: "#fdf6e3",
    orange: "#cb4b16", blue: "#268bd2", cyan: "#2aa198",
  };
  const PROJ = SOL.cyan;   // projects (matches the deck's project colour)
  const PAPER = SOL.blue;  // papers   (matches the deck's paper colour)

  const DEFAULT_CITY = "Munich";
  const TOP_N = 10;        // topics shown per city (legibility); cosine uses all
  const MIN_EACH = 8;      // a city needs >= this many of each type to be selectable

  const root = document.getElementById("topic-profile-app");
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
    fetch("assets/data/artifacts.json")
      .then(r => r.json())
      .then(build)
      .catch(err => {
        root.innerHTML =
          `<p style="padding:1.5em;color:#c00;font-family:monospace;">Data error: ${err}</p>`;
        console.error("topic-profile widget:", err);
      });
  });

  function build(artifacts) {
    // Tally, per city and type, how many artifacts fall in each topic cluster.
    // Skip noise (cluster_label < 0) and patents — this slide's equation is paper×project.
    const counts = new Map();   // city -> { project: Map(topic->n), paper: Map(topic->n) }
    const totals = new Map();   // city -> { project: n, paper: n }
    for (const a of artifacts) {
      const t = a.type, city = a.city, topic = a.cluster_name;
      if ((t !== "project" && t !== "paper") || !city || topic == null) continue;
      if (a.cluster_label != null && a.cluster_label < 0) continue;
      if (!counts.has(city)) {
        counts.set(city, { project: new Map(), paper: new Map() });
        totals.set(city, { project: 0, paper: 0 });
      }
      const cm = counts.get(city)[t];
      cm.set(topic, (cm.get(topic) || 0) + 1);
      totals.get(city)[t] += 1;
    }

    // Turn a topic-count Map into a share Map (fractions summing to 1).
    const shares = (m, n) => {
      const s = new Map();
      for (const [k, v] of m) s.set(k, v / n);
      return s;
    };
    const cosine = (P, Q) => {
      let dot = 0, np = 0, nq = 0;
      const keys = new Set([...P.keys(), ...Q.keys()]);
      for (const k of keys) dot += (P.get(k) || 0) * (Q.get(k) || 0);
      for (const v of P.values()) np += v * v;
      for (const v of Q.values()) nq += v * v;
      return np && nq ? dot / Math.sqrt(np * nq) : 0;
    };

    // Eligible cities: enough of each type for a meaningful profile.
    const eligible = [];
    for (const [city, tot] of totals) {
      if (tot.project >= MIN_EACH && tot.paper >= MIN_EACH) {
        const P = shares(counts.get(city).project, tot.project);
        const Q = shares(counts.get(city).paper, tot.paper);
        eligible.push({ city, P, Q, np: tot.project, npap: tot.paper, cos: cosine(P, Q) });
      }
    }
    // Order the dropdown by total volume so big, recognisable cities are near the top.
    eligible.sort((a, b) => (b.np + b.npap) - (a.np + a.npap));
    const byCity = new Map(eligible.map(c => [c.city, c]));
    const start = byCity.has(DEFAULT_CITY) ? DEFAULT_CITY : eligible[0].city;

    // ─── Shell ───────────────────────────────────────────────────────────────
    root.innerHTML = `
      <div style="font-family:inherit;">
        <div style="display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:2px;">
          <span style="font-size:0.72rem;font-weight:700;letter-spacing:0.06em;
                       text-transform:uppercase;color:${SOL.base1};">A city as a distribution over topics</span>
          <label style="font-size:0.8rem;color:${SOL.base01};margin-left:auto;">City
            <select id="tp-city" style="font-size:0.8rem;padding:2px 6px;border:1px solid ${SOL.base2};
                    border-radius:5px;background:${SOL.base3};color:${SOL.base00};">
              ${eligible.map(c => `<option value="${c.city}"${c.city === start ? " selected" : ""}>${c.city}</option>`).join("")}
            </select>
          </label>
        </div>
        <div style="display:flex;align-items:center;gap:14px;font-size:0.78rem;color:${SOL.base00};margin:1px 0 2px;">
          <span><span style="display:inline-block;width:10px;height:10px;background:${PROJ};border-radius:2px;"></span> projects</span>
          <span><span style="display:inline-block;width:10px;height:10px;background:${PAPER};border-radius:2px;"></span> papers</span>
          <span id="tp-badge" style="margin-left:auto;font-weight:700;color:${SOL.base01};"></span>
        </div>
        <div id="tp-plot" style="height:min(400px,44vh);min-height:260px;"></div>
        <div id="tp-note" style="font-size:0.62rem;color:${SOL.base1};padding:2px 4px 0;line-height:1.35;"></div>
      </div>`;

    const plot = document.getElementById("tp-plot");
    const badge = document.getElementById("tp-badge");
    const note = document.getElementById("tp-note");
    const select = document.getElementById("tp-city");

    const short = (s, n = 30) => (s.length <= n ? s : s.slice(0, n - 1) + "…");

    function draw(cityName) {
      const c = byCity.get(cityName);
      // Top topics by combined project+paper share.
      const keys = new Set([...c.P.keys(), ...c.Q.keys()]);
      const topics = [...keys]
        .map(k => ({ k, p: c.P.get(k) || 0, q: c.Q.get(k) || 0 }))
        .sort((a, b) => (b.p + b.q) - (a.p + a.q))
        .slice(0, TOP_N)
        .reverse();  // Plotly draws first item at the bottom; we want biggest on top

      const labels = topics.map(t => short(t.k));
      const shared = topics.map(t => t.p > 0 && t.q > 0);
      const nShared = shared.filter(Boolean).length;
      // Shared topics at full strength; one-sided spurs dimmed so bowties pop.
      const rgba = (hex, on) => on
        ? hex
        : hex + "80";  // ~50% alpha via 8-digit hex

      const projTrace = {
        y: labels, x: topics.map(t => -t.p * 100), orientation: "h", type: "bar",
        marker: { color: shared.map(s => rgba(PROJ, s)) },
        customdata: topics.map(t => [t.k, t.p * 100]),
        hovertemplate: "%{customdata[0]}<br>projects %{customdata[1]:.0f}%<extra></extra>",
      };
      const paperTrace = {
        y: labels, x: topics.map(t => t.q * 100), orientation: "h", type: "bar",
        marker: { color: shared.map(s => rgba(PAPER, s)) },
        customdata: topics.map(t => [t.k, t.q * 100]),
        hovertemplate: "%{customdata[0]}<br>papers %{customdata[1]:.0f}%<extra></extra>",
      };

      const maxv = Math.max(...topics.map(t => Math.max(t.p, t.q))) * 100;
      const layout = {
        margin: { l: 8, r: 8, t: 6, b: 34 },
        barmode: "overlay", bargap: 0.35,
        paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
        showlegend: false, hovermode: "closest",
        xaxis: {
          title: { text: "← share of projects   ·   share of papers →", font: { size: 11 } },
          range: [-maxv * 1.05, maxv * 1.05], zeroline: true, zerolinecolor: SOL.base1,
          zerolinewidth: 1, gridcolor: SOL.base2,
          tickvals: [-maxv, -maxv / 2, 0, maxv / 2, maxv].map(v => Math.round(v)),
          ticktext: [maxv, maxv / 2, 0, maxv / 2, maxv].map(v => Math.round(v) + "%"),
          tickfont: { size: 9 },
        },
        yaxis: { showticklabels: false, showgrid: false, zeroline: false },
        // Topic names centred on the zero line, sitting in the empty gutter between the bars.
        annotations: topics.map((t, i) => ({
          x: 0, y: labels[i], text: short(t.k), showarrow: false,
          font: { size: 10, color: shared[i] ? SOL.base01 : SOL.base1 },
          bgcolor: "rgba(253,246,227,0.82)", borderpad: 1,
        })),
        font: { color: SOL.base01 },
      };

      Plotly.react(plot, [projTrace, paperTrace], layout, { responsive: true, displayModeBar: false });

      badge.textContent = `topic-profile overlap (cosine) = ${c.cos.toFixed(3)}`;
      note.innerHTML =
        `${cityName}: ${c.np} projects, ${c.npap} papers. Showing the top ${topics.length} of ` +
        `80 topics by combined share (${nShared} shared by both types, at full colour). ` +
        `The overlap is the cosine of the two full 80-topic profiles.`;
    }

    Plotly.newPlot(plot, [], { margin: { t: 0 } }, { displayModeBar: false }).then(() => draw(start));
    select.addEventListener("change", e => draw(e.target.value));

    // Plotly draws at 0×0 inside a hidden reveal slide; re-fit when we scroll in.
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(es => {
        es.forEach(e => { if (e.isIntersecting && plot.data) Plotly.Plots.resize(plot); });
      }, { threshold: 0.05 }).observe(root);
    }
  }
}());
