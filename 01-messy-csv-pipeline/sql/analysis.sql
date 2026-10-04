-- 1. Top-N per group: RANK vs ROW_NUMBER
WITH ranked AS (
    SELECT location, name, rate, votes,
           ROW_NUMBER() OVER (PARTITION BY location ORDER BY rate DESC, votes DESC) AS rn,
           RANK()       OVER (PARTITION BY location ORDER BY rate DESC)             AS rnk
    FROM restaurants
    WHERE rate IS NOT NULL
)
SELECT * FROM ranked
WHERE location IN ('Indiranagar', 'Whitefield') AND rnk <= 3
ORDER BY location, rnk, rn;

-- 2. LAG + running total: vote concentration in Indiranagar (top 10 = ~25.5%)
WITH r AS (
    SELECT name, votes,
           ROW_NUMBER() OVER (ORDER BY votes DESC, name) AS rn,
           LAG(votes) OVER (ORDER BY votes DESC, name) AS prev_votes,
           SUM(votes) OVER (ORDER BY votes DESC, name) AS running_votes,
           SUM(votes) OVER () AS total_votes
    FROM restaurants
    WHERE location = 'Indiranagar'
)
SELECT rn, name, votes, prev_votes, prev_votes - votes AS gap_from_prev,
       running_votes, ROUND(100.0 * running_votes / total_votes, 1) AS cum_pct
FROM r WHERE rn <= 10 ORDER BY rn;

-- 3. Index: before = Seq Scan 6.9 ms, after = Index Scan 0.055 ms
CREATE INDEX idx_restaurants_name ON restaurants (name);
EXPLAIN ANALYZE SELECT name, location, rate, votes FROM restaurants WHERE name = 'Toit';
-- Leading wildcard ignores the B-tree index (back to Seq Scan)
EXPLAIN ANALYZE SELECT name, location, rate, votes FROM restaurants WHERE name LIKE '%Toit%';

-- 4. View: location summary, small locations filtered out
CREATE VIEW v_location_summary AS
SELECT location,
       COUNT(*) AS restaurants,
       ROUND(AVG(rate)::numeric, 2) AS avg_rating,
       SUM(votes) AS total_votes
FROM restaurants
WHERE location IS NOT NULL
GROUP BY location
HAVING COUNT(*) >= 20;

-- 5. Correlated subquery: restaurants rated above their location average
SELECT r.name, r.location, r.rate,
       ROUND((SELECT AVG(r2.rate) FROM restaurants r2 WHERE r2.location = r.location)::numeric, 2) AS location_avg
FROM restaurants r
WHERE r.location = 'Indiranagar'
  AND r.rate > (SELECT AVG(r2.rate) FROM restaurants r2 WHERE r2.location = r.location)
ORDER BY r.rate DESC, r.votes DESC
LIMIT 10;

-- 6. Self-join: pairs with same location and rest_type, smallest rating gap
SELECT a.name AS restaurant_1, b.name AS restaurant_2, a.rest_type,
       ROUND(ABS(a.rate - b.rate)::numeric, 1) AS rate_gap
FROM restaurants a
JOIN restaurants b
  ON a.location = b.location AND a.rest_type = b.rest_type AND a.name < b.name
WHERE a.location = 'Lavelle Road' AND a.rate IS NOT NULL AND b.rate IS NOT NULL
ORDER BY rate_gap, a.name
LIMIT 10;

-- 7. Transaction demo: UPDATE inside txn, then ROLLBACK (Atomicity)
BEGIN;
UPDATE restaurants SET rate = 1.0 WHERE location = 'Lavelle Road';
SELECT 'inside_txn' AS stage, ROUND(AVG(rate)::numeric, 2) AS avg_rate
FROM restaurants WHERE location = 'Lavelle Road';
ROLLBACK;