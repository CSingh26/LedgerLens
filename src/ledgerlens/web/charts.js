"use strict";
window.LedgerCharts = (() => {
  const ns = "http://www.w3.org/2000/svg";
  function el(tag, attributes = {}, text) {
    const e = document.createElementNS(ns, tag);
    Object.entries(attributes).forEach(([k, v]) =>
      e.setAttribute(k, String(v)),
    );
    if (text !== undefined) e.textContent = text;
    return e;
  }
  const amount = (v) =>
    `USD ${(v / 1e6).toLocaleString(undefined, { maximumFractionDigits: 2 })}m`;
  function frame(name, min, max) {
    const svg = el("svg", {
      viewBox: "0 0 720 260",
      role: "img",
      "aria-label": name,
    });
    const range = Math.max(max - min, 1),
      y = (v) => 210 - ((v - min) / range) * 170;
    svg.append(
      el(
        "text",
        { x: 55, y: 15, fill: "#627176", "font-size": 11 },
        "USD millions",
      ),
    );
    for (let i = 0; i <= 4; i++) {
      const v = min + (range * i) / 4,
        pos = y(v);
      svg.append(
        el("line", { x1: 55, x2: 700, y1: pos, y2: pos, stroke: "#e2e8e0" }),
        el(
          "text",
          {
            x: 45,
            y: pos + 4,
            "text-anchor": "end",
            fill: "#627176",
            "font-size": 10,
          },
          (v / 1e6).toLocaleString(undefined, { maximumFractionDigits: 1 }),
        ),
      );
    }
    return { svg, y };
  }
  function history(periods) {
    const rows = periods.slice().reverse(),
      get = (p, n) => p.facts[n]?.value ?? null;
    const values = rows
      .flatMap((p) => [get(p, "revenue"), get(p, "cfo")])
      .filter((v) => v !== null);
    if (!values.length) return null;
    const min = Math.min(0, ...values),
      max = Math.max(1, ...values) * 1.1,
      { svg, y } = frame(
        "Revenue and operating cash flow by fiscal period",
        min,
        max,
      );
    const step = 620 / rows.length;
    rows.forEach((p, i) => {
      [
        ["revenue", "#183d4a"],
        ["cfo", "#57a088"],
      ].forEach(([name, color], j) => {
        const v = get(p, name);
        if (v === null) return;
        const x = 70 + i * step + j * 32,
          rect = el("rect", {
            x,
            y: Math.min(y(0), y(v)),
            width: 27,
            height: Math.max(1, Math.abs(y(v) - y(0))),
            fill: color,
            rx: 2,
          });
        rect.append(el("title", {}, `${p.end} ${name}: ${amount(v)}`));
        svg.append(rect);
      });
      svg.append(
        el(
          "text",
          {
            x: 100 + i * step,
            y: 236,
            "text-anchor": "middle",
            fill: "#627176",
            "font-size": 11,
          },
          p.end,
        ),
      );
    });
    return svg;
  }
  function cash(bridge) {
    const required = ["opening", "cfo", "cfi", "cff", "fx", "closing"];
    if (required.some((k) => bridge[k] === null)) return null;
    const bars = [];
    let running = bridge.opening;
    bars.push({
      name: "Opening",
      start: 0,
      end: running,
      value: running,
      absolute: true,
    });
    for (const key of ["cfo", "cfi", "cff", "fx"]) {
      const next = running + bridge[key];
      bars.push({
        name: key.toUpperCase(),
        start: running,
        end: next,
        value: bridge[key],
      });
      running = next;
    }
    bars.push({
      name: "Closing",
      start: 0,
      end: bridge.closing,
      value: bridge.closing,
      absolute: true,
    });
    const extremes = bars.flatMap((b) => [b.start, b.end]),
      { svg, y } = frame(
        "Opening to closing cash reconciliation",
        Math.min(0, ...extremes),
        Math.max(1, ...extremes) * 1.12,
      );
    bars.forEach((b, i) => {
      const x = 75 + i * 98,
        rect = el("rect", {
          x,
          y: Math.min(y(b.start), y(b.end)),
          width: 46,
          height: Math.max(2, Math.abs(y(b.start) - y(b.end))),
          fill: b.absolute ? "#183d4a" : b.value >= 0 ? "#57a088" : "#b9755a",
          rx: 2,
        });
      rect.append(el("title", {}, `${b.name}: ${amount(b.value)}`));
      svg.append(
        rect,
        el(
          "text",
          {
            x: x + 23,
            y: 236,
            "text-anchor": "middle",
            fill: "#627176",
            "font-size": 11,
          },
          b.name,
        ),
      );
      if (i < bars.length - 1)
        svg.append(
          el("line", {
            x1: x + 46,
            x2: x + 98,
            y1: y(b.end),
            y2: y(b.end),
            stroke: "#a5b9ad",
            "stroke-dasharray": "3 3",
          }),
        );
    });
    return svg;
  }
  return { history, cash };
})();
