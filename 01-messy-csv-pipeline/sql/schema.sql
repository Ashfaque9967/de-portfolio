DROP VIEW IF EXISTS v_location_summary;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS restaurant_listings;
DROP TABLE IF EXISTS restaurants;

CREATE TABLE restaurants (
    url            TEXT,
    address        TEXT NOT NULL,
    name           TEXT NOT NULL,
    online_order   BOOLEAN,
    book_table     BOOLEAN,
    rate           DOUBLE PRECISION,
    votes          BIGINT,
    phone          TEXT,
    location       TEXT,
    rest_type      TEXT,
    dish_liked     TEXT,
    cuisines       TEXT,
    cost_for_two   BIGINT,
    reviews_list   TEXT,
    menu_item      TEXT,
    listing_type   TEXT,
    listing_city   TEXT,
    PRIMARY KEY (name, address)
);

CREATE TABLE restaurant_listings (
    name          TEXT NOT NULL,
    address       TEXT NOT NULL,
    listing_type  TEXT,
    FOREIGN KEY (name, address) REFERENCES restaurants (name, address)
);

CREATE TABLE reviews (
    name            TEXT NOT NULL,
    address         TEXT NOT NULL,
    review_text     TEXT,
    rating          DOUBLE PRECISION,
    text_corrupted  BOOLEAN,
    FOREIGN KEY (name, address) REFERENCES restaurants (name, address)
);

CREATE INDEX idx_restaurants_name ON restaurants (name);
CREATE INDEX idx_reviews_restaurant ON reviews (name, address);

CREATE VIEW v_location_summary AS
SELECT location,
       COUNT(*) AS restaurants,
       ROUND(AVG(rate)::numeric, 2) AS avg_rating,
       SUM(votes) AS total_votes
FROM restaurants
WHERE location IS NOT NULL
GROUP BY location
HAVING COUNT(*) >= 20;