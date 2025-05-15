-- declining_usage_detection.sql

/**
 * Declining Usage Detection Query
 * 
 * Purpose:
 * Identifies users with declining engagement who might need intervention or additional training.
 * 
 * Use Cases:
 * - Proactively identifying at-risk accounts before churn
 * - Targeting re-engagement campaigns
 * - Identifying potential product issues affecting specific user segments
 * - Prioritizing customer success interventions
 * 
 * Results Interpretation:
 * - Large negative percentage_change: Significant drop requiring immediate attention
 * - Patterns across departments: Potential systemic issues affecting user segments
 * - Previously high usage that declined: Higher priority than historically low users
 */

-- Define current period data (last 30 days)
WITH current_period AS (
    SELECT 
        user_id,
        COUNT(*) as call_count        -- Count calls in current period
    FROM calls
    WHERE call_date BETWEEN DATEADD(day, -30, CURRENT_DATE) AND CURRENT_DATE
    GROUP BY user_id
),

-- Define previous period data (30-60 days ago) for comparison
previous_period AS (
    SELECT 
        user_id,
        COUNT(*) as call_count        -- Count calls in previous period
    FROM calls
    WHERE call_date BETWEEN DATEADD(day, -60, CURRENT_DATE) AND DATEADD(day, -30, CURRENT_DATE)
    GROUP BY user_id
)

-- Main query to compare periods and calculate changes
SELECT 
    u.department,        -- Include department for segmentation analysis
    u.full_name,         -- User identification
    u.email,             -- Contact information for follow-up
    p.call_count as previous_month_calls,  -- Usage in previous period
    c.call_count as current_month_calls,   -- Usage in current period
    
    -- Calculate percentage change with null handling
    CASE 
        WHEN p.call_count > 0 THEN 
            ROUND((c.call_count - p.call_count) * 100.0 / p.call_count, 2)
        ELSE NULL        -- Avoid division by zero
    END as percentage_change
FROM users u

-- Join with current period data
LEFT JOIN current_period c ON u.user_id = c.user_id

-- Join with previous period data
LEFT JOIN previous_period p ON u.user_id = p.user_id

-- Filter for significant usage decline (users who were active before but reduced usage by 30%+)
WHERE (
    p.call_count > 10 AND  -- Only consider previously active users
    (c.call_count IS NULL OR c.call_count < p.call_count * 0.7)  -- 30% or greater decline
)

-- Order by severity of decline
ORDER BY percentage_change;
