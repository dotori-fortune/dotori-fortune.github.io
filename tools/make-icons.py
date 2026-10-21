"""홈 화면 아이콘을 index.html 의 도토리 스프라이트로 그려 저장소 맨 위에 쓴다.

실행: 저장소 맨 위에서 python tools/make-icons.py
"""
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
# 파일 이름, 한 변, 칸 크기. 칸 크기를 정수로 둬야 픽셀이 번지지 않는다.
# maskable 은 기기가 원으로 잘라도 도토리가 남게 한 칸 작게 그린다.
ICONS = [("apple-touch-icon.png", 180, 5), ("icon-192.png", 192, 5), ("icon-512.png", 512, 13), ("icon-maskable-512.png", 512, 12)]
# 쪼개진 두 반쪽을 벌리는 칸 수와 왼쪽 반쪽을 들어 올리는 칸 수
GAP, LIFT = 2, 1
JS = r"""([size, u, gap, lift]) => {
  const css = getComputedStyle(document.documentElement), v = n => css.getPropertyValue(n).trim();
  const cv = Object.assign(document.createElement("canvas"), { width: size, height: size });
  const g = cv.getContext("2d"), c = size / 2;
  // 사이트 팔레트 색만 쓴다. 별·금색은 황금 도토리 연출이라 넣지 않는다.
  const bg = g.createRadialGradient(c, c, 0, c, c, size * 0.75);
  bg.addColorStop(0, v("--ground-light")); bg.addColorStop(1, v("--ground-edge"));
  g.fillStyle = bg; g.fillRect(0, 0, size, size);
  g.globalAlpha = 0.35; g.fillStyle = v("--grass");
  for (let i = 0; i < 12; i++) {
    const a = i * Math.PI / 6, w = Math.PI / 12 / 1.4;
    g.beginPath(); g.moveTo(c, c); g.arc(c, c, size, a - w, a + w); g.closePath(); g.fill();
  }
  g.globalAlpha = 1;
  const parts = [[HALF_LEFT, -gap, -lift], [HALF_RIGHT, gap, 0]];
  // 격자의 빈칸을 빼고 실제로 칠한 칸의 상자를 한가운데에 둔다.
  let x1 = 1e9, x2 = -1e9, y1 = 1e9, y2 = -1e9;
  parts.forEach(([grid, dx, dy]) => grid.forEach((row, y) => row.forEach((cc, x) => {
    if (cc) { x1 = Math.min(x1, x + dx); x2 = Math.max(x2, x + dx); y1 = Math.min(y1, y + dy); y2 = Math.max(y2, y + dy); }
  })));
  const x0 = Math.round(c - (x1 + x2 + 1) / 2 * u), y0 = Math.round(c - (y1 + y2 + 1) / 2 * u);
  const beam = g.createLinearGradient(0, y0, 0, y0 + GRID_H * u);
  beam.addColorStop(0, "rgba(245,226,181,0)"); beam.addColorStop(0.5, "rgba(245,226,181,.95)"); beam.addColorStop(1, "rgba(245,226,181,0)");
  const bw = (2 * gap + 1) * u;
  g.fillStyle = beam;
  g.beginPath(); g.moveTo(c - bw / 2, 0); g.lineTo(c + bw / 2, 0); g.lineTo(c + bw * 1.6, size); g.lineTo(c - bw * 1.6, size); g.closePath(); g.fill();
  const cells = f => parts.forEach(([grid, dx, dy]) => grid.forEach((row, y) => row.forEach((cc, x) => { if (cc) f(cc, x0 + (x + dx) * u, y0 + (y + dy) * u); })));
  g.fillStyle = v("--acorn-hi");
  cells((cc, px, py) => g.fillRect(px - u, py - u, 3 * u, 3 * u));
  cells((cc, px, py) => { g.fillStyle = v(COLORS[cc]); g.fillRect(px, py, u, u); });
  g.fillStyle = v("--acorn-inner");
  [[-1, -3], [1, -5], [0, -7], [-2, -6], [2, -2]].forEach(([dx, dy]) => g.fillRect(Math.round(c + dx * u - u / 2), y0 + (10 + dy) * u, u, u));
  return cv.toDataURL("image/png");
}"""

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(color_scheme="light")
    pg.goto((ROOT / "index.html").as_uri())
    for name, size, u in ICONS:
        url = pg.evaluate(JS, [size, u, GAP, LIFT])
        (ROOT / name).write_bytes(base64.b64decode(url.split(",", 1)[1]))
        print(name)
    b.close()
