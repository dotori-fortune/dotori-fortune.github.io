import base64, sys
from playwright.sync_api import sync_playwright
JS = r"""async () => {
  await Promise.all(["104px Galmuri14", "66px Galmuri11", "34px Galmuri11"].map(f => document.fonts.load(f)));
  const css = getComputedStyle(acorn), v = n => css.getPropertyValue(n).trim();
  const W = 1200, H = 630, c = 14, U = 8, B = 6;
  const cv = Object.assign(document.createElement("canvas"), { width: W, height: H });
  const g = cv.getContext("2d"); g.imageSmoothingEnabled = false;
  const rnd = seeded(7);
  const rect = (x, y, w, h, col) => { g.fillStyle = col; g.fillRect(x, y, w, h); };
  const sprite = (art, x, y, u, col, flip) => art.forEach((row, ry) => [...row].forEach((ch, rx) => {
    if (ch === "X") rect(x + (flip ? row.length - 1 - rx : rx) * u, y + ry * u, u, u, col); }));
  const text = (s, x, y, font, col) => { g.font = font; g.fillStyle = col; g.textAlign = "center"; g.textBaseline = "top"; g.fillText(s, x, y); };

  rect(0, 0, W, H, v("--bg"));
  // 흩어진 무늬
  const decos = [LEAF, SPRIG, PEBBLES];
  for (let i = 0; i < 46; i++) sprite(decos[i % 3], Math.round(rnd() * W / 6) * 6, Math.round(rnd() * H * 0.8 / 6) * 6, 6, v("--bg-deco"), rnd() < .5);
  // 숲 능선 두 겹
  const ridge = (col, minR, maxR, lift, cell) => {
    const cols = Math.ceil(W / cell), tops = new Array(cols).fill(0);
    for (let x = -maxR; x < cols + maxR; x += Math.round((minR + rnd() * (maxR - minR)) * 0.9)) {
      const r = Math.round(minR + rnd() * (maxR - minR));
      for (let dx = -r; dx <= r; dx++) { const k = x + dx; if (k >= 0 && k < cols) tops[k] = Math.max(tops[k], Math.round(Math.sqrt(r * r - dx * dx)) + lift); }
    }
    tops.forEach((t, k) => rect(k * cell, H - t * cell, cell, t * cell, col));
  };
  ridge(v("--wood-far"), 6, 11, 9, 10);
  ridge(v("--wood-near"), 4, 8, 4, 10);

  // 바닥
  const cols = 96, rows = 10, gx = (W - cols * U) / 2, gy = 470, ggy = 498;
  for (let r = 0; r < rows; r++) {
    const dy = (r + 0.5) / rows * 2 - 1, half = Math.round(cols / 2 * Math.sqrt(1 - dy * dy)), x0 = gx + (cols / 2 - half) * U;
    rect(x0 - U, ggy + r * U, (half * 2 + 2) * U, U, v("--ground-edge"));
    rect(x0, ggy + r * U, half * 2 * U, U, v(r < 2 ? "--ground-light" : r < 6 ? "--ground" : "--ground-dark"));
  }

  // 빛살: 쪽지 가운데에서 여덟 방향으로 끊어지는 도트 줄
  const cx = W / 2, cy = 330, u = 10;
  [[1,0],[-1,0],[0,-1],[1,-1],[-1,-1],[1,1],[-1,1]].forEach(([dx, dy]) => {
    for (let s = 8; s < 17; s++) { if (s % 4 === 3) continue; rect(cx + dx * s * u - u / 2, cy + dy * s * u - u / 2, u, u, v("--sky-deco")); }
  });

  // 쪽지
  const SW = 120, F = stripFrame(SW), S = sealSize(SW), lineH = 80, pad = 22;
  const sh = stripHeight(SW, 0, 2, lineH, pad);
  const sx = cx - SW / 2, sy = gy - sh + 40;
  rect(sx - B, sy - B, SW + 2 * B, sh + B, v("--outline"));
  rect(sx, sy, SW, sh, v("--slip-paper"));
  rect(sx + F, sy + F, SW - 2 * F, sh - 2 * F, v("--slip-line"));
  rect(sx + F + B, sy + F + B, SW - 2 * F - 2 * B, sh - 2 * F - 2 * B, v("--slip-paper"));
  let ty = sy + F + B + pad;
  ["대", "길"].forEach((ch, i) => text(ch, cx, ty + i * lineH, "66px Galmuri11", v("--slip-ink")));
  ty += 2 * lineH + pad / 2;
  const su = S / SEAL.length, ssx = cx - S / 2;
  SEAL.forEach((row, ry) => [...row].forEach((ch, rx) => { if (ch === "R") rect(ssx + rx * su, ty + ry * su, su, su, v("--seal")); }));

  // 쪼개진 반쪽: 쪽지 양옆에 눕힌다
  const drawGrid = (grid, ox, oy) => grid.forEach((row, y) => row.forEach((k, x) => { if (k) rect(ox + x * c, oy + y * c, c, c, v(COLORS[k])); }));
  const L = cx - GRID_W / 2 * c, PY = gy + 12 - (GRID_W / 2) * c + PIVOT_Y * c - 4 * c;
  const SPREAD = 9;
  g.save(); g.translate(L + (PIVOT_L - SPREAD) * c, gy + 2 * c); g.rotate(-Math.PI / 2); drawGrid(HALF_LEFT, -PIVOT_L * c, -PIVOT_Y * c); g.restore();
  g.save(); g.translate(L + (PIVOT_R + SPREAD) * c, gy + 2 * c); g.rotate(Math.PI / 2); drawGrid(HALF_RIGHT, -PIVOT_R * c, -PIVOT_Y * c); g.restore();

  // 반짝이
  const SPARK = [".X.", "XXX", ".X."];
  [[cx - 190, 240], [cx + 180, 210], [cx - 120, 150], [cx + 230, 330], [cx - 250, 360]].forEach(([x, y]) => sprite(SPARK, x, y, 8, v("--acorn-hi")));
  // 떨어지는 잎
  [[110, 120, "--acorn-light"], [1050, 90, "--cap-light"], [210, 330, "--cap-light"], [990, 300, "--acorn-light"], [1110, 420, "--ground-light"]]
    .forEach(([x, y, col], i) => sprite(LEAF, x, y, 8, v(col), i % 2));

  // 제목
  text("도토리 점괘", cx + 7, 40 + 7, "104px Galmuri14", v("--outline"));
  text("도토리 점괘", cx, 40, "104px Galmuri14", v("--acorn"));
  return cv.toDataURL("image/png");
}"""
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome"); pg = b.new_page(color_scheme="light")
    pg.goto("file:///" + __import__("os").path.abspath(__import__("os").path.join(__import__("os").path.dirname(__file__), "..", "index.html")).replace("\\", "/") + "#reset"); pg.wait_for_timeout(800)
    pg.evaluate("() => { acornType = ACORN_TYPES[1]; acorn.className = 'acorn plain'; }")
    d = pg.evaluate(JS)
    open(sys.argv[1], "wb").write(base64.b64decode(d.split(",")[1]))
    b.close()
