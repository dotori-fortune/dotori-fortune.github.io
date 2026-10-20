CREATE TABLE IF NOT EXISTS scores (
  day TEXT NOT NULL,
  player TEXT NOT NULL,
  name TEXT NOT NULL,
  score INTEGER NOT NULL,
  count INTEGER NOT NULL,
  at INTEGER NOT NULL,
  PRIMARY KEY (day, player)
);
CREATE INDEX IF NOT EXISTS scores_rank ON scores (day, score DESC, at);

-- 점수별 인원. 순위를 셀 때 scores 를 훑지 않으려고 둔다.
CREATE TABLE IF NOT EXISTS hist (
  day TEXT NOT NULL,
  score INTEGER NOT NULL,
  n INTEGER NOT NULL,
  PRIMARY KEY (day, score)
);
