// 무한 도토리 오늘의 랭킹. 날짜마다 사람(player)당 최고점 하나만 남긴다.
const ORIGINS = [/^https:\/\/dotori-fortune\.github\.io$/, /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/];
const TOP = 10;
const NAME_MAX = 8;
const MISSES = 1;
const SCORE_MAX = 5000;
const DAY_MS = 86400000;
// 상위 목록은 모두에게 같아서 잠깐 캐시에 담아 D1 읽기를 아낀다.
const TOP_TTL = 5;
const topKey = day => `https://acorn-rank.cache/top?day=${encodeURIComponent(day)}`;

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

// 캐시에는 player 를 담아 두고, 내보낼 때는 내 줄인지만 표시하고 지운다.
async function topRows(env, day) {
  const cache = caches.default;
  const hit = await cache.match(topKey(day));
  if (hit) return hit.json();
  const { results } = await env.DB.prepare(
    "SELECT player, name, score, count FROM scores WHERE day = ?1 ORDER BY score DESC, at ASC LIMIT ?2",
  ).bind(day, TOP).all();
  await cache.put(topKey(day), new Response(JSON.stringify(results), { headers: { "cache-control": `max-age=${TOP_TTL}` } }));
  return results;
}

// 순위는 나보다 높은 점수의 사람 수 + 1 이다. 점수별 인원표(hist)를 더해서 참가자 수와 상관없이 몇 줄만 읽는다.
async function myRank(env, day, player) {
  const mine = await env.DB.prepare("SELECT score, count FROM scores WHERE day = ?1 AND player = ?2").bind(day, player).first();
  if (!mine) return null;
  const above = await env.DB.prepare("SELECT COALESCE(SUM(n), 0) AS n FROM hist WHERE day = ?1 AND score > ?2").bind(day, mine.score).first();
  return { score: mine.score, count: mine.count, rank: above.n + 1 };
}

async function ranking(env, day, player) {
  const rows = await topRows(env, day);
  const top = rows.map(({ player: p, ...r }) => ({ ...r, me: !!player && p === player }));
  return { top, mine: player ? await myRank(env, day, player) : null };
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
      const prev = await env.DB.prepare("SELECT score FROM scores WHERE day = ?1 AND player = ?2").bind(run.day, run.player).first();
      if (!prev || run.score > prev.score) {
        const bump = (score, d) => env.DB.prepare(
          "INSERT INTO hist (day, score, n) VALUES (?1, ?2, ?3) ON CONFLICT (day, score) DO UPDATE SET n = n + excluded.n",
        ).bind(run.day, score, d);
        await env.DB.batch([
          env.DB.prepare(
            `INSERT INTO scores (day, player, name, score, count, at) VALUES (?1, ?2, ?3, ?4, ?5, ?6)
             ON CONFLICT (day, player) DO UPDATE SET name = excluded.name, score = excluded.score, count = excluded.count, at = excluded.at`,
          ).bind(run.day, run.player, name, run.score, run.count, Date.now()),
          bump(run.score, 1),
          ...(prev ? [
            bump(prev.score, -1),
            env.DB.prepare("DELETE FROM hist WHERE day = ?1 AND score = ?2 AND n <= 0").bind(run.day, prev.score),
          ] : []),
        ]);
        await caches.default.delete(topKey(run.day));
      }
      return json(await ranking(env, run.day, run.player), 200, cors);
    }
    return json({ error: "method" }, 405, cors);
  },
};
