-- New Zealand Tourism Commercial Insights | YE June 2026
-- Source: MBIE IVS microdata. The source ZIP is downloaded separately.
-- This query runs on the temporary visitor-level table made by src/verify_sql.py.
-- SQL work deliberately takes place at visitor grain to avoid multiplying spending
-- when joining itinerary, activities or other multi-response child tables.

WITH segmented AS (
    SELECT
       CASE country_of_residence
          WHEN 'Australia' THEN 'Australia'
          WHEN 'China, People''s Republic of' THEN 'China'
          WHEN 'United States of America' THEN 'United States'
       END AS market,
       CASE purpose_of_visit_main
          WHEN 'Holiday / vacation' THEN 'Holiday'
          WHEN 'Visiting friends / relatives' THEN 'VFR'
          WHEN 'Conference / convention' THEN 'Conference'
          WHEN 'Business' THEN 'Business'
          ELSE 'Other / education'
       END AS purpose,
       first_nz_trip,
       population_weight AS w,
       treated_spend AS spend,
       no_days_in_nz AS days
    FROM ivs_visitors
    WHERE (year = 2025 AND qtr IN (3,4))
       OR (year = 2026 AND qtr IN (1,2))
)
SELECT
    market,
    COUNT(*) AS sample_n,
    SUM(w) AS estimated_ivs_visitors,
    SUM(w * spend) AS estimated_total_spend_nzd,
    SUM(w * spend) / SUM(w) AS mean_total_spend_per_visit_nzd,
    SUM(w * (spend / days)) / SUM(w) AS mean_daily_spend_per_visitor_nzd,
    SUM(w * days) / SUM(w) AS mean_length_of_stay_days,
    100.0 * SUM(CASE WHEN first_nz_trip='No' THEN w ELSE 0 END) / SUM(w) AS repeat_visitor_share_pct,
    100.0 * SUM(CASE WHEN purpose='Holiday' THEN w ELSE 0 END) / SUM(w) AS holiday_visitor_share_pct
FROM segmented
WHERE market IS NOT NULL
GROUP BY market
ORDER BY CASE market WHEN 'Australia' THEN 1 WHEN 'China' THEN 2 ELSE 3 END;