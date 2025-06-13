# AI Evaluation Platform - Detailed Code Structure & Workflow

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Backend Components](#backend-components)
3. [Frontend Components](#frontend-components)
4. [Data Flow](#data-flow)
5. [Key Features & Implementation](#key-features--implementation)
6. [Error Handling & Edge Cases](#error-handling--edge-cases)
7. [Prompts & Templates](#prompts--templates)

## System Architecture

### Overview
The AI Evaluation Platform is built using a FastAPI backend and a modern HTML/JavaScript frontend. The system evaluates AI agents through structured conversations and provides detailed analysis and recommendations.

### Core Components
- **Backend**: FastAPI application (`main.py`)
- **Frontend**: HTML templates with JavaScript (`templates/index.html`)
- **API Integration**: DeepSeek API for AI-powered analysis
- **Database**: SQL database for storing evaluation results

## Backend Components

### 1. API Configuration (`APIConfig` Class)
```python
class APIConfig(BaseModel):
    type: str = Field(default="http")
    url: str = Field(..., description="AI Agent API URL")
    method: str = Field(default="POST")
    headers: Dict[str, str] = Field(default={})
    timeout: int = Field(default=30)
    agentId: Optional[str] = None
    region: Optional[str] = "global"
    botId: Optional[str] = None
    botVersion: Optional[str] = None
```

### 2. Evaluation Request Structure
```python
class EvaluationRequest(BaseModel):
    agent_api: APIConfig
    requirement_doc: Optional[str] = ""
    conversation_scenarios: List[ConversationScenario]
    use_raw_messages: Optional[bool] = False
    coze_bot_id: Optional[str] = None
```

### 3. DeepSeek API Integration
```python
async def call_deepseek_api(prompt: str, max_retries: int = 2) -> str:
    """
    Core function for DeepSeek API interaction
    - Handles authentication
    - Manages retries
    - Processes responses
    """
    headers = {
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
        "temperature": config.DEFAULT_TEMPERATURE
    }
```

### 4. AI Improvement Suggestions Generation
```python
async def generate_ai_improvement_suggestions_for_programmers(
    explanations: Dict, 
    evaluation_summary: Dict
) -> List[str]:
    """
    Generates AI-powered improvement suggestions
    - Analyzes evaluation results
    - Creates structured suggestions
    - Handles formatting and validation
    """
```

## Frontend Components

### 1. Report Generation Structure
```javascript
function generateFinalReport(data) {
    const summary = data.evaluation_summary || {};
    const persona = summary.persona || {};
    const usageContext = summary.usage_context || {};
    const goal = summary.goal || {};
    const recommendations = summary.recommendations || data.recommendations || [];
    
    return `
        <div class="final-report-container">
            ${generateOverallScoreCard(summary)}
            ${generateRecommendationsCard(recommendations)}
            ${generateUserPersonaCard(persona, usageContext, goal)}
            ${generateDimensionsCard(summary.dimension_scores_100)}
            ${generateConversationsCard(data.conversation_records || [])}
            ${generateTechDataCard(data)}
        </div>
    `;
}
```

### 2. Recommendations Display
```javascript
function generateRecommendationsCard(recommendations) {
    // Priority handling for different suggestion types
    const aiSuggestions = currentEvaluationData?.ai_improvement_suggestions || [];
    const displayRecommendations = aiSuggestions.length > 0 ? aiSuggestions : recommendations;
    
    // Formatting logic for each suggestion
    return recommendations.map(rec => {
        const lines = rec.split('\n');
        const formattedLines = lines.map(line => {
            if (line.startsWith('问题：')) {
                return `<h6 class="mb-2 text-primary">${line}</h6>`;
            } else if (line.startsWith('方案：')) {
                return `<p class="mb-2">${line}</p>`;
            } else if (line.startsWith('预期：')) {
                return `<p class="mb-3 text-info"><small>${line}</small></p>`;
            }
        }).join('');
    });
}
```

### 3. Styling and Layout
```css
/* Core styling for recommendations */
.recommendations-container {
    max-height: 500px;
    overflow-y: auto;
}

.recommendation-item {
    margin-bottom: 1rem;
    padding: 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background: white;
    transition: all 0.3s ease;
}

.recommendation-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
```

## Data Flow

### 1. Evaluation Process
1. User submits evaluation request
2. Backend processes request and initiates evaluation
3. DeepSeek API generates analysis
4. Results are structured and stored
5. Frontend receives and displays data

### 2. Suggestion Generation Flow
```
User Request
    ↓
Evaluation Processing
    ↓
DeepSeek API Analysis
    ↓
Suggestion Generation
    ↓
Data Structuring
    ↓
Frontend Display
```

### 3. Data Structure
```json
{
    "conversation_records": [],
    "recommendations": [],
    "ai_improvement_suggestions": [],
    "evaluation_summary": {
        "overall_score_100": 85.5,
        "dimension_scores_100": {},
        "persona": {},
        "usage_context": {},
        "goal": {}
    },
    "user_persona_info": {}
}
```

## Key Features & Implementation

### 1. Multi-source Suggestion Handling
- Priority order for suggestions:
  1. AI-generated suggestions
  2. Regular recommendations
  3. Fallback suggestions

### 2. Structured Suggestion Format
- Problem identification
- Technical solution
- Expected outcome
- Priority indicators

### 3. Visual Hierarchy
- Color coding for different sections
- Clear typography hierarchy
- Interactive elements
- Responsive design

### 4. Performance Optimizations
- Lazy loading of content
- Efficient DOM updates
- Caching of evaluation data
- Optimized API calls

## Error Handling & Edge Cases

### 1. API Error Handling
```python
try:
    response = await client.post(config.DEEPSEEK_API_URL, 
                               headers=headers, 
                               json=payload)
    response.raise_for_status()
except httpx.HTTPError as e:
    print(f"❌ API调用失败: {str(e)}")
    if attempt < max_retries - 1:
        continue
    raise
```

### 2. Frontend Error States
```javascript
function generateRecommendationsCard(recommendations) {
    if (!recommendations || recommendations.length === 0) {
        return `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">优化建议</h5>
                    <p class="text-muted">暂无具体改进建议，当前表现良好。</p>
                </div>
            </div>`;
    }
    // ... rest of the function
}
```

### 3. Data Validation
- Input sanitization
- Type checking
- Null value handling
- Default value provision

### 4. Edge Cases
- Empty evaluation results
- API timeout handling
- Network error recovery
- Data format inconsistencies

## Best Practices & Guidelines

### 1. Code Organization
- Clear separation of concerns
- Modular component design
- Consistent naming conventions
- Comprehensive documentation

### 2. Performance Considerations
- Efficient data structures
- Optimized API calls
- Minimal DOM updates
- Resource caching

### 3. Security Measures
- Input validation
- API key protection
- XSS prevention
- CSRF protection

### 4. Maintenance Guidelines
- Regular code reviews
- Performance monitoring
- Error logging
- Documentation updates

## Prompts & Templates

### 1. Evaluation Prompts

#### 1.1 General Dimension Evaluation Prompt
```python
eval_prompt = f"""
你是对话质量评估专家。请根据下方对话内容，从"{dimension_name}"这个维度对AI的表现进行评分，满分100分。

📘【场景信息】:
- 场景标题: {scenario.get('title', 'N/A')}
- 背景描述: {scenario.get('context', 'N/A')}
- 用户角色: {persona.get('role', 'N/A')}

🧾【对话内容】:
{conversation_text}

📏【评分标准】:
- 90–100分: 表现优秀，完全满足该维度要求
- 80–89分: 良好表现，略有提升空间
- 60–79分: 基本达标，但存在明显不足
- 40–59分: 有较大问题，影响用户体验
- 0–39分: 表现失败，严重偏离该维度要求

🧪【评分示例】:

示例1（评分: 95）：
- 维度: 回答准确性
- 对话：
  用户：施工时混凝土振捣的时间怎么控制？
  AI：根据《GB50204-2015》第6.3.2条，普通混凝土振捣时间应控制在10-30秒之间。
- 评价：引用规范准确，内容完整、专业。

示例2（评分: 72）：
- 维度: 回答准确性
- 对话：
  用户：钢筋搭接长度？
  AI：钢筋搭接30公分就够了。
- 评价：回答模糊，未引用具体标准，误导用户。

📝【请填写】:
评分：[0-100]
理由：[基于维度和对话，说明你的判断依据]
"""
```
**Usage**: Used to evaluate AI performance in specific dimensions with enhanced few-shot examples for better objectivity

#### 1.2 Answer Correctness Evaluation
```python
evaluation_prompts["answer_correctness"] = f"""
你是建筑类对话专家，任务是评估AI回答的准确性与专业性，评分范围为0–100分。

{base_context}

📚【评分标准】:
- 90–100分: 回答完整，内容专业，引用规范清晰
- 80–89分: 回答准确但略缺细节或未引用规范
- 60–79分: 回答基本正确但存在模糊或误导性表达
- 40–59分: 核心内容错误或结构混乱
- 0–39分: 严重错误，可能产生误导或危险

📘【示例参考】:

示例1（评分: 95）：
用户：水泥砂浆的厚度标准是多少？
AI：根据《GB50209-2010》第5.2.1条，普通水泥砂浆厚度一般控制在15mm左右。
评价：回答准确、引用规范清晰。

示例2（评分: 68）：
用户：混凝土振捣多久？
AI：一分钟左右。
评价：方向对但不专业，缺乏标准支持。

📝【请完成】:
评分：[0-100]
理由：[基于准确性进行解释]
"""
```
**Usage**: Evaluates the accuracy and professionalism of AI responses with domain-specific examples

#### 1.3 Persona Alignment Evaluation
```python
evaluation_prompts["persona_alignment"] = f"""
你是用户画像匹配度评估专家，任务是判断AI是否采用了符合该用户角色的沟通风格与表达方式。

{base_context}

📐【评分标准】:
- 90–100分: 完全贴合用户角色，语气自然专业
- 80–89分: 基本匹配，偶有不自然表达
- 60–79分: 有术语、语调等不适配问题
- 40–59分: 明显风格不符
- 0–39分: 完全脱离角色

📘【示例参考】:

示例1（评分: 92）：
用户（施工员）：水泥怎么养护？
AI：初凝后洒水保持湿润7天。
评价：语气贴近现场，表达简洁。

示例2（评分: 84）：
用户（甲方）：需要闭水试验吗？
AI：请根据GB规范进行闭水。
评价：表达专业但偏生硬。

📝【请填写】:
评分：[0-100]
理由：[结合语调、用词是否贴合用户画像]
"""
```
**Usage**: Evaluates how well the AI's communication style matches the user's persona with concrete examples

### 2. Conversation Generation Prompts

#### 2.1 Initial Message Generation
```python
initial_message_prompt = f"""你现在要扮演{role}，在以下场景中开始一段对话：

场景背景: {scenario_context}
场景标题: {scenario_title}

你的角色特征:
- 职业: {role}
- 经验水平: {experience_level}  
- 沟通风格: {communication_style}
- 工作领域: {business_domain}

请生成一句自然的开场白，作为{role}向AI助手提出的第一个问题或请求。
要求：
1. 语言自然，符合{communication_style}的风格
2. 体现{role}的专业关注点
3. 与{scenario_title}场景相关
4. 长度控制在50字以内

直接输出对话内容，不要其他解释："""
```
**Usage**: Generates the first user message in a conversation based on the user's persona and scenario

#### 2.2 Follow-up Message Generation
```python
followup_prompt = f"""你是{role}，正在与AI助手进行专业咨询对话。以下是对话历史：

{conversation_context}

AI刚才的回应：{ai_response}

根据AI的回应和你的专业背景，生成下一句自然的跟进问题。

要求:
1. 基于AI的具体回应内容进行有针对性的跟进
2. 体现{role}的专业关注点和思维方式
3. 语言自然，符合{communication_style}的风格
直接输出对话内容，不要其他解释："""
```
**Usage**: Generates follow-up messages based on the conversation history and AI's previous response

### 3. Improvement Suggestion Prompts

#### 3.1 AI Improvement Suggestions
```python
improvement_prompt = f"""评估概况:
- 综合得分: {evaluation_summary.get('overall_score_100', 75)}/100分
- 评估维度得分: {'; '.join(dimension_scores)}
- 评估框架: {evaluation_summary.get('framework', '规范查询评估')}

主要问题分析:
{chr(10).join(dimension_issues) if dimension_issues else '总体表现良好'}

请提供3-5条具体的技术改进建议，每条建议必须包含以下三个部分：
1. 问题描述：明确指出需要改进的具体问题，特别是与提示词相关的问题
2. 解决方案：提供具体可行的技术方案，包括具体的提示词优化建议
3. 预期效果：说明改进后的预期效果

重点关注以下方面：
- 提示词结构和格式优化
- 上下文管理和历史对话处理
- 角色定义和任务指令的清晰度
- 专业领域知识的引导方式
- 多轮对话的连贯性维护
- 错误处理和边界情况的提示词设计

格式要求：
每条建议必须按照以下格式输出：
问题：xxx
方案：xxx
预期：xxx

改进建议："""
```
**Usage**: Generates AI-powered improvement suggestions based on evaluation results with structured format

### 4. Fallback Prompts

#### 4.1 Fallback Response Generation
```python
fallback_prompt = f"""作为一个专业的{user_persona_info.get('user_persona', {}).get('role', '助手')}，请对以下问题给出简短但有用的回复：

用户问题：{current_user_message}
回复要求：
1. 直接回答问题，不要说"我不知道"
2. 保持专业但友好的语调
3. 如果需要更多信息，可以简单询问
4. 回复控制在50字以内

请直接给出回复："""
```
**Usage**: Generates a fallback response when the primary AI response is empty or invalid

### 5. Scenario Generation Prompts

#### 5.1 Dynamic Scenario Generation
```python
scenario_prompt = f"""基于以下用户画像，生成1个真实、具体的对话场景：

用户角色：{role}
业务领域：{business_domain}
主要使用场景：{', '.join(primary_scenarios)}
沟通风格：{persona.get('communication_style', '专业直接')}
工作环境：{persona.get('work_environment', '专业环境')}

请生成JSON格式的场景：
{{
  "title": "具体场景名称",
  "context": "详细的业务背景和情境描述，反映{role}在{business_domain}中的典型工作情况",
  "user_profile": "用户在此场景下的具体身份和需求"
}}

要求：
1. 场景要真实反映{role}在{business_domain}中的典型工作情况
2. 场景要有明确的业务背景和具体情境
3. 避免过于复杂的技术细节，但要足够具体

直接输出JSON对象，不要其他文字："""
```
**Usage**: Generates dynamic conversation scenarios based on user persona and business context

### 6. 🎯 Tricky Test Mode Prompts (NEW Feature)

#### 6.1 Tricky Initial Message Generation
```python
async def generate_quick_initial_message(scenario: Dict, user_persona_info: Dict, is_tricky_test: bool = False) -> str:
    """
    Generates initial messages with optional tricky test mode for edge-case scenarios
    """
    
    if is_tricky_test:
        tricky_prompt = f"""你现在要扮演{role}，但现在需要提出一些刁钻但合理的问题。

场景背景: {scenario_context}
你的角色: {role}
业务领域: {business_domain}

请生成一个关于极端或非常规建筑场景的问题，例如：
- 极端气候条件下的建筑问题（南极、沙漠、高海拔）
- 历史建筑改造的特殊要求
- 特殊材料或工艺的应用
- 非标准规范的边界情况

要求：
1. 问题要刁钻但现实合理，不是天马行空
2. 应该是标准规范数据库中不太容易找到答案的问题
3. 符合{role}的专业背景和关注点
4. 长度控制在30-50字

直接输出问题，不要其他解释："""

        # Fallback tricky questions for different domains
        tricky_fallbacks = {
            "建筑工程": [
                "南极科考站建设中，混凝土在-40°C环境下的浇筑工艺有什么特殊要求？",
                "海拔4500米高原地区的钢筋混凝土结构，需要考虑哪些大气压力影响？",
                "历史保护建筑中，如何在不破坏原有结构的前提下增加抗震措施？"
            ],
            "金融银行": [
                "数字货币跨境交易在制裁国家的合规风险如何评估？",
                "AI量化交易在极端市场波动期间的风控策略应该如何调整？",
                "小国央行数字货币政策对跨国银行业务的影响如何？"
            ],
            "医疗健康": [
                "在太空环境下，药物的代谢机制会发生什么改变？",
                "基因编辑技术在治疗罕见遗传病时的伦理边界在哪里？",
                "极地探险队员的心理健康评估标准有何特殊性？"
            ],
            "教育培训": [
                "AI导师在情感支持方面能否完全替代人类教师？",
                "元宇宙教学环境对学习者认知发展的长期影响如何？",
                "多语言环境下的认知负荷理论应用有什么局限性？"
            ]
        }
```
**Usage**: Generates edge-case questions targeting scenarios not covered by standard databases

#### 6.2 Tricky Follow-up Message Generation
```python
async def generate_next_message_based_on_response(
    scenario_info: Dict, 
    user_persona_info: Dict, 
    conversation_history: List[Dict], 
    ai_response: str,
    is_tricky_test: bool = False
) -> str:
    """
    Generates follow-up messages with continuation of tricky scenarios
    """
    
    if is_tricky_test:
        tricky_followup_prompt = f"""你是{role}，刚才提出了一个关于极端场景的问题。

对话历史：
{conversation_context}

AI的回应：{ai_response}

现在请基于AI的回应，继续提出一个更深入的刁钻问题，要求：
1. 延续之前的极端场景设定
2. 基于AI的具体回应内容进行针对性追问
3. 涉及更加边缘的技术细节或特殊情况
4. 例如：如果之前问的是极寒建筑，现在可以问相关的材料特性、施工周期等

直接输出问题，不要解释："""

        # Enhanced tricky scenarios focusing on extreme conditions
        tricky_scenarios = [
            "极端天气条件建筑",
            "历史建筑保护改造", 
            "特殊材料应用",
            "非标准环境施工",
            "跨文化建筑标准",
            "可持续建筑创新"
        ]
```
**Usage**: Continues extreme scenario questioning based on AI's previous responses

#### 6.3 Tricky Test Domain-Specific Examples

**Construction/Engineering Domain:**
- Antarctic research station construction requirements
- High-altitude concrete pouring considerations  
- Historical building seismic retrofitting
- Desert climate construction challenges
- Underwater structure maintenance
- Space habitat construction principles

**Banking/Finance Domain:**
- Cryptocurrency regulation in sanctions
- AI trading extreme market conditions
- Central bank digital currency impacts
- Cross-border payment compliance
- Quantum computing encryption threats
- Decentralized finance risk assessment

**Healthcare Domain:**
- Space medicine drug metabolism
- Gene editing ethical boundaries
- Arctic expedition health protocols
- Rare disease treatment protocols
- AI diagnosis accuracy limitations
- Pandemic response optimization

**Education Domain:**
- AI tutor emotional intelligence
- Metaverse learning cognitive effects
- Multilingual cognitive load theory
- Remote learning effectiveness
- Personalized AI curriculum design
- Virtual reality training safety

### 7. Frontend Integration with Prompt System

#### 7.1 Tricky Test Toggle UI Implementation
```javascript
// Visual feedback when toggling tricky test mode
function handleTrickyTestToggle(checkboxId) {
    const checkbox = document.getElementById(checkboxId);
    const configSection = checkbox.closest('.config-section');
    
    if (checkbox.checked) {
        configSection.classList.add('tricky-test-active');
        // Add visual indicator
        const indicator = document.createElement('div');
        indicator.className = 'tricky-test-indicator';
        indicator.innerHTML = '⚡';
        indicator.title = '刁钻测试模式激活';
        configSection.appendChild(indicator);
        showTrickyTestWarning();
    } else {
        configSection.classList.remove('tricky-test-active');
        // Remove indicator
    }
}
```
**Purpose**: Provides immediate visual feedback when tricky test mode is enabled

#### 7.2 Form Data Integration
```javascript
// Form submission with tricky test parameter
if (selectedProjectScenario === 'specification-query') {
    formData.append('enable_turn_control', document.getElementById('enableTurnControl').checked);
    formData.append('is_tricky_test', document.getElementById('enableTrickyTest').checked);
    endpoint = '/api/evaluate-agent-specification-query';
} else {
    // Dynamic evaluation path
    formData.append('is_tricky_test', document.getElementById('enableTrickyTestDynamic').checked);
    endpoint = '/api/evaluate-agent-dynamic';
}
```
**Purpose**: Passes tricky test mode selection to backend API endpoints

#### 7.3 Results Display Enhancement
```javascript
function generateOverallScoreCard(summary) {
    const isTrickyMode = summary.is_tricky_test || false;
    const trickyBadge = isTrickyMode ? 
        `<span class="badge bg-warning ms-2" title="使用了刁钻测试模式">
            <i class="fas fa-bolt"></i> 刁钻模式
        </span>` : '';
    
    // Display tricky mode indicator in results
    return `<div class="card">
        <h3>综合得分报告${trickyBadge}</h3>
        <p>最终得分（100分制）${isTrickyMode ? ' - 极端场景测试' : ''}</p>
        // ... rest of the report
    </div>`;
}
```
**Purpose**: Clearly indicates when tricky test mode was used in evaluation results

## Key Improvements in Enhanced Prompts

### 1. **Few-Shot Examples**
- Added concrete examples with scores and explanations
- Improved evaluation consistency and objectivity
- Reduced ambiguity in scoring criteria

### 2. **Visual Structure**
- Used emojis and formatting for better readability
- Clear section headers with visual indicators
- Structured layout for easier comprehension

### 3. **Unified 0-100 Scoring**
- Consistent scoring scale across all evaluation dimensions
- More granular scoring for better differentiation
- Aligned with system's 100-point evaluation framework

### 4. **Domain-Specific Context**
- Construction/engineering examples for better relevance
- Role-specific language and terminology
- Industry-appropriate scenarios and standards

### 5. **Enhanced Clarity**
- Clearer instructions and requirements
- Specific formatting guidelines
- Reduced ambiguity in prompt interpretation

### 6. **🎯 Tricky Test Mode Innovation**
- Edge-case scenario generation for boundary testing
- Domain-specific extreme situation prompts
- Intelligent follow-up question continuity
- Visual UI feedback and clear result indication
- Comprehensive fallback mechanisms for different industries

## Prompt System Architecture

### 1. **Hierarchical Prompt Structure**
```
Evaluation Framework
├── Dimension-Specific Prompts
│   ├── Answer Correctness
│   ├── Persona Alignment
│   ├── Goal Alignment
│   └── Specification Citation
├── Conversation Generation
│   ├── Initial Message Generation
│   ├── Follow-up Generation
│   └── 🎯 Tricky Test Generation
├── Improvement Suggestions
│   ├── Technical Recommendations
│   └── Prompt Optimization
└── Fallback & Error Handling
    ├── Response Validation
    └── Alternative Generation
```

### 2. **Parameter Flow Architecture**
```
Frontend UI Toggle → Form Submission → Backend API → 
Prompt Selection → DeepSeek API → Response Processing → 
Result Display with Mode Indication
```

### 3. **Quality Assurance Mechanisms**
- **Prompt Validation**: All prompts include explicit output format requirements
- **Fallback Systems**: Multiple backup prompts for each scenario type
- **Context Preservation**: Conversation history maintained across all prompt types
- **Domain Adaptation**: Prompts automatically adjust based on user persona and business domain
- **Error Recovery**: Graceful degradation when AI generation fails

### 4. **Performance Optimization**
- **Prompt Caching**: Reusable prompt templates with dynamic variable injection
- **Batch Processing**: Multiple evaluations can share prompt infrastructure
- **Async Processing**: Non-blocking prompt generation and evaluation
- **Resource Management**: Prompt complexity balanced with response time requirements 