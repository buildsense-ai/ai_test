# 🚀 AI Agent 自动化评估平台 - 部署指南

## 📋 项目概述

这是一个基于 DeepSeek 智能引擎的专业 AI 代理评估系统，支持：
- 多平台 API 集成 (Coze、Dify、自定义 API)
- 文档智能解析与用户画像提取
- 4维度评估框架 (模糊理解、回答准确性、用户匹配度、目标对齐度)
- 动态对话流程与工作流兼容

## 🛠️ 部署前准备

### 系统要求
- Python 3.8+
- SQLite 3.x (或其他数据库)
- 8GB+ RAM (推荐)
- 2GB+ 磁盘空间

### 必需的 API 密钥
1. **DeepSeek API Key** (必需)
   - 获取地址: https://platform.deepseek.com
   - 用于用户画像提取和智能评估

2. **AI 平台 API** (至少一个)
   - Coze API Token (推荐)
   - Dify API Token  
   - 其他自定义 API

## 🚀 快速部署

### 1. 克隆项目
```bash
git clone <repository-url>
cd ai_test
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境
复制并编辑配置文件:
```bash
cp config.py config_local.py
```

编辑 `config_local.py`:
```python
# 必需配置
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"

# 可选配置 (根据需要)
COZE_API_TOKEN = "your_coze_token_here"
DEFAULT_COZE_BOT_ID = "your_coze_bot_id"

# 数据库配置 (可选，默认使用 SQLite)
DATABASE_URL = "sqlite:///evaluation_platform.db"

# 服务器配置
DEFAULT_PORT = 8000
DEBUG_MODE = False  # 生产环境设为 False
```

### 4. 初始化数据库
```bash
python simple_create_tables.py
```

### 5. 启动服务
```bash
python main.py
```

服务将在 http://localhost:8000 启动

## 🐳 Docker 部署

### 使用 Docker 快速部署
```bash
# 构建镜像
docker build -t ai-evaluation-platform .

# 运行容器
docker run -d \
  --name ai-eval-platform \
  -p 8000:8000 \
  -e DEEPSEEK_API_KEY="your_key_here" \
  -e COZE_API_TOKEN="your_token_here" \
  ai-evaluation-platform
```

### 使用 docker-compose (推荐)
创建 `docker-compose.yml`:
```yaml
version: '3.8'
services:
  ai-evaluation:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - COZE_API_TOKEN=${COZE_API_TOKEN}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

启动:
```bash
docker-compose up -d
```

## ⚙️ 配置说明

### 核心配置项
```python
# config.py 中的关键配置

# DeepSeek API (必需)
DEEPSEEK_API_KEY = "sk-xxx"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_TIMEOUT = 60

# Coze API (可选)
COZE_API_TOKEN = "pat_xxx"
DEFAULT_COZE_BOT_ID = "7511993619423985674"
COZE_API_BASE = "https://api.coze.cn/open_api"

# 数据库配置
DATABASE_PATH = "evaluation_platform.db"

# 服务器配置
DEFAULT_PORT = 8000
```

### 支持的 AI 平台

#### 1. Coze 平台
```json
{
  "type": "coze-bot",
  "botId": "your_bot_id",
  "headers": {
    "Authorization": "Bearer your_coze_token"
  }
}
```

#### 2. Dify 平台
```json
{
  "type": "custom-api",
  "url": "http://your-dify-api.com/v1/chat-messages",
  "headers": {
    "Authorization": "Bearer app-xxx",
    "Content-Type": "application/json"
  }
}
```

#### 3. 自定义 API
```json
{
  "type": "custom-api",
  "url": "https://api.example.com/chat",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer your_token",
    "Content-Type": "application/json"
  }
}
```

## 📊 使用流程

### 1. 准备需求文档
支持格式：`.docx`, `.pdf`, `.txt`

### 2. 选择评估模式
- **智能提取模式**: 自动提取用户画像
- **动态对话模式**: 真实对话流程 (推荐)
- **手动配置模式**: 自定义场景

### 3. 配置 AI 系统
根据你使用的 AI 平台配置相应参数

### 4. 开始评估
系统将自动进行多轮对话并生成详细报告

## 🔧 故障排查

### 常见问题

#### 1. DeepSeek API 调用失败
```bash
# 检查 API Key 是否正确
curl -H "Authorization: Bearer your_key" https://api.deepseek.com/v1/models
```

#### 2. 数据库连接问题
```bash
# 重新初始化数据库
python simple_create_tables.py
```

#### 3. 端口占用
```bash
# 检查端口占用
lsof -i :8000

# 使用其他端口
python main.py --port 8001
```

#### 4. 内存不足
- 推荐至少 8GB RAM
- 可以调整 `config.py` 中的 `MAX_CONCURRENT_EVALUATIONS`

### 日志调试
查看详细日志:
```bash
# 检查应用日志
tail -f logs/application.log

# 检查调试日志
cat AI评估平台调试日志.md
```

## 🛡️ 安全注意事项

1. **API 密钥安全**
   - 不要将 API 密钥提交到代码仓库
   - 使用环境变量或配置文件管理
   - 定期轮换 API 密钥

2. **网络安全**
   - 生产环境使用 HTTPS
   - 配置防火墙规则
   - 限制访问 IP 范围

3. **数据安全**
   - 定期备份数据库
   - 敏感数据加密存储
   - 遵守数据保护法规

## 📈 性能优化

### 1. 数据库优化
```sql
-- 创建索引 (已在 database_schema_fixed.sql 中)
CREATE INDEX idx_session_timestamp ON evaluation_sessions(timestamp);
CREATE INDEX idx_download_session ON download_records(session_id);
```

### 2. 缓存配置
可以添加 Redis 缓存提升性能:
```python
# 在 config.py 中添加
REDIS_URL = "redis://localhost:6379/0"
CACHE_TTL = 3600  # 1小时
```

### 3. 负载均衡
生产环境推荐使用 Nginx + Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

## 📚 相关文档

- `README.md` - 项目总体介绍
- `AI评估平台调试日志.md` - 详细调试记录
- `代码功能总结.md` - 功能特性说明
- `未来改进方向计划.md` - 发展规划
- `DATABASE_SETUP_GUIDE.md` - 数据库设置指南

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 技术支持

如遇问题，请参考：
1. 本部署指南
2. 调试日志文件
3. 提交 GitHub Issue
4. 联系项目维护团队

---

**部署成功后，访问 http://your-server:8000 开始使用！** 🎉 