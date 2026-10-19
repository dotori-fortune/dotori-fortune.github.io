import base64, sys
from playwright.sync_api import sync_playwright
JS = r"""async () => {
  await Promise.all(["88px Galmuri11", "104px Galmuri14", "66px Galmuri11", "34px Galmuri11"].map(f => document.fonts.load(f)));
  const css = getComputedStyle(acorn), v = n => css.getPropertyValue(n).trim();
  const W = 1200, H = 630, c = 12, U = 8, B = 6, SCENE_LIFT = 40;
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

  // 아래에 게이지를 둘 자리를 내려고 장면을 위로 올린다.
  g.save(); g.translate(0, -SCENE_LIFT);
  // 바닥
  const cols = 96, rows = 8, gx = (W - cols * U) / 2, gy = 470, ggy = 498;
  for (let r = 0; r < rows; r++) {
    const dy = (r + 0.5) / rows * 2 - 1, half = Math.round(cols / 2 * Math.sqrt(1 - dy * dy)), x0 = gx + (cols / 2 - half) * U;
    rect(x0 - U, ggy + r * U, (half * 2 + 2) * U, U, v("--ground-edge"));
    rect(x0, ggy + r * U, half * 2 * U, U, v(r < 2 ? "--ground-light" : r < 6 ? "--ground" : "--ground-dark"));
  }

  // 게임의 BURST 와 같은 모양으로, 한 프레임을 골라 멈춘 그림으로 찍는다.
  const gameBurst = (kind, frame, x0, y0, u) => {
    const { dirs, core } = BURST[kind], [gap, len] = BURST[kind].frames[frame], o = Math.max(2, Math.round(u / 3));
    const cells = [];
    for (let y = 0; y < core; y++) for (let x = 0; x < core; x++)
      if ((x !== 0 && x !== core - 1) || (y !== 0 && y !== core - 1) || core < 3) cells.push([x - (core - 1) / 2, y - (core - 1) / 2, "--slip-paper"]);
    dirs.forEach(([dx, dy]) => {
      const n = dx && dy ? Math.ceil(len * 0.7) : len;
      for (let i = 0; i < n; i++) cells.push([dx * (gap + i), dy * (gap + i), i === n - 1 ? "--acorn-light" : "--acorn-hi"]);
    });
    const at = t => t * u - u / 2;
    cells.forEach(([x, y]) => rect(x0 + at(x) - o, y0 + at(y) - o, u + 2 * o, u + 2 * o, v("--outline")));
    cells.forEach(([x, y, col]) => rect(x0 + at(x), y0 + at(y), u, u, v(col)));
  };
  const cx = W / 2, cy = 366;
  gameBurst("final", 2, cx, cy + 10, 12);

  // 쪽지
  const SW = 120, F = stripFrame(SW), S = sealSize(SW), lineH = 64, pad = 22;
  const sh = stripHeight(SW, 0, 2, lineH, pad);
  const sx = cx - SW / 2, sy = gy - sh + 40;
  rect(sx - B, sy - B, SW + 2 * B, sh + B, v("--outline"));
  rect(sx, sy, SW, sh, v("--slip-paper"));
  rect(sx + F, sy + F, SW - 2 * F, sh - 2 * F, v("--slip-line"));
  rect(sx + F + B, sy + F + B, SW - 2 * F - 2 * B, sh - 2 * F - 2 * B, v("--slip-paper"));
  let ty = sy + F + B + pad;
  // 점괘는 깨 봐야 아는 것이라 썸네일에서는 감춘다.
  ty += 2 * lineH + pad / 2;
  // 글자 상자가 아니라 실제 잉크 상자 기준으로 종이 위쪽과 도장 사이 한가운데에 둔다.
  g.font = "110px Galmuri11"; g.textAlign = "left"; g.textBaseline = "alphabetic";
  const qm = g.measureText("?"), qw = qm.actualBoundingBoxRight - qm.actualBoundingBoxLeft, qh = qm.actualBoundingBoxAscent + qm.actualBoundingBoxDescent;
  const qTop = sy + F + B, qMid = (qTop + ty) / 2;
  g.fillStyle = v("--slip-ink");
  g.fillText("?", Math.round(cx - qw / 2 + qm.actualBoundingBoxLeft), Math.round(qMid - qh / 2 + qm.actualBoundingBoxAscent));
  const su = S / SEAL.length, ssx = cx - S / 2;
  SEAL.forEach((row, ry) => [...row].forEach((ch, rx) => { if (ch === "R") rect(ssx + rx * su, ty + ry * su, su, su, v("--seal")); }));

  // 쪼개진 반쪽: 맞은 순간 서로 다른 각도와 높이로 튕겨 나간다.
  // 캔버스로 돌리면 도트가 번져서 칸 단위로 돌린 뒤 키운다.
  const rotGrid = (grid, deg) => {
    const h = grid.length, w = grid[0].length, a = deg * Math.PI / 180, ca = Math.cos(a), sa = Math.sin(a);
    const n = Math.ceil(Math.hypot(w, h)) + 2, out = [];
    for (let y = 0; y < n; y++) { const row = []; for (let x = 0; x < n; x++) {
      const dx = x + 0.5 - n / 2, dy = y + 0.5 - n / 2;
      const sx = Math.floor(ca * dx + sa * dy + w / 2), sy = Math.floor(-sa * dx + ca * dy + h / 2);
      row.push(sy >= 0 && sy < h && sx >= 0 && sx < w ? grid[sy][sx] : null);
    } out.push(row); }
    // 돌리면서 생긴 구멍을 메우고, 가장자리를 다시 테두리 색으로 칠해 윤곽을 잇는다.
    const at = (x, y) => out[y]?.[x] ?? null, N4 = [[1,0],[-1,0],[0,1],[0,-1]];
    const filled = out.map((row, y) => row.map((k, x) => k ?? (N4.filter(([dx, dy]) => at(x + dx, y + dy)).length >= 3 ? "O" : null)));
    return filled.map((row, y) => row.map((k, x) => k && N4.some(([dx, dy]) => !(filled[y + dy]?.[x + dx])) ? "O" : k));
  };
  const drawGrid = (grid, ox, oy) => grid.forEach((row, y) => row.forEach((k, x) => { if (k) rect(ox + x * c, oy + y * c, c, c, v(COLORS[k])); }));
  const flying = (grid, deg, mx, my) => { const r = rotGrid(grid, deg); drawGrid(r, mx - r[0].length * c / 2, my - r.length * c / 2); };
  // 바닥 그림자로 공중에 떠 있음을 보인다.
  const shadowAt = (x, w) => rect(x - w / 2, ggy + 10, w, 12, v("--shadow"));
  shadowAt(cx - 240, 130); shadowAt(cx + 245, 104);
  flying(HALF_LEFT, -38, cx - 245, 360);
  flying(HALF_RIGHT, 72, cx + 250, 372);
  // 껍질 파편과 흩날리는 궤적
  const SHARDS = [[-150, 264, "--acorn", 2], [-330, 254, "--cap", 2], [-120, 464, "--acorn-light", 1], [170, 284, "--acorn-dark", 2],
    [350, 334, "--cap-dark", 2], [140, 484, "--acorn", 1], [-380, 414, "--acorn-dark", 1], [395, 474, "--acorn-light", 1]];
  SHARDS.forEach(([dx, y, col, n]) => {
    rect(cx + dx, y, n * 8, n * 8, v("--outline"));
    rect(cx + dx + 2, y + 2, n * 8 - 4, n * 8 - 4, v(col));
    const sx = dx < 0 ? 1 : -1;
    for (let i = 1; i <= 3; i++) rect(cx + dx + sx * (n * 8 + i * 12), y + n * 4 - 2 + (i % 2) * 2, 6, 4, v("--sky-deco"));
  });

  // 반짝이
  const SPARK = [".X.", "XXX", ".X."];
  [[cx - 190, 274], [cx + 180, 244], [cx - 130, 214], [cx + 230, 364], [cx - 250, 394]].forEach(([x, y]) => sprite(SPARK, x, y, 8, v("--acorn-hi")));
  g.restore();

  // 게이지: 커서가 진한 칸 한가운데에 꽂힌 순간
  const GW = 480, GH = 32, gX = cx - GW / 2, gY = 506, HIT = 0.64;
  rect(gX - B, gY, GW + 2 * B, GH, v("--outline")); rect(gX, gY - B, GW, GH + 2 * B, v("--outline"));
  rect(gX + B, gY + GH + B, GW, B, v("--drop")); rect(gX + GW + B, gY + B, B, GH, v("--drop"));
  rect(gX, gY, GW, GH, v("--paper"));
  const zone = (r, col) => rect(Math.round(gX + (HIT - r / 2) * GW), gY, Math.round(r * GW), GH, col);
  zone(ZONE.good, v("--ground-light")); zone(ZONE.perfect, v("--acorn"));
  const curX = Math.round(gX + HIT * GW) - 5;
  rect(curX, gY - 12, 10, GH + 24, v("--outline"));
  gameBurst("perfect", 2, curX + 5, gY + GH / 2, 6);

  // 떨어지는 잎
  [[110, 120, "--acorn-light"], [1050, 90, "--cap-light"], [210, 330, "--cap-light"], [990, 300, "--acorn-light"], [160, 470, "--ground-light"]]
    .forEach(([x, y, col], i) => sprite(LEAF, x, y, 8, v(col), i % 2));

  // 제목: 원래 크기로 찍은 글자를 한 칸 두껍게 만든 뒤 정수 배로 키워 도트를 살린다.
  const LOGO_FONT = "bold 11px Galmuri11";
  await document.fonts.load(LOGO_FONT);
  const logo = (str, cxp, top, k, font = LOGO_FONT) => {
    const o = document.createElement("canvas"), og = o.getContext("2d");
    og.font = font; og.letterSpacing = "1px";
    const tw = Math.ceil(og.measureText(str).width) + 6, th = 17;
    o.width = tw; o.height = th;
    og.font = font; og.letterSpacing = "1px"; og.textBaseline = "top"; og.fillStyle = "#000"; og.fillText(str, 3, 3);
    const a = og.getImageData(0, 0, tw, th).data, on = (x, y) => x >= 0 && y >= 0 && x < tw && y < th && a[(y * tw + x) * 4 + 3] > 110;
    const fill = on;
    const edge = (x, y) => !fill(x, y) && [[1,0],[-1,0],[0,1],[0,-1],[1,1],[-1,-1],[1,-1],[-1,1]].some(([dx, dy]) => fill(x + dx, y + dy));
    const ox = Math.round(cxp - tw * k / 2);
    const px = (x, y, col, d = 0) => rect(ox + (x + d) * k, top + (y + d) * k, k, k, col);
    for (let y = 0; y < th; y++) for (let x = 0; x < tw; x++) if (fill(x, y) || edge(x, y)) px(x, y, v("--outline"), 1);
    for (let y = 0; y < th; y++) for (let x = 0; x < tw; x++) {
      if (edge(x, y)) px(x, y, v("--outline"));
      else if (fill(x, y)) px(x, y, v("--acorn"));
    }
  };
  logo("도토리 점괘", cx, 50, 7);
  // 11px 글꼴의 정수 배(66px)로 찍어야 도트가 번지지 않는다.

  return cv.toDataURL("image/png");
}"""
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome"); pg = b.new_page(color_scheme="light")
    pg.goto("file:///" + __import__("os").path.abspath(__import__("os").path.join(__import__("os").path.dirname(__file__), "..", "index.html")).replace("\\", "/") + "#reset"); pg.wait_for_timeout(800)
    pg.evaluate("() => { acornType = ACORN_TYPES[1]; acorn.className = 'acorn plain'; }")
    d = pg.evaluate(JS)
    open(sys.argv[1], "wb").write(base64.b64decode(d.split(",")[1]))
    b.close()
