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

-- Remove null ratings and ratings below 1.0
non_null = FILTER reviews BY rating IS NOT NULL AND rating >= 1.0;

-- Group valid reviews by product category
category_group = GROUP non_null BY product_category;

-- Calculate average rating for each category
category_avg = FOREACH category_group GENERATE
    group AS product_category,
    ROUND_TO(AVG(non_null.rating), 2) AS average_rating;

-- Display the results
DUMP category_avg;

-- Store the results in HDFS
STORE category_avg
INTO '/user/aiml/category_average_rating'
USING PigStorage(',');
