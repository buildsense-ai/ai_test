import pymysql

print("Creating tables...")

try:
    conn = pymysql.connect(
        host='gz-cdb-e0aa423v.sql.tencentcdb.com',
        port=20236,
        user='root',
        password='Aa@114514',
        database='ai_evaluation_db',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # Create sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_evaluation_sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(100) UNIQUE NOT NULL,
        overall_score DECIMAL(3,2) NOT NULL,
        total_scenarios INT NOT NULL DEFAULT 0,
        total_conversations INT NOT NULL DEFAULT 0,
        evaluation_mode ENUM('manual', 'auto', 'dynamic') NOT NULL,
        evaluation_framework VARCHAR(100) DEFAULT 'AI Agent 3维度评估框架',
        requirement_document LONGTEXT,
        ai_agent_config JSON,
        user_persona_info JSON,
        evaluation_summary JSON,
        recommendations TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("✅ Created ai_evaluation_sessions")
    
    # Create configs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_evaluation_configs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        config_key VARCHAR(100) UNIQUE NOT NULL,
        config_value TEXT NOT NULL,
        config_type ENUM('string', 'json', 'number', 'boolean') DEFAULT 'string',
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("✅ Created ai_evaluation_configs")
    
    # Create scenarios table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_conversation_scenarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(100) NOT NULL,
        scenario_index INT NOT NULL,
        scenario_title VARCHAR(200) NOT NULL,
        scenario_context TEXT,
        user_profile TEXT,
        scenario_score DECIMAL(3,2) NOT NULL,
        conversation_turns INT NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("✅ Created ai_conversation_scenarios")
    
    # Create turns table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_conversation_turns (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(100) NOT NULL,
        scenario_id INT NOT NULL,
        turn_number INT NOT NULL,
        user_message TEXT NOT NULL,
        enhanced_message TEXT,
        ai_response LONGTEXT NOT NULL,
        response_length INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) ON DELETE CASCADE,
        FOREIGN KEY (scenario_id) REFERENCES ai_conversation_scenarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("✅ Created ai_conversation_turns")
    
    # Create scores table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_evaluation_scores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(100) NOT NULL,
        scenario_id INT NOT NULL,
        dimension_name VARCHAR(50) NOT NULL,
        dimension_label VARCHAR(100) NOT NULL,
        score DECIMAL(3,2) NOT NULL,
        detailed_analysis LONGTEXT,
        specific_quotes TEXT,
        improvement_suggestions TEXT,
        full_response LONGTEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) ON DELETE CASCADE,
        FOREIGN KEY (scenario_id) REFERENCES ai_conversation_scenarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("✅ Created ai_evaluation_scores")
    
    # Create downloads table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_report_downloads (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(100) NOT NULL,
        download_format ENUM('json', 'txt', 'docx') NOT NULL,
        include_transcript BOOLEAN DEFAULT FALSE,
        file_size INT,
        download_ip VARCHAR(45),
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("✅ Created ai_report_downloads")
    
    # Insert default configs
    cursor.execute("""
    INSERT IGNORE INTO ai_evaluation_configs (config_key, config_value, config_type, description) VALUES
    ('system_version', '4.1.0', 'string', '系统版本号'),
    ('enable_auto_save', 'true', 'boolean', '是否启用自动保存评估结果'),
    ('enable_download_tracking', 'true', 'boolean', '是否启用下载跟踪')
    """)
    print("✅ Inserted default configs")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("🎉 All tables created successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}") 