# �� AI Agent 自动化评估平台 v4.0

> **基于DeepSeek智能引擎的专业AI代理评估系统**  
> 支持多平台API • 文档智能解析 • 4维度评估框架 • 动态对话生成

![Platform](https://img.shields.io/badge/Platform-Web%20Application-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

## 📑 目录

- [功能概述](#-功能概述)
- [核心特性](#-核心特性)
- [技术架构](#-技术架构)
- [安装部署](#-安装部署)
- [使用指南](#-使用指南)
- [评估维度](#-评估维度)
- [API支持](#-api支持)
- [项目结构](#-项目结构)

## 🌟 功能概述

AI Agent 自动化评估平台是一套专业的AI代理评估解决方案，通过智能化的多轮对话测试，全面评估AI系统在真实场景下的表现。平台支持多种AI系统接入，提供4个维度的专业评估报告。

### 核心能力

- **🤖 智能用户画像提取** - 基于DeepSeek自动分析需求文档，提取用户角色特征
- **🗣️ 动态对话生成** - 真实模拟用户与AI的多轮交互，每轮问题基于前轮回答智能生成
- **📊 多维度评估** - 从模糊理解、回答准确性、用户匹配、目标对齐4个维度评估
- **📱 现代化界面** - 响应式设计，支持折叠式布局，提供专业的用户体验
- **🔌 多平台支持** - 支持Coze Agent、Coze Bot、自定义API等多种AI平台

## ✨ 核心特性

### 1. 三种评估模式

#### 🤖 智能提取模式
- 上传需求文档（Word/PDF/TXT）
- DeepSeek自动分析提取用户画像
- 基于画像生成测试场景

#### 🗣️ 动态对话模式 *（推荐）*
- 智能提取用户画像
- 自动生成2个测试场景
- 每轮对话基于AI回答动态生成后续问题
- 真实模拟用户-AI交互流程

#### ✋ 手动配置模式
- 手动设置用户角色和画像
- 自定义对话场景和测试轮次
- 适合特定场景的精确测试

### 2. 智能化评估引擎

#### 📈 四维度评估框架
- **🔍 模糊理解能力** - 评估AI对用户模糊描述的理解和澄清能力
- **✅ 回答准确性** - 评估AI回答的专业性和准确度
- **👥 用户匹配度** - 评估AI回答是否符合用户画像和沟通风格
- **🎯 目标对齐性** - 评估AI是否能帮助用户达成业务目标

#### 🧠 智能评估逻辑
- 每个维度提供详细评分理由
- 基于对话历史进行上下文分析
- 考虑用户画像的个性化评估
- 生成专业的改进建议

### 3. 现代化用户界面

#### 🎨 设计特色
- **折叠式卡片系统** - 清晰的信息层级，减少视觉干扰
- **紧凑布局设计** - 60%更少的视觉混乱，专业企业级外观
- **响应式适配** - 完美支持桌面端和移动端
- **智能交互** - 悬停效果、平滑动画、直观的状态反馈

#### 📊 结果展示
- 综合得分星级展示
- 维度评分可视化
- 折叠式对话记录
- 详细评估解释

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI** - 现代Python Web框架
- **DeepSeek API** - 智能分析和评估引擎
- **python-docx** - Word文档解析
- **PyPDF2** - PDF文档解析
- **aiohttp** - 异步HTTP客户端

### 前端技术栈
- **Bootstrap 5** - 响应式UI框架
- **Font Awesome** - 图标库
- **原生JavaScript** - 交互逻辑
- **CSS3** - 现代样式设计

### 核心组件
```
AI Agent 评估平台
├── 用户画像提取器 (DeepSeek)
├── 动态对话生成器 (DeepSeek)
├── 多平台API连接器
├── 4维度评估引擎
└── 现代化Web界面
```

## 🚀 安装部署

### 环境要求
- Python 3.8+
- 现代浏览器（Chrome、Firefox、Safari、Edge）

### 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd ai_test
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置API密钥**
```python
# 在main.py中配置DeepSeek API密钥
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"
```

4. **启动服务**
```bash
python main.py
```

5. **访问应用**
```
http://localhost:8000
```

### Docker部署

```bash
# 构建镜像
docker build -t ai-agent-evaluator .

# 运行容器
docker run -p 8000:8000 ai-agent-evaluator
```

## 📖 使用指南

### 1. 配置AI系统

选择并配置要评估的AI系统：

#### Coze Agent
- Agent ID：Agent的唯一标识
- Access Token：API访问令牌
- 平台版本：coze.com（全球版）或 coze.cn（中国版）

#### Coze Bot
- Bot ID：Bot的唯一标识
- Bot版本：latest或特定版本号

#### 自定义API
- API URL：AI服务的接口地址
- HTTP方法：POST/GET/PUT
- 请求头：JSON格式的认证信息

### 2. 选择评估模式

#### 推荐：动态对话模式
1. 上传需求文档或输入需求描述
2. 系统自动提取用户画像
3. 自动生成2个测试场景
4. 开始动态对话评估

#### 智能提取模式
1. 上传详细的需求文档
2. 点击"提取用户画像"
3. 系统基于提取的画像生成测试

#### 手动配置模式
1. 手动填写用户角色信息
2. 添加自定义对话场景
3. 设置对话轮次和内容

### 3. 查看评估结果

- **综合得分**：1-5分制，星级展示
- **维度详情**：4个评估维度的具体分数
- **对话记录**：完整的测试对话历史
- **改进建议**：基于评估结果的优化建议

## 📏 评估维度

### 🔍 模糊理解能力 (Fuzzy Understanding)
**评估AI对用户模糊、不完整描述的理解能力**

- ✅ **优秀 (4-5分)**: 主动澄清模糊信息，引导用户提供关键细节
- ⚠️ **一般 (2-3分)**: 基本理解但澄清不够主动或全面
- ❌ **较差 (1分)**: 无法识别模糊描述，直接给出不准确回答

### ✅ 回答准确性 (Answer Correctness)
**评估AI回答的专业性、准确性和实用性**

- ✅ **优秀 (4-5分)**: 回答专业准确，提供具体操作指导
- ⚠️ **一般 (2-3分)**: 回答基本正确但缺乏细节或部分不准确
- ❌ **较差 (1分)**: 回答错误或与问题不相关

### 👥 用户匹配度 (Persona Alignment)
**评估AI回答是否符合目标用户的特征和需求**

- ✅ **优秀 (4-5分)**: 语言风格、专业程度完全匹配用户画像
- ⚠️ **一般 (2-3分)**: 基本符合用户特征但有改进空间
- ❌ **较差 (1分)**: 回答风格不符合用户群体特征

### 🎯 目标对齐性 (Goal Alignment)
**评估AI是否帮助用户实现业务目标**

- ✅ **优秀 (4-5分)**: 直接解决用户问题，提供可行的解决方案
- ⚠️ **一般 (2-3分)**: 部分解决问题但不够深入或全面
- ❌ **较差 (1分)**: 未能解决用户的实际业务需求

## 🔌 API支持

### 支持的AI平台

#### Coze平台
- **Coze Agent**: 支持工具调用和工作流的智能代理
- **Coze Bot**: 传统聊天机器人，稳定可靠
- **全球/中国版**: 自动适配不同地区的API端点

#### 自定义API
- **OpenAI兼容**: 支持OpenAI API格式
- **通用REST API**: 支持自定义HTTP接口
- **认证方式**: 支持Bearer Token、API Key等多种认证

### API调用特性
- **智能重试**: 自动重试失败的API调用
- **超时控制**: 防止长时间等待
- **错误处理**: 友好的错误提示和fallback机制
- **日志记录**: 详细的API调用日志

## 📁 项目结构

```
ai_test/
├── main.py                 # 主应用文件 (FastAPI后端)
├── templates/              # HTML模板目录
│   └── index.html         # 主界面模板 (响应式设计)
├── requirements.txt        # Python依赖包
├── Dockerfile             # Docker配置文件
├── .gitignore            # Git忽略配置
└── README.md             # 项目文档
```

### 核心文件说明

#### `main.py` (3388行)
- FastAPI应用主体
- API路由定义
- DeepSeek集成逻辑
- 多平台AI接口适配
- 4维度评估算法

#### `templates/index.html` (1598行)
- 现代化响应式界面
- 折叠式卡片系统
- 实时交互逻辑
- 评估结果可视化

#### `requirements.txt`
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
jinja2==3.1.2
python-docx==1.1.0
PyPDF2==3.0.1
aiohttp==3.9.1
aiofiles==23.2.1
```

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 提交Bug报告
1. 使用GitHub Issues
2. 提供详细的复现步骤
3. 包含错误日志和环境信息

### 功能建议
1. 在Issues中描述新功能需求
2. 说明使用场景和价值
3. 参与讨论设计方案

### 代码贡献
1. Fork项目仓库
2. 创建功能分支
3. 提交Pull Request
4. 通过代码审查

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 📞 联系我们

- **项目维护者**: [Your Name]
- **邮箱**: your.email@example.com
- **GitHub**: [项目仓库地址]

---

<div align="center">

**🌟 如果这个项目对您有帮助，请给我们一个Star！**

Made with ❤️ by AI Evaluation Team

</div>