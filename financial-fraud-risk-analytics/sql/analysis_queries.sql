-- Financial Fraud & Risk Analytics (SQLite)
-- Import the CSV into a SQLite table named transactions before running.
-- Expected columns include: Time, Amount, Class. Quote "Time" because it can
-- be interpreted as a SQL keyword by some database tools.

-- 1. Dataset size and class balance
SELECT
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN Class = 1 THEN 1 ELSE 0 END) AS labelled_fraud_transactions,
    SUM(CASE WHEN Class = 0 THEN 1 ELSE 0 END) AS class_0_transactions,
    ROUND(
      100.0 * SUM(CASE WHEN Class = 1 THEN 1 ELSE 0 END) / COUNT(*), 6
    ) AS labelled_fraud_rate_percent
FROM transactions;

-- 2. Transaction amount summary by class
SELECT
    Class,
    COUNT(*) AS transaction_count,
    ROUND(AVG(Amount), 2) AS mean_amount,
    ROUND(MIN(Amount), 2) AS minimum_amount,
    ROUND(MAX(Amount), 2) AS maximum_amount
FROM transactions
GROUP BY Class
ORDER BY Class;

-- 3. Approximate elapsed-hour buckets (Time is seconds from the first record)
SELECT
    CAST("Time" / 3600 AS INTEGER) AS elapsed_hour_bucket,
    Class,
    COUNT(*) AS transaction_count
FROM transactions
GROUP BY elapsed_hour_bucket, Class
ORDER BY elapsed_hour_bucket, Class;

-- 4. Simple amount threshold baseline.
-- This is an educational baseline, not a recommended real-world fraud rule.
SELECT
    CASE WHEN Amount >= 100 THEN 'Flagged: amount >= 100'
         ELSE 'Not flagged: amount < 100' END AS screening_group,
    COUNT(*) AS transactions,
    SUM(CASE WHEN Class = 1 THEN 1 ELSE 0 END) AS labelled_fraud_count,
    SUM(CASE WHEN Class = 0 THEN 1 ELSE 0 END) AS class_0_count
FROM transactions
GROUP BY screening_group;

-- 5. Precision and recall for the >= 100 amount-only threshold
WITH flagged AS (
    SELECT
        CASE WHEN Amount >= 100 THEN 1 ELSE 0 END AS is_flagged,
        Class
    FROM transactions
)
SELECT
    SUM(CASE WHEN is_flagged = 1 AND Class = 1 THEN 1 ELSE 0 END) AS true_positives,
    SUM(CASE WHEN is_flagged = 1 AND Class = 0 THEN 1 ELSE 0 END) AS false_positives,
    SUM(CASE WHEN is_flagged = 0 AND Class = 1 THEN 1 ELSE 0 END) AS false_negatives,
    ROUND(
      1.0 * SUM(CASE WHEN is_flagged = 1 AND Class = 1 THEN 1 ELSE 0 END)
      / NULLIF(SUM(CASE WHEN is_flagged = 1 THEN 1 ELSE 0 END), 0), 4
    ) AS precision,
    ROUND(
      1.0 * SUM(CASE WHEN is_flagged = 1 AND Class = 1 THEN 1 ELSE 0 END)
      / NULLIF(SUM(CASE WHEN Class = 1 THEN 1 ELSE 0 END), 0), 4
    ) AS recall
FROM flagged;
