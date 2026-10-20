INSERT OR REPLACE INTO hist (day, score, n) SELECT day, score, COUNT(*) FROM scores GROUP BY day, score;
