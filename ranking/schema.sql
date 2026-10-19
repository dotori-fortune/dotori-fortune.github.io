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
