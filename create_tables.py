#!/usr/bin/env python3
# 自动创建数据库表结构脚本

import pymysql
import sys

def create_all_tables():
    """自动创建所有数据库表"""
    print("🚀 开始创建AI评估平台数据库表结构...")
    
    # 连接数据库
    try:
        connection = pymysql.connect(
            host='gz-cdb-e0aa423v.sql.tencentcdb.com',
            port=20236,
            user='root',
            password='Aa@114514',
            database='ai_evaluation_db',
            charset='utf8mb4',
            autocommit=True
        )
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    cursor = connection.cursor()
    
    # 表创建SQL列表
    table_sqls = [
        # 1. 评估会话主表
        """
        CREATE TABLE IF NOT EXISTS ai_evaluation_sessions (
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI评估会话主表'
        """,
        
        # 2. 对话场景表
        """
        CREATE TABLE IF NOT EXISTS ai_conversation_scenarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(100) NOT NULL COMMENT '关联会话ID',
            scenario_index INT NOT NULL COMMENT '场景序号',
            scenario_title VARCHAR(200) NOT NULL COMMENT '场景标题',
            scenario_context TEXT COMMENT '场景背景描述',
            user_profile TEXT COMMENT '用户画像描述',
            scenario_score DECIMAL(3,2) NOT NULL COMMENT '场景得分(1-5)',
            conversation_turns INT NOT NULL DEFAULT 0 COMMENT '对话轮数',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_session_scenario (session_id, scenario_index),
            INDEX idx_scenario_score (scenario_score),
            CONSTRAINT fk_scenarios_session 
                FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) 
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话场景表'
        """,
        
        # 3. 对话记录表
        """
        CREATE TABLE IF NOT EXISTS ai_conversation_turns (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(100) NOT NULL COMMENT '关联会话ID',
            scenario_id INT NOT NULL COMMENT '关联场景ID',
            turn_number INT NOT NULL COMMENT '对话轮次',
            user_message TEXT NOT NULL COMMENT '用户消息',
            enhanced_message TEXT COMMENT '增强后的用户消息(含上下文)',
            ai_response LONGTEXT NOT NULL COMMENT 'AI回复内容',
            response_length INT COMMENT 'AI回复长度',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_session_scenario_turn (session_id, scenario_id, turn_number),
            INDEX idx_created_at (created_at),
            CONSTRAINT fk_turns_session 
                FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) 
                ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fk_turns_scenario 
                FOREIGN KEY (scenario_id) REFERENCES ai_conversation_scenarios(id) 
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话记录表'
        """,
        
        # 4. 评估维度得分表
        """
        CREATE TABLE IF NOT EXISTS ai_evaluation_scores (
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
            INDEX idx_session_scenario_dimension (session_id, scenario_id, dimension_name),
            INDEX idx_dimension_score (dimension_name, score),
            INDEX idx_score (score),
            CONSTRAINT fk_scores_session 
                FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) 
                ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT fk_scores_scenario 
                FOREIGN KEY (scenario_id) REFERENCES ai_conversation_scenarios(id) 
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评估维度得分表'
        """,
        
        # 5. 系统配置表
        """
        CREATE TABLE IF NOT EXISTS ai_evaluation_configs (
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表'
        """,
        
        # 6. 报告下载记录表
        """
        CREATE TABLE IF NOT EXISTS ai_report_downloads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(100) NOT NULL COMMENT '关联会话ID',
            download_format ENUM('json', 'txt', 'docx') NOT NULL COMMENT '下载格式',
            include_transcript BOOLEAN DEFAULT FALSE COMMENT '是否包含对话记录',
            file_size INT COMMENT '文件大小(字节)',
            download_ip VARCHAR(45) COMMENT '下载IP地址',
            user_agent TEXT COMMENT '用户代理字符串',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_session_id (session_id),
            INDEX idx_download_format (download_format),
            INDEX idx_created_at (created_at),
            CONSTRAINT fk_downloads_session 
                FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) 
                ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报告下载记录表'
        """
    ]
    
    # 执行表创建
    table_names = [
        'ai_evaluation_sessions',
        'ai_conversation_scenarios', 
        'ai_conversation_turns',
        'ai_evaluation_scores',
        'ai_evaluation_configs',
        'ai_report_downloads'
    ]
    
    success_count = 0
    for i, sql in enumerate(table_sqls):
        try:
            cursor.execute(sql)
            print(f"✅ 创建表 {table_names[i]} 成功")
            success_count += 1
        except Exception as e:
            print(f"❌ 创建表 {table_names[i]} 失败: {e}")
    
    # 插入默认配置数据
    print("\n📝 插入默认系统配置...")
    config_sql = """
    INSERT IGNORE INTO ai_evaluation_configs (config_key, config_value, config_type, description) VALUES
    ('system_version', '4.1.0', 'string', '系统版本号'),
    ('max_scenarios_per_session', '10', 'number', '每次评估最大场景数'),
    ('max_turns_per_scenario', '10', 'number', '每个场景最大对话轮数'),
    ('default_evaluation_framework', 'AI Agent 3维度评估框架', 'string', '默认评估框架'),
    ('enable_auto_save', 'true', 'boolean', '是否启用自动保存评估结果'),
    ('data_retention_days', '365', 'number', '数据保留天数'),
    ('enable_download_tracking', 'true', 'boolean', '是否启用下载跟踪')
    """
    
    try:
        cursor.execute(config_sql)
        print("✅ 默认配置插入成功")
    except Exception as e:
        print(f"❌ 配置插入失败: {e}")
    
    # 创建视图
    print("\n🔍 创建统计视图...")
    view_sql = """
    CREATE OR REPLACE VIEW v_evaluation_summary AS
    SELECT 
        es.session_id,
        es.overall_score,
        es.total_scenarios,
        es.total_conversations,
        es.evaluation_mode,
        es.created_at,
        COALESCE(AVG(acs.scenario_score), 0) as avg_scenario_score,
        COUNT(DISTINCT ecs.dimension_name) as evaluated_dimensions,
        COALESCE(AVG(ecs.score), 0) as avg_dimension_score
    FROM ai_evaluation_sessions es
    LEFT JOIN ai_conversation_scenarios acs ON es.session_id = acs.session_id  
    LEFT JOIN ai_evaluation_scores ecs ON es.session_id = ecs.session_id
    GROUP BY es.session_id, es.overall_score, es.total_scenarios, es.total_conversations, es.evaluation_mode, es.created_at
    """
    
    try:
        cursor.execute(view_sql)
        print("✅ 统计视图创建成功")
    except Exception as e:
        print(f"❌ 视图创建失败: {e}")
    
    # 验证创建结果
    print("\n🔍 验证表创建结果...")
    cursor.execute("""
        SELECT TABLE_NAME, TABLE_COMMENT 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'ai_evaluation_db' 
          AND TABLE_NAME LIKE 'ai_%'
        ORDER BY TABLE_NAME
    """)
    
    tables = cursor.fetchall()
    print(f"✅ 成功创建 {len(tables)} 个表:")
    for table_name, comment in tables:
        print(f"   📊 {table_name} - {comment}")
    
    cursor.close()
    connection.close()
    
    print(f"\n🎉 数据库表结构创建完成！成功创建 {success_count}/{len(table_sqls)} 个表")
    return success_count == len(table_sqls)

if __name__ == "__main__":
    print("=" * 60)
    print("🏗️  AI评估平台数据库表结构自动创建")
    print("=" * 60)
    
    success = create_all_tables()
    
    if success:
        print("\n✅ 所有表创建成功！现在可以运行完整测试:")
        print("   python test_complete_setup.py")
        sys.exit(0)
    else:
        print("\n❌ 部分表创建失败，请检查错误信息")
        sys.exit(1) 