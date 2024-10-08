
-- > head -n 1 movies_metadata.csv 
-- adult,,budget,genres,homepage,
-- id,imdb_id,originabelongs_to_collectionl_language,original_title,overview,
-- popularity,poster_path,production_companies,
-- production_countries,release_date,revenue,runtime,
-- spoken_languages,status,tagline,title,video,
-- vote_average,vote_count

-- as superuser
-- CREATE DATABASE patient_iq;
-- \c patient_iq
-- CREATE SCHEMA patient_iq_schema;
-- \c patient_iq
CREATE TABLE patient_iq_schema.movies (
    id INT PRIMARY KEY,
    genres TEXT,
    revenue NUMERIC,
    budget NUMERIC,
    spoken_languages TEXT,
    release_date DATE
);

COPY patient_iq_schema.movies (id, budget, genres, release_date, revenue, spoken_languages)
FROM '/Users/sbecker11/workspace-patient-iq/kaggle-movies-processor/movies_metadata.csv'
DELIMITER ',' 
CSV HEADER 
ENCODING 'UTF8';








SELECT COUNT(*) FROM patient_iq_schema.raw_movies; --  45466

SELECT release_date FROM patient_iq_schema.raw_movies 
LIMIT 5; -- '\d{4}-\d{2}-\d{2}'

-- null release_date = 0
SELECT COUNT(*) FROM patient_iq_schema.raw_movies 
where release_date is null;

-- matches date format - 45376
SELECT COUNT(*) FROM patient_iq_schema.raw_movies 
where release_date ~ '\d{4}-\d{2}-\d{2}';

-- does not match date format - 90
SELECT COUNT(*) FROM patient_iq_schema.raw_movies 
where release_date !~ '\d{4}-\d{2}-\d{2}';

-- all white spaces - 0
SELECT count(*) FROM patient_iq_schema.raw_movies 
WHERE release_date ~ '\s'; 

-- does not contain only white spaces - 3
SELECT release_date FROM patient_iq_schema.raw_movies 
WHERE release_date IS NOT NULL
  AND release_date !~ '^\s*$'  -- Not all white spaces
  AND release_date !~ '^\d{4}-\d{2}-\d{2}$';  -- Does not match YYYY-MM-DD pattern
--------------
 1
 12
 22
(3 rows)

-- set invalid release_dates to null
UPDATE patient_iq_schema.raw_movies
SET release_date = CASE
    WHEN release_date !~ '^\d{4}-\d{2}-\d{2}$'  -- Does not match YYYY-MM-DD pattern
    THEN NULL
    ELSE release_date
END;

-- null release_date = 90
SELECT COUNT(*) FROM patient_iq_schema.raw_movies 
where release_date is null;

-- add a new release_month column
ALTER TABLE patient_iq_schema.raw_movies
ADD COLUMN release_month INT;

-- update release_month column where release_date is not null
-- 45466
UPDATE patient_iq_schema.raw_movies
SET release_month = CASE
    WHEN release_date IS NOT NULL THEN EXTRACT(MONTH FROM release_date::DATE)
    ELSE NULL
END;

-- null release_month = 90
SELECT COUNT(*) FROM patient_iq_schema.raw_movies 
where release_month is null;

-- count movies with null genres column - 0
SELECT COUNT(*)
FROM patient_iq_schema.raw_movies
WHERE genres IS NULL;

-- count movies with empty string genres =0
SELECT COUNT(*)
FROM patient_iq_schema.raw_movies
WHERE genres = '';

-- view random genres
SELECT genres
FROM patient_iq_schema.raw_movies
ORDER BY RANDOM()
LIMIT 5;
[{'id': 53, 'name': 'Thriller'}, {'id': 28, 'name': 'Action'}, {'id': 18, 'name': 'Drama'}]

-- Count rows where genres contains valid JSON that can be exploded
SELECT count(*)
FROM patient_iq_schema.raw_movies
WHERE jsonb_typeof(genres::jsonb) = 'array';
ERROR:  invalid input syntax for type json
DETAIL:  Token "'" is invalid.
CONTEXT:  JSON data, line 1: -- 

-- convert single quotes to double quotes before casting to jsonb -- 45466
SELECT count(*)
FROM patient_iq_schema.raw_movies
WHERE jsonb_typeof(REPLACE(genres, '''', '"')::jsonb) = 'array';

-- review revenue column
SELECT COUNT(*) from patient_iq_schema.raw_movies
WHERE revenue IS NULL; -- 0

-- count movies with a valid revenue column - 45460 - so 6 invalid
SELECT COUNT(*)
FROM patient_iq_schema.raw_movies
WHERE revenue ~ '^\d+(\.\d+)?$';

-- review invalid revnue values - 6 but all are empty strings
SELECT revenue
FROM patient_iq_schema.raw_movies
WHERE revenue !~ '^\d+(\.\d+)?$';

-- count movies with empty string revenue = 6
SELECT count(*)
FROM patient_iq_schema.raw_movies
WHERE revenue = '';

-- set invalid revenue values to null
UPDATE patient_iq_schema.raw_movies
SET revenue = NULL
WHERE revenue = '';

-- count movies with null revenue - 6
SELECT COUNT(*) from patient_iq_schema.raw_movies
WHERE revenue IS NULL;

-- review budget column
SELECT COUNT(*) from patient_iq_schema.raw_movies
WHERE budget IS NULL; -- 0

-- count movies with a valid budget column - 45463 - so 3 invalid
SELECT COUNT(*) from patient_iq_schema.raw_movies
WHERE budget ~ '^\d+(\.\d+)?$';

-- set invalid budget values to null
UPDATE patient_iq_schema.raw_movies
SET budget = NULL
WHERE budget !~ '^\d+(\.\d+)?$';

-- count movies with null budget - 3
SELECT COUNT(*) from patient_iq_schema.raw_movies
WHERE budget IS NULL;

-- find the min/max revenue and budget values
SELECT MIN(revenue), MAX(revenue), MIN(budget), MAX(budget)
FROM patient_iq_schema.raw_movies 
where revenue is not null and budget is not null;
 min |   max    | min |  max
-----+----------+-----+--------
 0   | 99965753 | 0   | 998000

-- find the number of movies with zero revenue
SELECT COUNT(*) from patient_iq_schema.raw_movies
WHERE revenue = 0;
HINT:  No operator matches the given name and argument types. You might need to add explicit type casts.

-- cast revenue to numeric and compare to 0 -  38052
SELECT COUNT(*) from patient_iq_schema.raw_movies
WHERE revenue::NUMERIC = 0;

-- find the number of movies with zero budget - 36573
SELECT COUNT(*) from patient_iq_schema.raw_movies
WHERE budget::NUMERIC = 0;

-- add a new column to store the profit
ALTER TABLE patient_iq_schema.raw_movies
ADD COLUMN profit NUMERIC;
-- update profit column -- 45466
UPDATE patient_iq_schema.raw_movies
SET profit = revenue::NUMERIC - budget::NUMERIC;

-- find the number of movies with zero profit - 34563
SELECT COUNT(*) from patient_iq_schema.raw_movies
WHERE profit = 0;

question #4 - How many movies are in more than one language?

-- review spoken_languages column
select spoken_languages from patient_iq_schema.raw_movies
where spoken_languages is not null
ORDER BY RANDOM()
LIMIT 5;

-- add a new column to count the number of spoken languages for each movie
ALTER TABLE patient_iq_schema.raw_movies
ADD COLUMN spoken_languages_count INT;

-- update the spoken_languages_count column -- 45466
UPDATE patient_iq_schema.raw_movies
SET spoken_languages_count = jsonb_array_length(REPLACE(spoken_languages, '''', '"')::jsonb);

-- update the spoken_languages_count column -- 45466
UPDATE patient_iq_schema.raw_movies
SET spoken_languages_count = jsonb_array_length(REPLACE(spoken_languages, '''', '"')::jsonb);
ERROR:  invalid input syntax for type json
DETAIL:  The input string ended unexpectedly.
CONTEXT:  JSON data, line 1:

-- find spoken_languages that are not valid JSON - 6
select spoken_languages from patient_iq_schema.raw_movies
where spoken_languages !~ '^\[.*\]$';

-- set invalid spoken_languages values to null
UPDATE patient_iq_schema.raw_movies
SET spoken_languages = NULL
WHERE spoken_languages !~ '^\[.*\]$';

-- find spoken_languages that have excape sequences
select spoken_languages from patient_iq_schema.raw_movies
where spoken_languages ~ '\\x';
-- [{'iso_639_1': 'ru', 'name': 'Pусский'}, {'iso_639_1': 'lt', 'name': 'Lietuvi\x9akai'}]
-- [{'iso_639_1': 'fr', 'name': 'Français'}, {'iso_639_1': 'lt', 'name': 'Lietuvi\x9akai'}, {'iso_639_1': 'ru', 'name': 'Pусский'}]

-- replace excape sequences with unicode characters
UPDATE patient_iq_schema.raw_movies
SET spoken_languages = REPLACE(spoken_languages, '\x9a', 'š')
WHERE spoken_languages ~ '\\x';

-- retry the update spoken_languages_count column -- 45466 - all counts are valid
UPDATE patient_iq_schema.raw_movies
SET spoken_languages_count = jsonb_array_length(REPLACE(spoken_languages, '''', '"')::jsonb);

-- QUESTION #4
-- find the number of movies with number of spoken_languages_count > 1 - 7895
SELECT COUNT(*)
FROM patient_iq_schema.raw_movies
WHERE spoken_languages_count > 1;
 count
-------
  7895

-- QUESTION #5
-- For each month, show the top genre by number of releases in that month
with genre_counts as (
    SELECT release_month, jsonb_array_elements_text(REPLACE(genres, '''', '"')::jsonb) as genre
    FROM patient_iq_schema.raw_movies
    WHERE jsonb_typeof(REPLACE(genres, '''', '"')::jsonb) = 'array'
    and release_month is not null
),
genre_counts_by_month as (
    SELECT release_month, genre, COUNT(*) as genre_count
    FROM genre_counts
    GROUP BY release_month, genre
)
SELECT release_month, genre, genre_count
FROM (
    SELECT release_month, genre, genre_count, 
           ROW_NUMBER() OVER (PARTITION BY release_month ORDER BY genre_count DESC) as rn
    FROM genre_counts_by_month
) as ranked_genres
WHERE rn = 1;

 release_month |            genre            | genre_count
---------------+-----------------------------+-------------
             1 | {"id": 18, "name": "Drama"} |        2310
             2 | {"id": 18, "name": "Drama"} |        1413
             3 | {"id": 18, "name": "Drama"} |        1518
             4 | {"id": 18, "name": "Drama"} |        1518
             5 | {"id": 18, "name": "Drama"} |        1624
             6 | {"id": 18, "name": "Drama"} |        1347
             7 | {"id": 18, "name": "Drama"} |        1016
             8 | {"id": 18, "name": "Drama"} |        1487
             9 | {"id": 18, "name": "Drama"} |        2588
            10 | {"id": 18, "name": "Drama"} |        2055
            11 | {"id": 18, "name": "Drama"} |        1663
            12 | {"id": 18, "name": "Drama"} |        1716

question #3
What's the average revenue per genre?  
List them in order from highest to lowest 
average revenue.  For brevity, list the first 
three as the response to this question.

with genre_revenue as (
    SELECT jsonb_array_elements_text(REPLACE(genres, '''', '"')::jsonb) as genre, revenue::NUMERIC
    FROM patient_iq_schema.raw_movies
    WHERE jsonb_typeof(REPLACE(genres, '''', '"')::jsonb) = 'array'
    and revenue is not null
) SELECT genre, round(avg(revenue)) as avg_revenue
from genre_revenue
group by genre
order by avg_revenue desc
limit 3;
              genre              | avg_revenue
---------------------------------+-------------
 {"id": 12, "name": "Adventure"} |    57242375
 {"id": 14, "name": "Fantasy"}   |    44978258
 {"id": 10751, "name": "Family"} |    38713063
(3 rows)

question #2
Which movies did not recoup their budget? 
(Where revenue did not exceed budget).  
For brevity, list the first 3 (as ordered by 
imdb_id) as the response to this question.

select imdb_id, original_title, 
revenue::NUMERIC - budget::NUMERIC as profit
from patient_iq_schema.raw_movies
where revenue::NUMERIC < budget::NUMERIC
and imdb_id <> ''
order by imdb_id
limit 3;

  imdb_id  |     original_title      | profit
-----------+-------------------------+--------
 tt0000417 | Le Voyage dans la Lune  |  -5985
 tt0000439 | The Great Train Robbery |   -150
 tt0000498 | Rescued by Rover        |    -37

question #1
Which movie(s) had the 3rd highest revenue?
SELECT imdb_id, original_title, revenue
FROM patient_iq_schema.raw_movies
where revenue::NUMERIC > 0
ORDER BY revenue DESC
offset 2 limit 1;

  imdb_id  |     original_title     | revenue
-----------+------------------------+---------
 tt2288121 | Tot yeshchyo Karloson! | 9938268

check with top 4
  imdb_id  |     original_title     | revenue
-----------+------------------------+----------
 tt0465494 | Hitman                 | 99965753
 tt0111301 | Street Fighter         | 99423521
 tt2288121 | Tot yeshchyo Karloson! | 9938268
 tt1327194 | The Lucky One          | 99357138



1.	Which movie(s) had the 3rd highest revenue?

  imdb_id  |     original_title     | revenue
-----------+------------------------+---------
 tt2288121 | Tot yeshchyo Karloson! | 9938268

2.	Which movies did not recoup their budget? 
(Where revenue did not exceed budget).  For 
brevity, list the first 3 (as ordered by 
imdb_id) as the response to this question.

  imdb_id  |     original_title      | profit
-----------+-------------------------+--------
 tt0000417 | Le Voyage dans la Lune  |  -5985
 tt0000439 | The Great Train Robbery |   -150
 tt0000498 | Rescued by Rover        |    -37

3.	What's the average revenue per genre?  List 
them in order from highest to lowest average 
revenue.  For brevity, list the first three as 
the response to this question.

              genre              | avg_revenue
---------------------------------+-------------
 {"id": 12, "name": "Adventure"} |    57242375
 {"id": 14, "name": "Fantasy"}   |    44978258
 {"id": 10751, "name": "Family"} |    38713063

4.	How many movies are in more than one language?

  7895

5.	You want to understand if there is a seasonal 
component to movie releases.  For each month, which
genre had the highest proportion of releases?  There
should be 1 answer for each calendar month.  If 
there's a tie, list all the genres.

 release_month |            genre            | num_releases
---------------+-----------------------------+-------------
             1 | {"id": 18, "name": "Drama"} |        2310
             2 | {"id": 18, "name": "Drama"} |        1413
             3 | {"id": 18, "name": "Drama"} |        1518
             4 | {"id": 18, "name": "Drama"} |        1518
             5 | {"id": 18, "name": "Drama"} |        1624
             6 | {"id": 18, "name": "Drama"} |        1347
             7 | {"id": 18, "name": "Drama"} |        1016
             8 | {"id": 18, "name": "Drama"} |        1487
             9 | {"id": 18, "name": "Drama"} |        2588
            10 | {"id": 18, "name": "Drama"} |        2055
            11 | {"id": 18, "name": "Drama"} |        1663
            12 | {"id": 18, "name": "Drama"} |        1716
