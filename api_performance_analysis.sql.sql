-- api_performance_analysis.sql

/**
 * API Performance Analysis Query
 * 
 * Purpose:
 * Identifies slow-performing API calls to diagnose integration performance issues.
 * 
 * Use Cases:
 * - Troubleshooting slow integrations between Gong and CRM systems
 * - Identifying API endpoints that might be causing timeouts
 * - Detecting patterns in API performance degradation
 * - Prioritizing optimization efforts based on impact
 * 
 * Results Interpretation:
 * - High avg_response_time with low error_count: Likely performance bottleneck
 * - High error_count: Potential authentication or payload issues
 * - High call_count with high avg_response_time: High-impact optimization target
 */

SELECT 
    endpoint_path,
    AVG(response_time_ms) as avg_response_time,    -- Average response time in milliseconds
    MAX(response_time_ms) as max_response_time,    -- Maximum observed response time
    COUNT(*) as call_count,                        -- Total number of calls to this endpoint
    COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count,  -- Count of error responses
    -- Calculate error percentage for easier analysis
    ROUND((COUNT(CASE WHEN status_code >= 400 THEN 1 END) * 100.0) / COUNT(*), 2) as error_percentage
FROM api_request_logs
WHERE 
    -- Filter for a specific time range to focus analysis
    timestamp BETWEEN '2023-07-01' AND '2023-07-07'
    -- Optionally filter for a specific customer
    -- AND customer_id = 'CUSTOMER123'
GROUP BY endpoint_path
-- Order by average response time to prioritize slowest endpoints
ORDER BY avg_response_time DESC
LIMIT 10;  -- Focus on top 10 slowest endpoints
