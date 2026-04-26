// Shared helpers used across the dashboard, map and explore pages.
// Loaded after data.js, so window.NOMAD_DATA is available.

(function () {
  const data = window.NOMAD_DATA || [];

  const fmt = {
    int: (v) => (v == null ? "—" : Math.round(v).toLocaleString("en-US")),
    num: (v, d = 1) => (v == null ? "—" : Number(v).toFixed(d)),
    gdp: (v) => (v == null ? "—" : v >= 1000 ? (v / 1000).toFixed(1) + "k 亿" : v.toFixed(1) + " 亿"),
    pop: (v) => (v == null ? "—" : v >= 1000 ? (v / 100).toFixed(1) + "k 万" : v.toFixed(1) + " 万"),
    income: (v) => (v == null ? "—" : v.toLocaleString("en-US") + " 元"),
    pct: (v) => (v == null ? "—" : v.toFixed(1) + "%"),
    yn: (v) => (v == null ? "—" : v ? "✓" : "·"),
    bool: (v) => (v == null ? "" : v ? "yes" : "no"),
  };

  function buildNav(active) {
    const tabs = [
      { id: "index", href: "index.html", label: "Dashboard" },
      { id: "map", href: "map.html", label: "Map" },
      { id: "explore", href: "explore.html", label: "Explore" },
    ];
    const html = `
      <nav class="nav">
        <div class="brand">中国小县城<span class="dot">·</span>Nomad Atlas</div>
        ${tabs
          .map(
            (t) =>
              `<a class="tab ${t.id === active ? "active" : ""}" href="${t.href}">${t.label}</a>`
          )
          .join("")}
        <div class="spacer"></div>
        <div class="meta">${data.length.toLocaleString()} 条记录</div>
      </nav>`;
    document.body.insertAdjacentHTML("afterbegin", html);
  }

  // Diverging color scale for coloring map markers / scatter points by metric.
  // Returns an interpolator (0..1 -> hex color).
  function makeColorScale(stops) {
    return function (t) {
      t = Math.max(0, Math.min(1, t));
      for (let i = 0; i < stops.length - 1; i++) {
        const a = stops[i], b = stops[i + 1];
        if (t >= a.t && t <= b.t) {
          const k = (t - a.t) / (b.t - a.t);
          const r = Math.round(a.r + (b.r - a.r) * k);
          const g = Math.round(a.g + (b.g - a.g) * k);
          const bl = Math.round(a.b + (b.b - a.b) * k);
          return `rgb(${r},${g},${bl})`;
        }
      }
      return "#888";
    };
  }
  // viridis-ish (cold->warm)
  const viridis = makeColorScale([
    { t: 0, r: 68, g: 1, b: 84 },
    { t: 0.25, r: 59, g: 82, b: 139 },
    { t: 0.5, r: 33, g: 145, b: 140 },
    { t: 0.75, r: 94, g: 201, b: 98 },
    { t: 1, r: 253, g: 231, b: 37 },
  ]);
  // Cool→warm (for temperature)
  const coolwarm = makeColorScale([
    { t: 0, r: 59, g: 76, b: 192 },
    { t: 0.5, r: 221, g: 221, b: 221 },
    { t: 1, r: 180, g: 4, b: 38 },
  ]);

  function quantileScale(values) {
    const arr = values.filter((v) => v != null && !Number.isNaN(v)).sort((a, b) => a - b);
    if (arr.length === 0) return { lo: 0, hi: 1 };
    // Use 5–95 percentile so a couple of outliers don't flatten the gradient.
    const lo = arr[Math.floor(arr.length * 0.05)];
    const hi = arr[Math.floor(arr.length * 0.95)];
    return { lo, hi: hi === lo ? lo + 1 : hi };
  }

  // Province palette — recycled but stable.
  const PROVINCE_COLORS = [
    "#5470C6", "#91CC75", "#FAC858", "#EE6666", "#73C0DE",
    "#3BA272", "#FC8452", "#9A60B4", "#EA7CCC", "#5B8FF9",
    "#5AD8A6", "#5D7092", "#F6BD16", "#E8684A", "#6DC8EC",
    "#9270CA", "#FF9D4D", "#269A99", "#FF99C3", "#FFD86E",
  ];
  const provinceColor = (() => {
    const map = new Map();
    let i = 0;
    return (p) => {
      if (!map.has(p)) {
        map.set(p, PROVINCE_COLORS[i % PROVINCE_COLORS.length]);
        i++;
      }
      return map.get(p);
    };
  })();

  window.NOMAD = {
    data,
    fmt,
    buildNav,
    viridis,
    coolwarm,
    quantileScale,
    provinceColor,
  };
})();
