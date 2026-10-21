"""홈 화면 아이콘을 index.html 의 도토리 스프라이트로 그려 저장소 맨 위에 쓴다.

실행: 저장소 맨 위에서 python tools/make-icons.py
"""
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
# 파일 이름, 한 변, 칸 크기. maskable 은 기기가 원·둥근 사각으로 잘라도 도토리가 남게 작게 그린다.
ICONS = [("apple-touch-icon.png", 180, 6), ("icon-192.png", 192, 6), ("icon-512.png", 512, 16), ("icon-maskable-512.png", 512, 12)]
JS = r"""([size, u]) => {
  const css = getComputedStyle(document.documentElement), v = n => css.getPropertyValue(n).trim();
  const cv = Object.assign(document.createElement("canvas"), { width: size, height: size });
  const g = cv.getContext("2d");
  g.fillStyle = v("--bg"); g.fillRect(0, 0, size, size);
  const x0 = Math.round((size - GRID_W * u) / 2), y0 = Math.round((size - GRID_H * u) / 2);
  WHOLE.forEach((row, y) => row.forEach((c, x) => {
    if (c) { g.fillStyle = v(COLORS[c]); g.fillRect(x0 + x * u, y0 + y * u, u, u); }
  }));
  return cv.toDataURL("image/png");
}"""

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(color_scheme="light")
    pg.goto((ROOT / "index.html").as_uri())
    for name, size, u in ICONS:
        url = pg.evaluate(JS, [size, u])
        (ROOT / name).write_bytes(base64.b64decode(url.split(",", 1)[1]))
        print(name)
    b.close()
