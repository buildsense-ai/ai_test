# AI Agent Evaluation Platform v4.2

🚀 **DEPLOYMENT READY** - All configuration is hardcoded for easy deployment!

A comprehensive platform for evaluating AI agents through dynamic multi-turn conversations with intelligent user persona extraction and 3-dimensional evaluation framework.

## ✨ Key Features

- **🎭 Intelligent User Persona Extraction**: Automatically extracts user personas from requirement documents using DeepSeek AI
- **💬 Dynamic Conversation Generation**: Creates realistic, multi-turn conversations based on extracted personas
- **📊 3-Dimensional Evaluation Framework**: 
  - Fuzzy Understanding & Follow-up Capability
  - Answer Accuracy & Professionalism  
  - User Persona Alignment
- **📄 Document Processing**: Supports Word (.docx), PDF (.pdf), and Text (.txt) files
- **🔧 Multiple API Support**: Coze Bot, Coze Agent, and custom API configurations
- **📈 Comprehensive Reporting**: Detailed analysis with improvement recommendations

## 🚀 Quick Start (Deployment Ready)

### Prerequisites
- Python 3.8+
- Internet connection for API calls

### 1. Clone and Setup
```bash
git clone <your-repository-url>
cd ai_test
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python main.py
```

The server will automatically:
- Load all configuration from `config.py` (no environment variables needed!)
- Find an available port (8000, 8001, etc.)
- Display startup message with the port number

### 3. Access the Platform
Open your browser and go to: `http://localhost:8000` (or the port shown in startup message)

## 🔧 Configuration

All configuration is **hardcoded** in `config.py` for easy deployment:

```python
# DeepSeek API Configuration (Already configured)
DEEPSEEK_API_KEY = "sk-d2513b4c4626409599a73ba64b2e9033"
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1/chat/completions"

# Coze API Configuration (Already configured)  
COZE_API_BASE = "https://api.coze.com/v3/chat"
COZE_API_TOKEN = "pat_uNT5YdZdvv3AjgVyN9LzAZ7E9dUeGaHGAJ5HQp1PWy7PFKdIbJvGFxTGUq8vvCBB"
DEFAULT_COZE_BOT_ID = "7511993619423985674"

# Timeout Settings (Optimized to prevent network errors)
DEEPSEEK_TIMEOUT = 60  # Increased for stability
COZE_TIMEOUT = 60
```

**No additional configuration needed!** Just run and deploy.

## 📋 Usage

### Dynamic Evaluation (Recommended)

1. **Upload Document**: Upload your requirement document (Word, PDF, or Text)
2. **Configure AI Agent**: Set up your AI agent API configuration
3. **Start Evaluation**: The platform will:
   - Extract user persona from your document
   - Generate 2 dynamic conversation scenarios
   - Conduct 2-3 turn conversations per scenario
   - Provide comprehensive evaluation and recommendations

### API Configuration Examples

#### Coze Bot Configuration
```json
{
  "type": "coze-bot",
  "url": "https://api.coze.com/v3/chat",
  "botId": "your-bot-id",
  "headers": {
    "Authorization": "Bearer your-access-token"
  }
}
```

#### Coze Agent Configuration  
```json
{
  "type": "coze-agent",
  "url": "https://api.coze.com/v3/chat",
  "agentId": "your-agent-id",
  "region": "global",
  "headers": {
    "Authorization": "Bearer your-access-token"
  }
}
```

## 🛠️ Technical Architecture

### Core Components
- **FastAPI Backend**: High-performance async web framework
- **DeepSeek Integration**: AI-powered persona extraction and evaluation
- **Document Processing**: Multi-format document parsing
- **Dynamic Conversation Engine**: Real-time conversation generation
- **Evaluation Framework**: Multi-dimensional scoring system

### API Endpoints
- `GET /`: Main evaluation interface
- `POST /api/evaluate-agent-dynamic`: Dynamic evaluation with persona extraction
- `POST /api/evaluate-agent-with-file`: Manual evaluation with custom scenarios
- `POST /api/validate-config`: API configuration validation

## 🔍 Evaluation Dimensions

### 1. Fuzzy Understanding & Follow-up Capability (模糊理解与追问能力)
- Ability to understand ambiguous user expressions
- Proactive clarification and follow-up questions
- Guidance towards clear requirements

### 2. Answer Accuracy & Professionalism (回答准确性与专业性)
- Factual correctness of responses
- Professional terminology usage
- Reference to standards and regulations

### 3. User Persona Alignment (用户适配度)
- Communication style matching user background
- Appropriate technical level for user experience
- Cultural and contextual sensitivity

## 📊 Sample Output

```json
{
  "evaluation_summary": {
    "overall_score": 4.2,
    "total_scenarios": 2,
    "total_conversations": 6,
    "framework": "动态多轮对话评估"
  },
  "extracted_persona_display": {
    "user_role": "现场监理工程师",
    "business_domain": "建筑工程",
    "experience_level": "5年现场经验",
    "communication_style": "简洁专业，偶有模糊表达"
  },
  "recommendations": [
    "🟢 针对现场监理工程师的整体表现优秀！",
    "💡 建议加强对模糊问题的追问引导机制",
    "📚 提升建筑规范相关知识的准确性"
  ]
}
```

## 🚀 Deployment Options

### Local Development
```bash
python main.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### Docker Deployment
```bash
docker build -t ai-evaluation-platform .
docker run -p 8000:8000 ai-evaluation-platform
```

## 🔧 Troubleshooting

### Common Issues

1. **Network Timeout Errors**: 
   - Already fixed with increased timeout settings in config.py
   - DEEPSEEK_TIMEOUT and COZE_TIMEOUT set to 60 seconds

2. **API Authentication Errors**:
   - Check your API tokens in the configuration
   - Ensure tokens have proper permissions

3. **Document Processing Errors**:
   - Ensure document is not corrupted
   - Check file size (max 10MB)
   - Supported formats: .docx, .pdf, .txt

### Error Handling
The platform includes comprehensive error handling:
- Automatic fallback for persona extraction failures
- Graceful degradation for API timeouts
- **Fixed Coze API Integration**: Resolved "no valid response content" errors with proper SSE streaming support

## 🔧 Recent Updates

### v4.2 - Enhanced Evaluation Display & Raw Message Processing

- **📊 Fixed Scoring System**: Standardized all scores to 0-100 scale across all evaluation components
- **🎯 Enhanced Evaluation Display**: Improved visibility of detailed analysis sections and comprehensive scoring
- **💬 Raw Message Processing**: Added support for raw user message processing without persona enhancement
- **🔍 Modular Debug Logging**: Implemented comprehensive debug logs with message traceability
- **⚡ Technical Improvements**: 
  - Standardized score normalization across evaluation dimensions
  - Enhanced persona extraction and user role identification
  - Improved report generation with detailed analysis display
  - Better error handling and fallback mechanisms
- **🎨 UI/UX Enhancements**:
  - Better visibility of detailed analysis sections
  - Improved score display consistency
  - Enhanced recommendation generation
  - Clearer evaluation summary presentation
- **🛠️ Bug Fixes**:
  - Resolved persona alignment scoring inconsistencies
  - Enhanced document processing reliability
  - Improved error message clarity

### v4.1 - Coze API Integration Fix
- **✅ Fixed Coze API Response Parsing**: Resolved critical issue where Coze API returned "no valid response content in coze api result"
- **🔄 Enhanced Streaming Support**: Added proper Server-Sent Events (SSE) parsing for Coze API streaming responses
- **📡 Improved API Compatibility**: Updated payload format to match Coze API v3 requirements:
  - Added missing `"type": "question"` field in message objects
  - Implemented proper `"parameters": {}` field structure
  - Enhanced content-type detection for streaming vs JSON responses
- **🚀 Better Error Handling**: Improved error messages and fallback mechanisms for API failures
- **⚡ Performance Optimization**: Optimized response parsing for both streaming and non-streaming API responses

### Technical Details of Coze API Fix
The fix addresses several critical issues:
1. **Missing Required Fields**: Added `"type": "question"` field which was causing API rejections
2. **Streaming Response Parsing**: Implemented proper SSE (Server-Sent Events) parsing for `text/event-stream` responses
3. **Content Extraction Logic**: Enhanced logic to extract content from both `conversation.message.delta` and `conversation.message.completed` events
4. **Fallback Mechanisms**: Added multiple fallback strategies for different response formats
- Detailed error messages for debugging

## 📝 Development Notes

### Recent Fixes (v4.0)
- ✅ All configuration moved to `config.py` (no environment variables)
- ✅ Increased API timeouts to prevent network errors
- ✅ Enhanced error handling with fallback mechanisms
- ✅ Improved DeepSeek API integration
- ✅ Optimized Coze API calls
- ✅ Better document processing reliability

### Code Quality
- Type hints throughout codebase
- Comprehensive error handling
- Async/await for optimal performance
- Modular architecture for easy maintenance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**Ready for immediate deployment!** 🚀 Just clone, install dependencies, and run!