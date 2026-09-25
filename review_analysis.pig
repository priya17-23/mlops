-- Assignment 1: E-commerce product review analysis
-- Local:  pig -x local review_analysis.pig
-- HDFS:   hdfs dfs -mkdir -p /reviews
--         hdfs dfs -put reviews.csv /reviews/
--         pig review_analysis.pig   (change LOAD path to '/reviews/reviews.csv')

raw_reviews = LOAD 'reviews.csv'
USING PigStorage(',')
AS (review_id:int, category:chararray, rating:double);

valid_reviews = FILTER raw_reviews
BY rating IS NOT NULL AND rating >= 1.0;

grouped_by_category = GROUP valid_reviews BY category;

category_avg_ratings = FOREACH grouped_by_category GENERATE
    group AS category,
    ROUND_TO(AVG(valid_reviews.rating), 2) AS average_rating;

DUMP category_avg_ratings;

STORE category_avg_ratings
INTO 'review_output'
USING PigStorage(',');
