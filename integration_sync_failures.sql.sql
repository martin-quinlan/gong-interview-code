-- integration_sync_failures.sql

/**
 * Integration Sync Failures Query
 * 
 * Purpose:
 * Identifies records failing to sync between systems for troubleshooting integration issues.
 * 
 * Use Cases:
 * - Diagnosing problems with CRM integrations
 * - Identifying patterns in failed syncs
 * - Verifying integration health after configuration changes
 * - Providing evidence for troubleshooting escalations
 * 
 * Results Interpretation:
 * - Clusters of failures around specific timestamps: Potential API outage or rate limiting
 * - Patterns in error_message: Common failure modes to address
 * - Null sync_status: Records not attempted for sync yet
 */

SELECT 
    c.call_id,                     -- Unique identifier for the call
    c.started_at,                  -- Call timestamp for chronological analysis
    c.duration,                    -- Call duration to identify patterns with longer calls
    c.recording_status,            -- Current status in source system
    
    -- Integration sync information
    i.sync_status,                 -- Current sync status (NULL, PENDING, SUCCESS, FAILED)
    i.last_sync_attempt,           -- Last attempt timestamp
    i.error_message,               -- Error message if failed
    
    -- Calculate time since last attempt for aging analysis
    DATEDIFF(minute, i.last_sync_attempt, CURRENT_TIMESTAMP) as minutes_since_attempt
    
FROM calls c

-- Left join to include calls without sync records
LEFT JOIN integration_sync_records i ON c.call_id = i.call_id

-- Filter for recent calls within last week
WHERE c.started_at > DATEADD(day, -7, CURRENT_DATE)
    -- Only include unsynced or failed syncs
    AND (i.sync_status IS NULL OR i.sync_status = 'FAILED')
    
-- Order by most recent calls first
ORDER BY c.started_at DESC;
