-- AI对话代理评估平台数据库设计
-- 创建时间：2024年12月

-- 1. 评估会话主表
CREATE TABLE ai_evaluation_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL COMMENT '评估会话唯一标识',
    overall_score DECIMAL(3,2) NOT NULL COMMENT '综合评分(1-5)',
    total_scenarios INT NOT NULL DEFAULT 0 COMMENT '总场景数',
    total_conversations INT NOT NULL DEFAULT 0 COMMENT '总对话轮数',
    evaluation_mode ENUM('manual', 'auto', 'dynamic') NOT NULL COMMENT '评估模式',
    evaluation_framework VARCHAR(100) DEFAULT 'AI Agent 3维度评估框架' COMMENT '评估框架',
    requirement_document LONGTEXT COMMENT '需求文档内容',
    ai_agent_config JSON COMMENT 'AI代理配置信息',
    user_persona_info JSON COMMENT '用户画像信息',
    evaluation_summary JSON COMMENT '评估汇总数据',
    recommendations TEXT COMMENT '改进建议',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at),
    INDEX idx_evaluation_mode (evaluation_mode),
    INDEX idx_overall_score (overall_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI评估会话主表';

-- 2. 对话场景表
CREATE TABLE ai_conversation_scenarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL COMMENT '关联会话ID',
    scenario_index INT NOT NULL COMMENT '场景序号',
    scenario_title VARCHAR(200) NOT NULL COMMENT '场景标题',
    scenario_context TEXT COMMENT '场景背景描述',
    user_profile TEXT COMMENT '用户画像描述',
    scenario_score DECIMAL(3,2) NOT NULL COMMENT '场景得分(1-5)',
    conversation_turns INT NOT NULL DEFAULT 0 COMMENT '对话轮数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_scenario (session_id, scenario_index),
    INDEX idx_scenario_score (scenario_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话场景表';

-- 3. 对话记录表
CREATE TABLE ai_conversation_turns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL COMMENT '关联会话ID',
    scenario_id INT NOT NULL COMMENT '关联场景ID',
    turn_number INT NOT NULL COMMENT '对话轮次',
    user_message TEXT NOT NULL COMMENT '用户消息',
    enhanced_message TEXT COMMENT '增强后的用户消息(含上下文)',
    ai_response LONGTEXT NOT NULL COMMENT 'AI回复内容',
    response_length INT COMMENT 'AI回复长度',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id) REFERENCES ai_conversation_scenarios(id) ON DELETE CASCADE,
    INDEX idx_session_scenario_turn (session_id, scenario_id, turn_number),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话记录表';

-- 4. 评估维度得分表
CREATE TABLE ai_evaluation_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL COMMENT '关联会话ID',
    scenario_id INT NOT NULL COMMENT '关联场景ID',
    dimension_name VARCHAR(50) NOT NULL COMMENT '评估维度名称',
    dimension_label VARCHAR(100) NOT NULL COMMENT '维度中文标签',
    score DECIMAL(3,2) NOT NULL COMMENT '维度得分(1-5)',
    detailed_analysis LONGTEXT COMMENT '详细分析内容',
    specific_quotes TEXT COMMENT '具体对话引用',
    improvement_suggestions TEXT COMMENT '改进建议',
    full_response LONGTEXT COMMENT 'DeepSeek完整回复',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id) REFERENCES ai_conversation_scenarios(id) ON DELETE CASCADE,
    INDEX idx_session_scenario_dimension (session_id, scenario_id, dimension_name),
    INDEX idx_dimension_score (dimension_name, score),
    INDEX idx_score (score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评估维度得分表';

-- 5. 系统配置表
CREATE TABLE ai_evaluation_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL COMMENT '配置项键名',
    config_value TEXT NOT NULL COMMENT '配置项值',
    config_type ENUM('string', 'json', 'number', 'boolean') DEFAULT 'string' COMMENT '配置类型',
    description TEXT COMMENT '配置描述',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_key (config_key),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 6. 评估报告下载记录表
CREATE TABLE ai_report_downloads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL COMMENT '关联会话ID',
    download_format ENUM('json', 'txt', 'docx') NOT NULL COMMENT '下载格式',
    include_transcript BOOLEAN DEFAULT FALSE COMMENT '是否包含对话记录',
    file_size INT COMMENT '文件大小(字节)',
    download_ip VARCHAR(45) COMMENT '下载IP地址',
    user_agent TEXT COMMENT '用户代理字符串',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_download_format (download_format),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报告下载记录表';

-- 插入默认系统配置
INSERT INTO ai_evaluation_configs (config_key, config_value, config_type, description) VALUES
('system_version', '4.0.0', 'string', '系统版本号'),
('max_scenarios_per_session', '10', 'number', '每次评估最大场景数'),
('max_turns_per_scenario', '10', 'number', '每个场景最大对话轮数'),
('default_evaluation_framework', 'AI Agent 3维度评估框架', 'string', '默认评估框架'),
('enable_auto_save', 'true', 'boolean', '是否启用自动保存评估结果'),
('data_retention_days', '365', 'number', '数据保留天数'),
('enable_download_tracking', 'true', 'boolean', '是否启用下载跟踪');

-- 创建视图：评估汇总统计
CREATE VIEW v_evaluation_summary AS
SELECT 
    es.session_id,
    es.overall_score,
    es.total_scenarios,
    es.total_conversations,
    es.evaluation_mode,
    es.created_at,
    AVG(esc.scenario_score) as avg_scenario_score,
    COUNT(DISTINCT ecs.dimension_name) as evaluated_dimensions,
    AVG(ecs.score) as avg_dimension_score,
    JSON_EXTRACT(es.user_persona_info, '$.user_persona.role') as user_role,
    JSON_EXTRACT(es.user_persona_info, '$.usage_context.business_domain') as business_domain
FROM ai_evaluation_sessions es
LEFT JOIN ai_conversation_scenarios acs ON es.session_id = acs.session_id  
LEFT JOIN ai_evaluation_scores ecs ON es.session_id = ecs.session_id
GROUP BY es.session_id, es.overall_score, es.total_scenarios, es.total_conversations, es.evaluation_mode, es.created_at;

-- 创建存储过程：保存完整评估结果
DELIMITER //
CREATE PROCEDURE SaveEvaluationResult(
    IN p_session_id VARCHAR(100),
    IN p_evaluation_data JSON
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- 插入或更新主评估记录
    INSERT INTO ai_evaluation_sessions (
        session_id, overall_score, total_scenarios, total_conversations,
        evaluation_mode, evaluation_framework, requirement_document,
        ai_agent_config, user_persona_info, evaluation_summary, recommendations
    ) VALUES (
        p_session_id,
        JSON_EXTRACT(p_evaluation_data, '$.evaluation_summary.overall_score'),
        JSON_EXTRACT(p_evaluation_data, '$.evaluation_summary.total_scenarios'),
        JSON_EXTRACT(p_evaluation_data, '$.evaluation_summary.total_conversations'),
        JSON_UNQUOTE(JSON_EXTRACT(p_evaluation_data, '$.evaluation_mode')),
        JSON_UNQUOTE(JSON_EXTRACT(p_evaluation_data, '$.evaluation_summary.framework')),
        JSON_UNQUOTE(JSON_EXTRACT(p_evaluation_data, '$.requirement_document')),
        JSON_EXTRACT(p_evaluation_data, '$.ai_agent_config'),
        JSON_EXTRACT(p_evaluation_data, '$.user_persona_info'),
        JSON_EXTRACT(p_evaluation_data, '$.evaluation_summary'),
        JSON_EXTRACT(p_evaluation_data, '$.recommendations')
    ) ON DUPLICATE KEY UPDATE
        overall_score = VALUES(overall_score),
        total_scenarios = VALUES(total_scenarios),
        total_conversations = VALUES(total_conversations),
        evaluation_summary = VALUES(evaluation_summary),
        recommendations = VALUES(recommendations),
        updated_at = CURRENT_TIMESTAMP;
    
    COMMIT;
END //
DELIMITER ;

-- 创建函数：生成评估会话ID
DELIMITER //
CREATE FUNCTION GenerateSessionId() RETURNS VARCHAR(100)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE session_id VARCHAR(100);
    DECLARE counter INT DEFAULT 0;
    
    REPEAT
        SET session_id = CONCAT('EVAL_', DATE_FORMAT(NOW(), '%Y%m%d'), '_', 
                                LPAD(FLOOR(RAND() * 999999), 6, '0'));
        SET counter = counter + 1;
    UNTIL NOT EXISTS (SELECT 1 FROM ai_evaluation_sessions WHERE session_id = session_id) 
          OR counter > 100
    END REPEAT;
    
    RETURN session_id;
END //
DELIMITER ;

-- 创建索引优化查询性能
CREATE INDEX idx_evaluation_sessions_score_date ON ai_evaluation_sessions(overall_score, created_at);
CREATE INDEX idx_evaluation_sessions_mode_date ON ai_evaluation_sessions(evaluation_mode, created_at);
CREATE INDEX idx_conversation_scenarios_score ON ai_conversation_scenarios(scenario_score);
CREATE INDEX idx_evaluation_scores_dimension_score ON ai_evaluation_scores(dimension_name, score);

-- 数据库维护脚本
-- 清理过期数据（保留365天）
CREATE EVENT ev_cleanup_old_data
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    DELETE FROM ai_evaluation_sessions 
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 365 DAY);
END;

-- 启用事件调度器
SET GLOBAL event_scheduler = ON; 