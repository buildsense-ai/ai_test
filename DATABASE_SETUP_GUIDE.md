# 🚀 AI评估平台数据库设置指南

## 📋 问题解决

### ✅ 已解决的问题
- **PyMySQL安装**: ✅ 已添加到requirements.txt并安装
- **API配置**: ✅ DeepSeek API密钥已恢复
- **数据库连接**: ✅ 腾讯云数据库配置已更新

### ❌ 需要手动操作
- **数据库创建**: 需要在腾讯云MySQL中创建数据库
- **表结构**: 需要执行SQL脚本创建表

---

## 🛠️ 完整设置步骤

### 第1步: 在MySQL Workbench中创建数据库

1. **连接到腾讯云数据库**:
   ```
   主机: gz-cdb-e0aa423v.sql.tencentcdb.com
   端口: 20236
   用户名: root
   密码: Aa@114514
   ```

2. **创建数据库**:
   ```sql
   CREATE DATABASE ai_evaluation_db 
   CHARACTER SET utf8mb4 
   COLLATE utf8mb4_unicode_ci;
   ```

3. **选择数据库**:
   ```sql
   USE ai_evaluation_db;
   ```

### 第2步: 执行表结构创建

**方式一: 使用修正的SQL文件**
1. 打开 `database_schema_fixed.sql` 文件
2. 在MySQL Workbench中逐个执行SQL语句

**方式二: 手动复制执行**
复制下面的SQL并在MySQL Workbench中执行:

```sql
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
    INDEX idx_session_scenario (session_id, scenario_index),
    INDEX idx_scenario_score (scenario_score),
    CONSTRAINT fk_scenarios_session 
        FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) 
        ON DELETE CASCADE ON UPDATE CASCADE
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
    INDEX idx_session_scenario_turn (session_id, scenario_id, turn_number),
    INDEX idx_created_at (created_at),
    CONSTRAINT fk_turns_session 
        FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_turns_scenario 
        FOREIGN KEY (scenario_id) REFERENCES ai_conversation_scenarios(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
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
    INDEX idx_session_scenario_dimension (session_id, scenario_id, dimension_name),
    INDEX idx_dimension_score (dimension_name, score),
    INDEX idx_score (score),
    CONSTRAINT fk_scores_session 
        FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_scores_scenario 
        FOREIGN KEY (scenario_id) REFERENCES ai_conversation_scenarios(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
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
    INDEX idx_session_id (session_id),
    INDEX idx_download_format (download_format),
    INDEX idx_created_at (created_at),
    CONSTRAINT fk_downloads_session 
        FOREIGN KEY (session_id) REFERENCES ai_evaluation_sessions(session_id) 
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='报告下载记录表';

-- 插入默认系统配置
INSERT INTO ai_evaluation_configs (config_key, config_value, config_type, description) VALUES
('system_version', '4.1.0', 'string', '系统版本号'),
('max_scenarios_per_session', '10', 'number', '每次评估最大场景数'),
('max_turns_per_scenario', '10', 'number', '每个场景最大对话轮数'),
('default_evaluation_framework', 'AI Agent 3维度评估框架', 'string', '默认评估框架'),
('enable_auto_save', 'true', 'boolean', '是否启用自动保存评估结果'),
('data_retention_days', '365', 'number', '数据保留天数'),
('enable_download_tracking', 'true', 'boolean', '是否启用下载跟踪');
```

### 第3步: 验证设置

1. **运行测试脚本**:
   ```bash
   python test_complete_setup.py
   ```

2. **预期结果**:
   ```
   🧪 AI评估平台完整设置测试
   🔍 1. 测试PyMySQL导入...
      ✅ PyMySQL导入成功
   
   🔍 2. 测试数据库连接...
      ✅ 数据库连接成功
      📊 MySQL版本: 8.0.xx
   
   🔍 3. 测试数据库表结构...
      ✅ 找到 6 个数据表:
      📊 ai_conversation_scenarios - 对话场景表
      📊 ai_conversation_turns - 对话记录表
      📊 ai_evaluation_configs - 系统配置表
      📊 ai_evaluation_scores - 评估维度得分表
      📊 ai_evaluation_sessions - AI评估会话主表
      📊 ai_report_downloads - 报告下载记录表
   
   🔍 4. 测试系统配置数据...
      ✅ 找到 7 个配置项
   
   🔍 5. 测试数据库保存功能...
      ✅ 生成会话ID: EVAL_20241215_123456
      ✅ 测试数据保存成功
   
   🏁 测试结果: 5/5 通过
   🎉 所有测试通过！系统准备就绪
   ```

### 第4步: 启动服务

```bash
python main.py
```

**预期输出**:
```
📝 Configuration loaded: DeepSeek API key configured
✅ Configuration loaded from config.py - DeepSeek API configured
🚀 AI Agent评估平台启动在端口 8000
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**不再出现**: `⚠️ PyMySQL not available. Database features disabled.`

---

## ✨ 新功能确认

### 🆕 自动数据库保存
- **评估完成时**: 自动保存评估结果到数据库
- **报告下载时**: 自动记录下载活动
- **会话管理**: 每次评估生成唯一会话ID

### 📊 数据持久化
- **完整评估数据**: 会话、场景、对话、评分全部保存
- **历史查询**: 支持按时间、评分、模式等查询
- **数据分析**: 视图支持统计分析

### 🎯 增强报告生成
- **自动触发保存**: 生成报告时自动保存到数据库
- **下载追踪**: 记录所有报告下载活动
- **多格式支持**: JSON、TXT、DOCX格式

---

## 🔧 故障排除

### 问题1: 数据库连接失败
**解决方案**:
1. 检查网络连接
2. 验证数据库服务器是否运行
3. 确认防火墙设置
4. 验证用户名密码

### 问题2: 表不存在错误
**解决方案**:
1. 确认已创建数据库 `ai_evaluation_db`
2. 完整执行表结构SQL
3. 检查外键约束是否正确

### 问题3: PyMySQL导入失败
**解决方案**:
```bash
pip install PyMySQL==1.1.0
```

---

## 📈 系统状态

- ✅ **PyMySQL**: 已安装并可用
- ✅ **配置文件**: DeepSeek API密钥和数据库连接已配置
- ✅ **代码更新**: 报告生成时自动保存到数据库
- 🔄 **数据库**: 需要手动创建（见上述步骤）

完成数据库设置后，您的AI评估平台将具备完整的数据持久化能力！ 