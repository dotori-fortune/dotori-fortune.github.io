// 무한 도토리 오늘의 랭킹. 날짜마다 사람(player)당 최고점 하나만 남긴다.
const ORIGINS = [/^https:\/\/dotori-fortune\.github\.io$/, /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/];
const TOP = 10;
const NAME_MAX = 8;
const MISSES = 1;
const SCORE_MAX = 5000;
const DAY_MS = 86400000;

const json = (body, status, cors) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", ...cors } });

// 날짜 키는 브라우저 현지 날짜라 서버 UTC 기준 앞뒤 하루까지 받는다.
function validDay(day) {
  const m = /^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(day ?? "");
  if (!m) return false;
  const t = Date.UTC(+m[1], +m[2] - 1, +m[3]);
  return Math.abs(t - Date.now()) < 2 * DAY_MS;
}

const validPlayer = p => typeof p === "string" && /^[0-9a-f-]{36}$/.test(p);
const isCount = n => Number.isInteger(n) && n >= 0 && n <= SCORE_MAX;

// 점수는 딱 2점·톡 1점의 합이다. 맞히면 한 번에 깨지고 헛손질 한 번에 끝나므로 서로 맞아야 한다.
function validRun({ score, count, perfects, taps }) {
  if (![score, count, perfects, taps].every(isCount)) return false;
  const goods = taps - perfects - MISSES;
  return goods >= 0 && score === 2 * perfects + goods && count === taps - MISSES;
}

async function ranking(env, day, player) {
  const { results } = await env.DB.prepare(
    "SELECT name, score, count, player = ?2 AS me FROM scores WHERE day = ?1 ORDER BY score DESC, at ASC LIMIT ?3",
  ).bind(day, player ?? "", TOP).all();
  let mine = null;
  if (player) {
    mine = await env.DB.prepare(
      "SELECT s.score, (SELECT COUNT(*) FROM scores o WHERE o.day = s.day AND (o.score > s.score OR (o.score = s.score AND o.at < s.at))) + 1 AS rank FROM scores s WHERE s.day = ?1 AND s.player = ?2",
    ).bind(day, player).first();
  }
  return { top: results.map(r => ({ ...r, me: !!r.me })), mine };
}

export default {
  async fetch(req, env) {
    const origin = req.headers.get("origin") ?? "";
    const cors = ORIGINS.some(re => re.test(origin))
      ? { "access-control-allow-origin": origin, "access-control-allow-methods": "GET, POST", "access-control-allow-headers": "content-type", vary: "origin" }
      : {};
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    const url = new URL(req.url);
    if (url.pathname !== "/rank") return json({ error: "not found" }, 404, cors);

    if (req.method === "GET") {
      const day = url.searchParams.get("day");
      if (!validDay(day)) return json({ error: "bad day" }, 400, cors);
      const player = url.searchParams.get("player");
      return json(await ranking(env, day, validPlayer(player) ? player : null), 200, cors);
    }

    if (req.method === "POST") {
      let run;
      try { run = await req.json(); } catch { return json({ error: "bad body" }, 400, cors); }
      const name = String(run.name ?? "").replace(/[\p{C}<>]/gu, "").trim().slice(0, NAME_MAX);
      if (!validDay(run.day) || !validPlayer(run.player) || !name || !validRun(run)) return json({ error: "bad run" }, 400, cors);
      await env.DB.prepare(
        `INSERT INTO scores (day, player, name, score, count, at) VALUES (?1, ?2, ?3, ?4, ?5, ?6)
         ON CONFLICT (day, player) DO UPDATE SET name = excluded.name, score = excluded.score, count = excluded.count, at = excluded.at
         WHERE excluded.score > scores.score`,
      ).bind(run.day, run.player, name, run.score, run.count, Date.now()).run();
      return json(await ranking(env, run.day, run.player), 200, cors);
    }
    return json({ error: "method" }, 405, cors);
  },
};
