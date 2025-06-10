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
DEEPSEEK_API_KEY = "your_deepseek_api_key"

# 可选配置 (根据需要)
COZE_API_TOKEN = "your_coze_token"
DEFAULT_COZE_BOT_ID = "your_bot_id"

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
  -e DEEPSEEK_API_KEY="your_key" \
  -e COZE_API_TOKEN="your_token" \
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

## 🎯 **关键部署成功要点 - Cursor AI 必读**

> **⚠️ 重要提示**: 以下检查点是基于实际生产环境故障分析总结，Cursor在未来的代码修改中必须遵循这些原则，确保部署后系统稳定运行。

### ✅ **全面安全与稳定性修复** - 2024-12-19

**修复状态**: 🟢 **已完全修复并验证**

#### **已修复的关键问题**:

1. **ERR_EMPTY_RESPONSE 超时问题** ✅
   - 前端所有fetch调用添加AbortSignal.timeout()
   - 动态评估: 10分钟，其他评估: 8分钟，下载: 2分钟

2. **安全漏洞修复** ✅
   - 文件上传路径遍历防护
   - 危险文件扩展名阻止
   - API URL安全验证
   - 用户输入清理和长度限制

3. **资源管理优化** ✅
   - 内存使用监控 (85%警告, 95%阻止)
   - 文件大小严格限制 (10MB)
   - 配置化常量替代硬编码值

4. **错误处理增强** ✅
   - 统一HTTPException格式
   - 详细错误信息和建议
   - 优雅的降级处理

5. **数据库安全** ✅
   - 参数化查询防止SQL注入
   - 连接池配置优化
   - 事务回滚保护

运行验证命令确认修复:
```bash
python test_comprehensive_fixes.py
```

预期输出: `✅ All comprehensive fixes verified! Your deployment should be much more robust.`

### 1. **防止 ERR_EMPTY_RESPONSE 的关键配置** ⭐⭐⭐

#### A. 前后端超时配置一致性检查
```javascript
// 前端 JavaScript - 必须确保超时设置合理
const response = await fetch('/api/evaluate-agent-dynamic', {
    method: 'POST',
    body: formData,
    // ⭐ 关键：前端超时必须大于后端超时
    signal: AbortSignal.timeout(600000)  // 10分钟前端超时
});
```

```python
# 后端 Python - 对应的超时配置
EVALUATION_TIMEOUT = 480  # 8分钟后端处理超时
DEFAULT_TIMEOUT = 120     # 2分钟API调用超时
```

#### B. API配置结构验证 - 防止解析失败
```python
# main.py 中必须包含的配置清理逻辑
def clean_api_config(api_config_dict):
    """清理和验证API配置，防止解析失败"""
    # 1. 确保timeout是整数
    if 'timeout' in api_config_dict:
        try:
            api_config_dict['timeout'] = int(api_config_dict['timeout'])
        except (ValueError, TypeError):
            api_config_dict['timeout'] = 30
    
    # 2. 确保headers是字典
    if 'headers' in api_config_dict and not isinstance(api_config_dict['headers'], dict):
        api_config_dict['headers'] = {}
    
    # 3. 移除包装层
    if 'config' in api_config_dict and isinstance(api_config_dict['config'], dict):
        api_config_dict = api_config_dict['config']
    
    return api_config_dict
```

### 2. **资源限制与内存管理** ⭐⭐

#### A. 文件上传大小强制检查
```python
# 每个文件处理函数必须包含的检查
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB严格限制

async def process_uploaded_document_improved(file: UploadFile) -> str:
    # ⭐ 必需：文件大小检查
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="文件大小超过10MB限制")
    
    # ⭐ 必需：文件类型验证
    allowed_extensions = ['.docx', '.pdf', '.txt']
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_extension}")
```

#### B. 内存使用监控
```python
# 在长时间处理任务中添加内存检查
import psutil

def check_memory_usage():
    """检查内存使用，防止OOM"""
    memory_percent = psutil.virtual_memory().percent
    if memory_percent > 85:  # 超过85%内存使用
        raise HTTPException(status_code=507, detail="服务器内存不足，请稍后重试")
```

### 3. **错误处理与日志记录** ⭐⭐

#### A. 统一错误响应格式
```python
# 所有API端点必须使用统一的错误处理
from fastapi import HTTPException
from fastapi.responses import JSONResponse

async def handle_api_error(e: Exception, operation: str):
    """统一API错误处理，确保前端能收到有效响应"""
    error_message = f"{operation}失败: {str(e)}"
    logger.error(f"❌ {error_message}")
    logger.error(f"Full traceback: {traceback.format_exc()}")
    
    # 返回结构化错误响应
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": error_message,
            "timestamp": datetime.now().isoformat()
        }
    )
```

#### B. 关键操作日志记录
```python
# 每个关键操作必须包含的日志
logger.info(f"🚀 开始{operation_name}...")
print(f"🚀 开始{operation_name}...") # 同时输出到console便于调试

try:
    # 业务逻辑
    result = await process_operation()
    logger.info(f"✅ {operation_name}成功完成")
    print(f"✅ {operation_name}成功完成")
    return result
except Exception as e:
    logger.error(f"❌ {operation_name}失败: {str(e)}")
    print(f"❌ {operation_name}失败: {str(e)}")
    raise
```

### 4. **数据库连接稳定性** ⭐

#### A. 连接池配置
```python
# config.py 中必须包含的数据库连接池配置
DATABASE_CONFIG = {
    'host': 'your_host',
    'port': 20236,
    'user': 'root',
    'password': 'your_password',  
    'database': 'ai_evaluation_db',
    'charset': 'utf8mb4',
    'autocommit': True,
    # ⭐ 关键：连接池参数
    'maxconnections': 20,    # 最大连接数
    'mincached': 2,          # 最小缓存连接
    'maxcached': 5,          # 最大缓存连接
    'blocking': True,        # 连接不足时是否阻塞
    'ping': 4               # 连接检查间隔
}
```

#### B. 数据库连接重试机制
```python
async def get_database_connection_with_retry(max_retries=3):
    """带重试机制的数据库连接"""
    for attempt in range(max_retries):
        try:
            conn = get_database_connection()
            if conn:
                return conn
        except Exception as e:
            logger.warning(f"数据库连接尝试 {attempt + 1} 失败: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 指数退避
    
    raise HTTPException(status_code=503, detail="数据库连接失败")
```

### 5. **API集成稳定性检查** ⭐

#### A. API调用重试机制
```python
async def call_external_api_with_retry(api_func, *args, max_retries=3, **kwargs):
    """外部API调用的统一重试机制"""
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            result = await api_func(*args, **kwargs)
            if result:  # 验证结果有效性
                return result
        except Exception as e:
            last_exception = e
            logger.warning(f"API调用尝试 {attempt + 1} 失败: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
    
    # 所有重试失败
    raise HTTPException(
        status_code=502, 
        detail=f"外部API调用失败: {str(last_exception)}"
    )
```

#### B. API密钥有效性检查
```python
async def validate_api_keys():
    """启动时验证所有API密钥"""
    checks = {
        "DeepSeek": test_deepseek_api,
        "Coze": test_coze_api
    }
    
    for service, test_func in checks.items():
        try:
            await test_func()
            print(f"✅ {service} API密钥有效")
        except Exception as e:
            print(f"❌ {service} API密钥无效: {str(e)}")
            logger.error(f"{service} API密钥验证失败: {str(e)}")
```

## 🚨 **Cursor AI 代码修改检查清单**

每次修改代码后，Cursor必须确保：

### ✅ **基础稳定性**
- [ ] 所有异步函数都有适当的超时设置
- [ ] 所有文件操作都有大小限制检查
- [ ] 所有外部API调用都有重试机制
- [ ] 所有数据库操作都有连接池管理

### ✅ **错误处理完整性**
- [ ] 每个API端点都有try-catch包装
- [ ] 错误信息对前端友好且信息充分
- [ ] 关键操作都有详细日志记录
- [ ] HTTP状态码使用正确

### ✅ **性能与资源**
- [ ] 长时间操作有进度反馈
- [ ] 内存使用有监控和限制
- [ ] 数据库查询有优化
- [ ] 缓存机制合理使用

### ✅ **前后端一致性**
- [ ] API请求/响应格式匹配
- [ ] 超时设置前后端协调
- [ ] 错误状态码前端正确处理
- [ ] 数据结构前后端一致

### ✅ **部署环境适配**
- [ ] 配置文件支持环境变量
- [ ] 依赖版本明确指定
- [ ] 启动脚本健壮性
- [ ] 监控和健康检查完备

## 🔍 **故障排查优先级**

遇到部署问题时，按以下顺序排查：

1. **首先检查**: 服务器资源 (内存、磁盘、网络)
2. **然后检查**: API密钥配置和网络连通性
3. **接着检查**: 数据库连接和权限
4. **最后检查**: 代码逻辑和依赖版本

## 🎯 **成功部署验证标准**

只有通过以下所有测试，才算部署成功：

1. **负载测试**: 能处理2个并发用户同时评估
2. **容错测试**: API临时失败能自动恢复
3. **边界测试**: 大文件上传被正确拒绝
4. **持久测试**: 连续运行24小时无内存泄漏

---

**⚠️ 重要**: 这些检查点是基于真实生产故障总结的，跳过任何一项都可能导致部署后出现 ERR_EMPTY_RESPONSE 或其他严重问题。

**部署成功后，访问 http://your-server:8000 开始使用！** 🎉 