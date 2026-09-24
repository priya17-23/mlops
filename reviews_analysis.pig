-- Load review dataset from HDFS
reviews = LOAD '/user/hadoop/reviews/reviews.csv'
USING PigStorage(',')
AS (
    review_id:int,
    product_id:chararray,
    product_category:chararray,
    rating:double,
    review_text:chararray
);

-- Remove records with null ratings
non_null_reviews = FILTER reviews BY rating IS NOT NULL;

-- Remove ratings below 1.0
valid_reviews = FILTER non_null_reviews BY rating >= 1.0;

-- Group valid reviews by product category
grouped_reviews = GROUP valid_reviews BY product_category;

-- Calculate average rating for each category
average_ratings = FOREACH grouped_reviews GENERATE
    group AS product_category,
    AVG(valid_reviews.rating) AS average_rating;

-- Display the results
DUMP average_ratings;

-- Store the results in HDFS
STORE average_ratings
INTO '/user/hadoop/output/average_ratings'
USING PigStorage(',');
