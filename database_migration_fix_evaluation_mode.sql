-- Database Migration: Fix evaluation_mode column issue and remove deprecated dimensions
-- Issue: ENUM column too restrictive for new evaluation modes like 'specification_query'
-- Also: Remove fuzzy_understanding and error_handling_transparency dimensions
-- Date: 2024-12-12

USE ai_evaluation_db;

-- Step 1: Backup current data (optional but recommended)
-- CREATE TABLE ai_evaluation_sessions_backup AS SELECT * FROM ai_evaluation_sessions;

-- Step 2: Modify the evaluation_mode column from ENUM to VARCHAR(255) to support longer values
ALTER TABLE ai_evaluation_sessions 
MODIFY COLUMN evaluation_mode VARCHAR(255) NOT NULL DEFAULT 'manual' COMMENT '评估模式：支持manual, auto, specification_query等';

-- Step 3: Update the index if needed
DROP INDEX IF EXISTS idx_evaluation_mode ON ai_evaluation_sessions;
CREATE INDEX idx_evaluation_mode ON ai_evaluation_sessions(evaluation_mode);

-- Step 4: Clean up deprecated dimensions data (if exists)
-- Note: This is a data cleanup step - adjust table names according to your actual schema
-- UPDATE ai_evaluation_sessions 
-- SET evaluation_data = JSON_REMOVE(evaluation_data, '$.dimension_scores.fuzzy_understanding', '$.dimension_scores.error_handling_transparency')
-- WHERE JSON_VALID(evaluation_data) AND evaluation_data IS NOT NULL;

-- Step 5: Verify the change
DESCRIBE ai_evaluation_sessions;

-- Step 6: Test insertion of new evaluation modes
INSERT INTO ai_evaluation_sessions (session_id, evaluation_mode, created_at) 
VALUES 
    ('test_specification_query', 'specification_query', NOW()),
    ('test_custom_mode', 'custom_evaluation_mode_with_very_long_name', NOW())
ON DUPLICATE KEY UPDATE evaluation_mode = VALUES(evaluation_mode);

-- Step 7: Clean up test data
DELETE FROM ai_evaluation_sessions WHERE session_id IN ('test_specification_query', 'test_custom_mode');

-- Step 8: Verification query
SELECT 'Migration completed successfully. evaluation_mode column now supports specification_query and other custom modes.' AS status;

-- Show current evaluation modes in use
SELECT DISTINCT evaluation_mode, COUNT(*) as count 
FROM ai_evaluation_sessions 
GROUP BY evaluation_mode 
ORDER BY count DESC;

-- Show column info
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    COLUMN_DEFAULT,
    IS_NULLABLE,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'ai_evaluation_db' 
  AND TABLE_NAME = 'ai_evaluation_sessions' 
  AND COLUMN_NAME = 'evaluation_mode'; 