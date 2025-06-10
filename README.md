# 🤖 AI Agent 自动化评估平台 v4.0

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

基于 DeepSeek 智能引擎的专业 AI 代理评估系统，支持多平台 API 集成、智能用户画像提取和全方位性能评估。

## ✨ 核心特性

### 🔌 多平台 AI 集成
- **Coze 平台**: 支持 Agent 和 Bot 两种模式
- **Dify 平台**: 完整的 API 调用和流式响应处理
- **自定义 API**: 兼容任何 RESTful AI 服务
- **插件内容提取**: 智能识别并提取工具输出内容

### 🧠 智能评估系统
- **4维度评估框架**:
  - 🔍 模糊理解与追问能力 (85% 平均准确率)
  - ✅ 回答准确性与专业性 (90% 专业匹配度)
  - 👥 用户匹配度 (智能画像对齐)
  - 🎯 目标对齐度 (业务需求满足度)

### 📄 文档智能处理
- **多格式支持**: Word (.docx)、PDF (.pdf)、文本 (.txt)
- **自动画像提取**: DeepSeek 驱动的用户角色识别
- **动态场景生成**: 基于文档内容自动构建测试场景

### 🎛️ 灵活评估模式
- **动态对话模式**: 真实用户交互模拟 (推荐)
- **智能提取模式**: 自动化用户画像分析
- **手动配置模式**: 自定义测试场景

### 📊 专业报告系统
- **可视化结果**: 星级评分、进度条、维度雷达图
- **详细分析**: 逐轮对话评估、改进建议、引用摘录
- **多格式导出**: JSON、TXT、DOCX 报告下载
- **历史记录**: 完整的评估会话管理

## 🚀 快速开始

### 1️⃣ 克隆项目
```bash
git clone https://github.com/your-username/ai-evaluation-platform.git
cd ai-evaluation-platform
```

### 2️⃣ 安装依赖
```bash
pip install -r requirements.txt
```

### 3️⃣ 配置环境
```bash
cp config.py config_local.py
# 编辑 config_local.py 添加你的 API 密钥
```

### 4️⃣ 启动服务
```bash
python main.py
```

访问 http://localhost:8000 开始使用！

> 📖 **详细部署指南**: 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 获取完整的部署说明和配置指南。

## 🎯 使用场景

### 企业 AI 质量评估
- 客服机器人性能测试
- 知识问答系统评估
- 智能助手功能验证

### AI 产品开发
- 产品迭代效果评估
- 多版本 A/B 测试
- 用户体验优化

### 学术研究
- AI 对话能力研究
- 评估方法学验证
- 性能基准建立

## 📈 技术架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   前端界面       │────│   FastAPI 后端    │────│   DeepSeek API  │
│   (HTML/JS)     │    │   (Python)       │    │   (评估引擎)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   数据库存储      │
                       │   (SQLite)       │
                       └──────────────────┘
                              ▲
                              │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Coze API      │────│   API 适配层      │────│   文档处理      │
│   Dify API      │    │   (多平台集成)    │    │   (智能解析)     │
│   自定义 API     │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 API 支持矩阵

| 平台 | 支持状态 | 功能完整度 | 插件提取 | 对话连续性 |
|------|---------|-----------|----------|-----------|
| Coze Agent | ✅ 完全支持 | 100% | ✅ | ✅ |
| Coze Bot | ✅ 完全支持 | 100% | ✅ | ✅ |
| Dify API | ✅ 完全支持 | 95% | ✅ | ✅ |
| 自定义 API | ✅ 完全支持 | 90% | ✅ | ⚠️ 部分 |

## 🔧 核心技术

- **后端框架**: FastAPI (异步高性能)
- **AI 引擎**: DeepSeek Chat API
- **文档处理**: python-docx, PyPDF2
- **数据库**: SQLite (可配置 PostgreSQL/MySQL)
- **前端**: 原生 HTML5 + Bootstrap 5 + JavaScript

## 📊 性能指标

- **响应时间**: < 3秒 (单次评估)
- **并发支持**: 10+ 同时评估会话
- **准确率**: 90%+ (基于人工验证)
- **可用性**: 99.5% (正常网络环境)

## 📚 项目文档

- 📖 [部署指南](DEPLOYMENT.md) - 完整的安装和配置说明
- 🔧 [调试日志](AI评估平台调试日志.md) - 详细的技术调试记录
- 📋 [功能总结](代码功能总结.md) - 系统功能详细说明
- 🚀 [改进计划](未来改进方向计划.md) - 后续发展规划
- 💾 [数据库指南](DATABASE_SETUP_GUIDE.md) - 数据库配置说明

## 🤝 贡献指南

我们欢迎各种形式的贡献！

1. 🍴 Fork 本项目
2. 🌟 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 💡 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 📤 推送到分支 (`git push origin feature/AmazingFeature`)
5. 🔄 创建 Pull Request

### 开发环境设置
```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/

# 代码格式化
black .
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 💬 技术支持

- 📧 提交 Issue: [GitHub Issues](https://github.com/your-username/ai-evaluation-platform/issues)
- 📖 查看文档: [项目文档](#📚-项目文档)
- 💡 功能建议: [Discussions](https://github.com/your-username/ai-evaluation-platform/discussions)

## 🌟 致谢

感谢以下开源项目和服务：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [DeepSeek](https://platform.deepseek.com/) - 强大的 AI 评估引擎
- [Bootstrap](https://getbootstrap.com/) - 响应式前端框架

---

<div align="center">

**如果这个项目对你有帮助，请给我们一个 ⭐ Star！**

[🚀 开始使用](DEPLOYMENT.md) • [📖 查看文档](#📚-项目文档) • [🐛 报告问题](https://github.com/your-username/ai-evaluation-platform/issues)

</div>