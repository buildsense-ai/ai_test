import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import httpx
import json
from datetime import datetime
import socket
from enum import Enum
import io
import os
import re
import tempfile
import logging

# Document processing imports
try:
    import docx
    from PyPDF2 import PdfReader
    DOCUMENT_PROCESSING_AVAILABLE = True
except ImportError:
    DOCUMENT_PROCESSING_AVAILABLE = False

app = FastAPI(title="AI Agent Evaluation Platform", version="3.0.0")
templates = Jinja2Templates(directory="templates")

# Improved document processing functions based on user's approach
def read_docx_file(filepath: str) -> str:
    """Read Word document using direct file path approach"""
    try:
        if not DOCUMENT_PROCESSING_AVAILABLE:
            return "文档处理库未安装，请安装 python-docx：pip install python-docx"
        
        doc = docx.Document(filepath)
        # Extract text from paragraphs
        text_parts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_parts.append(cell.text.strip())
        
        # Join and clean the text
        full_text = "\n".join(text_parts)
        cleaned_text = full_text.replace("\r", "").replace("　", "").strip()
        
        print(f"📄 Word文档提取成功，内容长度: {len(cleaned_text)} 字符")
        return cleaned_text
        
    except Exception as e:
        error_msg = f"Word文档解析失败: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

def read_pdf_file(filepath: str) -> str:
    """Read PDF document using direct file path approach"""
    try:
        if not DOCUMENT_PROCESSING_AVAILABLE:
            return "文档处理库未安装，请安装 PyPDF2：pip install PyPDF2"
        
        with open(filepath, 'rb') as file:
            pdf_reader = PdfReader(file)
            text_parts = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    text_parts.append(text.strip())
        
        # Join and clean the text
        full_text = "\n".join(text_parts)
        cleaned_text = full_text.replace("\r", "").replace("　", "").strip()
        
        print(f"📄 PDF文档提取成功，内容长度: {len(cleaned_text)} 字符")
        return cleaned_text
        
    except Exception as e:
        error_msg = f"PDF文档解析失败: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

def read_txt_file(filepath: str) -> str:
    """Read text file with proper encoding"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        
        # Clean the text
        cleaned_text = text.replace("\r", "").replace("　", "").strip()
        
        print(f"📄 文本文件提取成功，内容长度: {len(cleaned_text)} 字符")
        return cleaned_text
        
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        try:
            with open(filepath, "r", encoding="gbk") as f:
                text = f.read()
            cleaned_text = text.replace("\r", "").replace("　", "").strip()
            print(f"📄 文本文件提取成功(GBK编码)，内容长度: {len(cleaned_text)} 字符")
            return cleaned_text
        except Exception as e:
            error_msg = f"文本文件解析失败: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    except Exception as e:
        error_msg = f"文本文件解析失败: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

async def process_uploaded_document_improved(file: UploadFile) -> str:
    """Process uploaded document using improved approach with temporary files"""
    if not file or not file.filename:
        return ""
    
    # Create temporary file
    suffix = os.path.splitext(file.filename)[1].lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        try:
            # Write uploaded content to temporary file
            content = await file.read()
            tmp_file.write(content)
            tmp_file.flush()
            
            # Process based on file extension
            if suffix in ['.doc', '.docx']:
                result = read_docx_file(tmp_file.name)
            elif suffix == '.pdf':
                result = read_pdf_file(tmp_file.name)
            elif suffix == '.txt':
                result = read_txt_file(tmp_file.name)
            else:
                result = f"不支持的文件格式: {suffix}。支持格式: Word (.docx), PDF (.pdf), 文本 (.txt)"
            
            return result
            
        except Exception as e:
            return f"文档处理失败: {str(e)}"
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_file.name)
            except:
                pass

# Legacy functions for backward compatibility (but using improved approach)
async def extract_text_from_docx(file_content: bytes) -> str:
    """Legacy function - now uses improved approach with temporary file"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
        try:
            tmp_file.write(file_content)
            tmp_file.flush()
            return read_docx_file(tmp_file.name)
        finally:
            try:
                os.unlink(tmp_file.name)
            except:
                pass

async def extract_text_from_pdf(file_content: bytes) -> str:
    """Legacy function - now uses improved approach with temporary file"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        try:
            tmp_file.write(file_content)
            tmp_file.flush()
            return read_pdf_file(tmp_file.name)
        finally:
            try:
                os.unlink(tmp_file.name)
            except:
                pass

async def process_uploaded_document(file: UploadFile) -> str:
    """Legacy function - now uses improved approach"""
    return await process_uploaded_document_improved(file)

# Core Models according to README specifications
class APIConfig(BaseModel):
    """API Configuration for AI Agent"""
    type: str = Field(default="http", description="API Type")
    url: str = Field(..., description="AI Agent API URL")
    method: str = Field(default="POST", description="HTTP Method")
    headers: Dict[str, str] = Field(default={}, description="Request Headers")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    
    # Coze Agent specific fields
    agentId: Optional[str] = Field(default=None, description="Coze Agent ID")
    region: Optional[str] = Field(default="global", description="Coze region")
    
    # Coze Bot specific fields  
    botId: Optional[str] = Field(default=None, description="Coze Bot ID")
    botVersion: Optional[str] = Field(default=None, description="Coze Bot Version")

class ConversationScenario(BaseModel):
    """Test scenario for multi-turn conversation"""
    title: str = Field(..., description="Scenario title")
    turns: List[str] = Field(..., description="User conversation turns")
    context: Optional[str] = Field(default="", description="Business context")
    user_profile: Optional[str] = Field(default="", description="User persona")

class EvaluationRequest(BaseModel):
    """Main evaluation request following README structure"""
    agent_api: APIConfig = Field(..., description="AI Agent API Configuration")
    requirement_doc: Optional[str] = Field(default="", description="Requirement document for context")
    conversation_scenarios: List[ConversationScenario] = Field(..., description="Test scenarios")
    
    # Coze compatibility (temporary until full API support)
    coze_bot_id: Optional[str] = Field(default="7511993619423985674", description="Coze Bot ID for current implementation")

class EvaluationDimensions(BaseModel):
    """3-dimension evaluation framework from README"""
    fuzzy_understanding: float = Field(..., description="模糊理解与追问能力")
    answer_correctness: float = Field(..., description="回答准确性与专业性") 
    persona_alignment: float = Field(..., description="用户适配度")
    goal_alignment: Optional[float] = Field(default=None, description="目标对齐度")

class EvaluationResponse(BaseModel):
    """Response structure matching README output format"""
    evaluation_summary: Dict[str, Any] = Field(..., description="Evaluation summary")
    conversation_records: List[Dict[str, Any]] = Field(..., description="Detailed conversation records")
    recommendations: List[str] = Field(..., description="Improvement suggestions")
    timestamp: str = Field(..., description="Evaluation timestamp")

# DeepSeek Configuration
DEEPSEEK_API_KEY = "sk-d2513b4c4626409599a73ba64b2e9033"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

async def call_deepseek_api(prompt: str, max_retries: int = 2) -> str:
    """Enhanced DeepSeek API call for evaluation with suppressed exceptions"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 500
    }
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
                response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        content = result["choices"][0].get("message", {}).get("content", "").strip()
                        if content and len(content) > 10:
                            return content
                
                # Suppress warning message for non-critical errors
                if attempt < max_retries - 1:
                    continue
                else:
                    return "API评估暂时不可用，使用备用评分机制"
                    
        except Exception as e:
            # Suppress exception printing to avoid jarring terminal output
            if attempt < max_retries - 1:
                continue
            else:
                return "API评估暂时不可用，使用备用评分机制"

async def call_ai_agent_api(api_config: APIConfig, message: str) -> str:
    """Call AI Agent API - currently supports Coze, will expand for custom APIs"""
    try:
        # Check if we should use Coze API (either explicit coze URL or fallback URL)
        if "coze" in api_config.url.lower() or "fallback" in api_config.url.lower():
            return await call_coze_api_fallback(message)
        else:
            # Generic API support (to be implemented)
            headers = api_config.headers.copy()
            headers.setdefault("Content-Type", "application/json")
            
            payload = {"message": message, "query": message}  # Generic payload format
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(api_config.timeout)) as client:
                response = await client.request(
                    method=api_config.method,
                    url=api_config.url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Try common response paths
                    if "response" in result:
                        return result["response"]
                    elif "answer" in result:
                        return result["answer"]
                    elif "message" in result:
                        return result["message"]
                    else:
                        return str(result)
                else:
                    return f"API调用失败: {response.status_code}"
                    
    except Exception as e:
        print(f"❌ AI Agent API调用异常: {str(e)}")
        return "AI Agent API调用失败，请检查配置"

async def call_coze_api_fallback(message: str, bot_id: str = "7511993619423985674") -> str:
    """Fallback to Coze API for current implementation"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            url = "https://api.coze.cn/open_api/v2/chat"
            headers = {
                "Authorization": "Bearer pat_aWWxLQe20D8km5FsKt5W99pWL72L5LNxjkontH91q3lqqTU0ExBKUBl1cUy4tm8c",
                "Content-Type": "application/json"
            }
            
            payload = {
                "conversation_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{attempt}",
                "bot_id": bot_id,
                "user": "test_user",
                "query": message,
                "stream": False
            }
            
            print(f"🔄 Coze API 调用尝试 {attempt + 1}/{max_retries}")
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    messages = result.get("messages", [])
                    for msg in messages:
                        if msg.get("type") == "answer":
                            content = msg.get("content", "")
                            if content and len(content.strip()) > 0:
                                print(f"✅ Coze API 成功响应")
                                return content
                    
                    # If no answer found, try other message types
                    for msg in messages:
                        if msg.get("content"):
                            content = msg.get("content", "")
                            if content and len(content.strip()) > 0:
                                print(f"✅ Coze API 返回备用内容")
                                return content
                    
                    print(f"⚠️ Coze API 返回空内容，尝试重试...")
                else:
                    print(f"⚠️ Coze API HTTP错误: {response.status_code}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                        
        except Exception as e:
            print(f"❌ Coze API调用异常 (尝试 {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
    
    return "Coze API调用失败，请检查网络连接和API配置"

def extract_score_from_response(response: str) -> float:
    """Extract numerical score from DeepSeek response"""
    try:
        # Look for patterns like "评分：4分", "得分：4.5", "4/5", etc.
        patterns = [
            r'评分[：:]\s*(\d+(?:\.\d+)?)',
            r'得分[：:]\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*分',
            r'(\d+(?:\.\d+)?)\s*/\s*5',
            r'(\d+(?:\.\d+)?)\s*星'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                score = float(match.group(1))
                return min(max(score, 1.0), 5.0)  # Clamp between 1-5
        
        # If no pattern found, try to find any number
        numbers = re.findall(r'\d+(?:\.\d+)?', response)
        if numbers:
            for num in numbers:
                score = float(num)
                if 1 <= score <= 5:
                    return score
        
        # Default fallback
        return 3.0
        
    except Exception:
        return 3.0

async def call_coze_api(bot_id: str, message: str) -> str:
    """Legacy Coze Bot API call (fallback)"""
    return await call_coze_api_fallback(message, bot_id)

async def call_api(api_config: APIConfig, message: str) -> str:
    """Generic API call function"""
    return await call_ai_agent_api(api_config, message)

async def conduct_conversation(api_config: APIConfig, scenario: ConversationScenario) -> List[Dict]:
    """Conduct a conversation based on the scenario"""
    conversation_history = []
    
    print(f"🔧 API 配置类型: {api_config.type}")
    print(f"🔧 API 配置详情: {api_config}")
    
    for turn_num, user_message in enumerate(scenario.turns, 1):
        print(f"  第{turn_num}轮: {user_message}")
        
        # Get AI response based on API type
        if api_config.type == 'coze-agent':
            print("🤖 使用 Coze Agent API")
            # Extract access token properly
            access_token = api_config.headers.get('Authorization', '')
            if access_token.startswith('Bearer '):
                access_token = access_token.replace('Bearer ', '')
            
            print(f"🔑 Agent ID: {getattr(api_config, 'agentId', 'Not found')}")
            print(f"🔑 Region: {getattr(api_config, 'region', 'Not found')}")
            
            ai_response = await call_coze_agent_api(
                agent_id=getattr(api_config, 'agentId', ''),
                access_token=access_token,
                message=user_message,
                region=getattr(api_config, 'region', 'global')
            )
        elif api_config.type == 'coze-bot' or hasattr(api_config, 'botId'):
            print("🤖 使用 Coze Bot API")
            bot_id = getattr(api_config, 'botId', '')
            ai_response = await call_coze_api(bot_id, user_message)
        elif api_config.type == 'custom-api':
            print("🤖 使用自定义 API")
            ai_response = await call_api(api_config, user_message)
        else:
            print(f"❌ 未知的API类型: {api_config.type}")
            ai_response = f"API配置错误，无法识别的API类型: {api_config.type}"
        
        conversation_history.append({
            "turn": turn_num,
            "user_message": user_message,
            "ai_response": ai_response
        })
        
        # Truncate long responses for display
        display_response = ai_response[:100] + "..." if len(ai_response) > 100 else ai_response
        print(f"  AI回复: {display_response}")
    
    return conversation_history

async def evaluate_conversation_deepseek(
    conversation_history: List[Dict], 
    scenario: Dict, 
    requirement_context: str = "",
    evaluation_mode: str = "manual",
    user_persona_info: Dict = None
) -> tuple:
    """
    Enhanced DeepSeek evaluation with persona awareness
    """
    try:
        print("🧠 开始DeepSeek智能评估...")
        
        # Build enhanced context section
        context_section = f"""
业务场景: {scenario.get('context', '通用AI助手场景')}
用户画像: {scenario.get('user_profile', '普通用户')}
对话主题: {scenario.get('title', '')}
评估模式: {evaluation_mode}
"""
        
        # Add persona information if available
        if evaluation_mode == "auto" and user_persona_info:
            persona = user_persona_info.get('user_persona', {})
            context_section += f"""
提取的用户角色: {persona.get('role', '')}
用户经验水平: {persona.get('experience_level', '')}
沟通风格: {persona.get('communication_style', '')}
工作环境: {persona.get('work_environment', '')}
"""
        
        if requirement_context:
            context_section += f"\n需求文档上下文:\n{requirement_context[:1000]}"
        
        # Build conversation context
        conversation_text = ""
        for turn in conversation_history:
            conversation_text += f"用户: {turn['user_message']}\nAI: {turn['ai_response']}\n\n"
        
        # Enhanced evaluation prompts with persona awareness
        base_context = f"{context_section}\n\n对话记录:\n{conversation_text}\n"
        
        # Call the evaluation function
        return await perform_deepseek_evaluations({}, base_context, requirement_context)
        
    except Exception as e:
        print(f"❌ DeepSeek评估失败: {str(e)}")
        return {}, {}

def generate_enhanced_recommendations(evaluation_results: List[Dict], user_persona_info: Dict = None) -> List[str]:
    """
    Generate enhanced recommendations with persona awareness
    """
    recommendations = []
    
    if not evaluation_results:
        return ["⚠️ 无法生成建议：评估结果为空"]
    
    # Calculate average scores
    all_scores = {}
    for result in evaluation_results:
        scores = result.get("evaluation_scores", {})
        for dimension, score in scores.items():
            if dimension not in all_scores:
                all_scores[dimension] = []
            all_scores[dimension].append(score)
    
    avg_scores = {}
    for dimension, scores in all_scores.items():
        avg_scores[dimension] = sum(scores) / len(scores) if scores else 0
    
    overall_avg = sum(avg_scores.values()) / len(avg_scores) if avg_scores else 0
    
    # Overall performance assessment
    if overall_avg >= 4.5:
        recommendations.append("🟢 优秀表现！AI代理整体表现出色，能够有效处理各种用户需求")
    elif overall_avg >= 4.0:
        recommendations.append("🟡 良好表现！AI代理基本满足使用需求，有进一步优化空间")
    elif overall_avg >= 3.0:
        recommendations.append("🟠 中等表现！建议针对低分维度进行重点改进")
    else:
        recommendations.append("🔴 需要显著改进！建议重新设计对话策略和知识库")
    
    # Dimension-specific recommendations with persona awareness
    if avg_scores.get('fuzzy_understanding', 0) < 3.5:
        persona_context = ""
        if user_persona_info:
            persona_context = f"特别是对于{user_persona_info['user_persona']['role']}这类用户，"
        recommendations.append(f"💡 模糊理解能力需要加强：{persona_context}增加追问引导机制，提高对不明确需求的处理能力")
    
    if avg_scores.get('answer_correctness', 0) < 3.5:
        recommendations.append("📚 专业准确性需要提升：加强知识库建设，确保回答的专业性和准确性")
    
    if avg_scores.get('persona_alignment', 0) < 3.5:
        persona_context = ""
        if user_persona_info:
            style = user_persona_info['user_persona']['communication_style']
            persona_context = f"特别要匹配{style}的沟通风格，"
        recommendations.append(f"👥 用户匹配度有待改善：{persona_context}优化语言风格和专业术语使用")
    
    if avg_scores.get('goal_alignment', 0) < 3.5:
        recommendations.append("🎯 目标对齐度需要改进：确保回答能够满足用户的实际业务需求")
    
    # Add persona-specific recommendations
    if user_persona_info:
        persona = user_persona_info.get('user_persona', {})
        usage_context = user_persona_info.get('usage_context', {})
        
        if persona.get('work_environment'):
            recommendations.append(f"🏢 环境适配建议：针对{persona['work_environment']}环境，优化回答的实用性和可操作性")
        
        pain_points = usage_context.get('pain_points', [])
        if pain_points:
            recommendations.append(f"⚡ 痛点解决：重点关注{', '.join(pain_points[:2])}等用户痛点问题")
    
    return recommendations

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/evaluate-agent-with-file", response_model=EvaluationResponse)
async def evaluate_agent_with_file(
    agent_api_config: str = Form(...),
    requirement_file: UploadFile = File(None),
    requirement_text: str = Form(None),
    conversation_scenarios: str = Form(...),
    coze_bot_id: str = Form(None),
    evaluation_mode: str = Form("manual"),  # "auto" or "manual"
    extracted_persona: str = Form(None)     # JSON string of extracted persona
):
    """
    Enhanced evaluation endpoint supporting both automatic persona extraction and manual input
    """
    try:
        print("🤖============================================================🤖")
        print("   AI Agent 评估平台 v3.0 (增强模式)")
        print("🤖============================================================🤖")
        
        # Parse API configuration
        try:
            api_config_dict = json.loads(agent_api_config)
            api_config = APIConfig(**api_config_dict)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"API配置解析失败: {str(e)}")
        
        # Handle requirement document
        requirement_context = ""
        user_persona_info = None
        
        if evaluation_mode == "auto" and extracted_persona:
            # Use extracted persona information
            try:
                user_persona_info = json.loads(extracted_persona)
                print("🎭 Using extracted user persona information")
            except:
                print("⚠️ Failed to parse extracted persona, falling back to manual mode")
                evaluation_mode = "manual"
        
        if requirement_file and requirement_file.filename:
            print(f"📄 Processing uploaded file: {requirement_file.filename}")
            file_content = await requirement_file.read()
            
            if requirement_file.filename.endswith('.docx'):
                requirement_context = await extract_text_from_docx(file_content)
            elif requirement_file.filename.endswith('.pdf'):
                requirement_context = await extract_text_from_pdf(file_content)
            elif requirement_file.filename.endswith('.txt'):
                requirement_context = file_content.decode('utf-8', errors='ignore')
            else:
                print("⚠️ Unsupported file format, using text input instead")
                
        if not requirement_context and requirement_text:
            requirement_context = requirement_text
        
        # Parse conversation scenarios
        scenarios = []
        
        if evaluation_mode == "auto" and user_persona_info:
            # Auto mode: generate scenarios based on extracted persona
            print("🎯 Auto mode: Generating conversation scenarios based on extracted persona...")
            scenarios = await generate_conversation_scenarios_from_persona(user_persona_info)
            print(f"✅ Generated {len(scenarios)} scenarios based on user persona: {user_persona_info['user_persona']['role']}")
            
        else:
            # Manual mode or fallback: parse provided scenarios
            try:
                scenarios = json.loads(conversation_scenarios)
            except Exception as e:
                if evaluation_mode == "manual":
                    raise HTTPException(status_code=400, detail=f"场景配置解析失败: {str(e)}")
                else:
                    # Auto mode but no valid persona - generate basic scenarios
                    print("⚠️ Auto mode but no persona available, generating basic scenarios...")
                    scenarios = [
                        {
                            "title": "基础咨询场景",
                            "context": "通用咨询环境",
                            "user_profile": "普通用户",
                            "turns": ["我有个问题", "能详细说明一下吗", "谢谢"]
                        }
                    ]

        if not scenarios:
            if evaluation_mode == "auto":
                raise HTTPException(status_code=400, detail="自动模式下无法生成对话场景，请检查用户画像提取是否成功")
            else:
                raise HTTPException(status_code=400, detail="请至少配置一个对话场景")

        print(f"📋 Total scenarios to evaluate: {len(scenarios)}")
        
        # Enhanced evaluation with persona-aware context
        evaluation_results = []
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"📋 场景 {i}/{len(scenarios)}: {scenario.get('title', '未命名场景')}")
            
            # Enhance scenario with extracted persona if available
            if evaluation_mode == "auto" and user_persona_info:
                scenario = enhance_scenario_with_persona(scenario, user_persona_info)
                print(f"🎭 Enhanced scenario with extracted persona: {user_persona_info['user_persona']['role']}")
            
            result = await evaluate_single_conversation_scenario(
                api_config=api_config,
                scenario=scenario,
                requirement_context=requirement_context,
                evaluation_mode=evaluation_mode,
                user_persona_info=user_persona_info
            )
            
            if result:
                evaluation_results.append(result)
            else:
                print(f"⚠️ 场景 {i} 评估失败，跳过")

        if not evaluation_results:
            raise HTTPException(status_code=500, detail="所有场景评估均失败，请检查AI Agent配置")

        # Generate summary
        summary = generate_evaluation_summary(evaluation_results, requirement_context)
        
        # Enhanced recommendations with persona awareness
        recommendations = generate_enhanced_recommendations(evaluation_results, user_persona_info)
        
        response_data = {
            "evaluation_summary": summary,
            "conversation_records": evaluation_results,
            "recommendations": recommendations,
            "evaluation_mode": evaluation_mode,
            "user_persona_info": user_persona_info,
                "timestamp": datetime.now().isoformat()
        }
        
        print(f"🎯 总体评估完成！综合得分: {summary.get('overall_score', 0):.2f}/5.0")
        print(f"📊 评估模式: {evaluation_mode}")
        if user_persona_info:
            print(f"🎭 用户画像: {user_persona_info['user_persona']['role']}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Evaluation failed with error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"评估过程出错: {str(e)}")

@app.post("/api/evaluate-agent-dynamic", response_model=EvaluationResponse)
async def evaluate_agent_dynamic(
    agent_api_config: str = Form(...),
    requirement_file: UploadFile = File(None),
    requirement_text: str = Form(None),
    extracted_persona: str = Form(None)  # JSON string of extracted persona
):
    """
    New dynamic evaluation endpoint implementing conversational workflow:
    1. Extract persona from document
    2. Generate 2 scenarios with dynamic conversations
    3. Conduct 2-3 rounds per scenario based on AI responses
    4. Generate comprehensive final report
    """
    try:
        print("🚀============================================================🚀")
        print("   AI Agent 动态对话评估平台 v4.0")
        print("🚀============================================================🚀")
        
        # Parse API configuration
        try:
            api_config_dict = json.loads(agent_api_config)
            api_config = APIConfig(**api_config_dict)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"API配置解析失败: {str(e)}")
        
        # Handle requirement document
        requirement_context = ""
        user_persona_info = None
        
        # Step 1: Process requirement document and extract persona
        if requirement_file and requirement_file.filename:
            print(f"📄 Processing uploaded file: {requirement_file.filename}")
            requirement_context = await process_uploaded_document_improved(requirement_file)
        elif requirement_text:
            requirement_context = requirement_text
        
        if not requirement_context:
            raise HTTPException(status_code=400, detail="请提供需求文档或文本内容")
        
        # Step 2: Extract user persona from requirement document using DeepSeek
        if extracted_persona:
            try:
                user_persona_info = json.loads(extracted_persona)
                print(f"🎭 使用提取的用户画像: {user_persona_info.get('user_persona', {}).get('role', '未知角色')}")
            except:
                print("⚠️ 画像数据解析失败，重新提取...")
                user_persona_info = None
        
        if not user_persona_info:
            print("🧠 从需求文档中提取用户画像...")
            user_persona_info = await extract_user_persona_with_deepseek(requirement_context)
            if not user_persona_info:
                raise HTTPException(status_code=400, detail="无法从需求文档中提取有效的用户画像信息")
        
        # Step 3: Conduct dynamic multi-scenario evaluation
        print("🎯 开始动态多轮对话评估...")
        evaluation_results = await conduct_dynamic_multi_scenario_evaluation(
            api_config, user_persona_info, requirement_context
        )
        
        if not evaluation_results:
            raise HTTPException(status_code=500, detail="动态对话评估失败，请检查AI Agent配置")
        
        # Step 4: Generate comprehensive final report
        print("📊 生成综合评估报告...")
        comprehensive_report = await generate_final_comprehensive_report(
            evaluation_results, user_persona_info, requirement_context
        )
        
        # Calculate overall summary
        overall_score = sum(r.get('scenario_score', 0) for r in evaluation_results) / len(evaluation_results) if evaluation_results else 0
        total_conversations = sum(len(r.get('conversation_history', [])) for r in evaluation_results)
        
        response_data = {
            "evaluation_summary": {
                "overall_score": overall_score,
                "total_scenarios": len(evaluation_results),
                "total_conversations": total_conversations,
                "framework": "动态多轮对话评估",
                "comprehensive_analysis": comprehensive_report,
                "extracted_persona_display": {
                    "user_role": user_persona_info.get('user_persona', {}).get('role', '专业用户'),
                    "business_domain": user_persona_info.get('usage_context', {}).get('business_domain', '专业服务'),
                    "experience_level": user_persona_info.get('user_persona', {}).get('experience_level', '中等经验'),
                    "communication_style": user_persona_info.get('user_persona', {}).get('communication_style', '专业沟通'),
                    "work_environment": user_persona_info.get('user_persona', {}).get('work_environment', '专业工作环境'),
                    "extraction_method": "DeepSeek智能提取分析"
                }
            },
            "conversation_records": evaluation_results,
            "recommendations": comprehensive_report.get('improvement_recommendations', []),
            "extracted_persona_full": comprehensive_report.get('extracted_persona_summary', {}),
            "persona_alignment_analysis": comprehensive_report.get('persona_alignment_analysis', ''),
            "business_goal_achievement": comprehensive_report.get('business_goal_achievement', ''),
            "evaluation_mode": "dynamic",
            "user_persona_info": user_persona_info,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"🎯 动态评估完成！综合得分: {overall_score:.2f}/5.0")
        print(f"📊 评估场景: {len(evaluation_results)} 个")
        print(f"💬 对话轮次: {total_conversations} 轮")
        print(f"🎭 用户画像: {user_persona_info.get('user_persona', {}).get('role', '未知角色')}")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Dynamic evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"动态评估过程出错: {str(e)}")

def enhance_scenario_with_persona(scenario: Dict, user_persona_info: Dict) -> Dict:
    """
    Enhance conversation scenario with extracted user persona information
    """
    enhanced_scenario = scenario.copy()
    
    persona = user_persona_info.get('user_persona', {})
    context = user_persona_info.get('usage_context', {})
    ai_role = user_persona_info.get('ai_role_simulation', {})
    
    # Enhance user profile
    if not scenario.get('user_profile') or scenario.get('user_profile') == '':
        enhanced_scenario['user_profile'] = f"{persona.get('role', '专业用户')}，{persona.get('experience_level', '有经验')}"
    
    # Enhance context if not provided
    if not scenario.get('context') or scenario.get('context') == '':
        work_env = persona.get('work_environment', '')
        business_domain = context.get('business_domain', '')
        enhanced_scenario['context'] = f"{work_env} - {business_domain}" if work_env and business_domain else work_env or business_domain or "专业工作环境"
    
    # Add persona-aware conversation approach
    enhanced_scenario['conversation_approach'] = ai_role.get('conversation_approach', '直接专业提问')
    enhanced_scenario['language_style'] = ai_role.get('language_characteristics', '专业术语与通俗解释结合')
    
    return enhanced_scenario

async def evaluate_single_conversation_scenario(
    api_config: APIConfig,
    scenario: Dict,
    requirement_context: str = "",
    evaluation_mode: str = "manual",
    user_persona_info: Dict = None
) -> Optional[Dict]:
    """
    Enhanced single scenario evaluation with persona awareness
    """
    try:
        print(f"🗣️ 开始对话场景: {scenario.get('title', '未命名场景')}")
        
        conversation_history = []
        turns = scenario.get('turns', [])
        
        if not turns:
            print("⚠️ 场景没有配置对话轮次")
            return None
            
        # Enhanced conversation simulation with persona context
        for turn_num, user_message in enumerate(turns, 1):
            if not user_message.strip():
                continue
                
            print(f"💬 第 {turn_num} 轮对话: {user_message[:50]}...")
            
            # Add persona context to the message if in auto mode
            enhanced_message = user_message
            if evaluation_mode == "auto" and user_persona_info:
                persona_context = f"[作为{user_persona_info['user_persona']['role']}，{user_persona_info['user_persona']['communication_style']}] {user_message}"
                enhanced_message = persona_context
            
            try:
                ai_response = await call_ai_agent_api(api_config, enhanced_message)
                
                if ai_response:
                    conversation_history.append({
                        "turn": turn_num,
                        "user_message": user_message,  # Store original message for display
                        "enhanced_message": enhanced_message if evaluation_mode == "auto" else user_message,
                        "ai_response": ai_response
                    })
                    print(f"✅ AI响应: {ai_response[:100]}...")
                else:
                    print(f"❌ 第 {turn_num} 轮AI无响应")
                    
            except Exception as e:
                print(f"❌ 第 {turn_num} 轮对话失败: {str(e)}")
                continue
        
        if not conversation_history:
            print("❌ 场景对话完全失败")
            return None
        
        # Enhanced evaluation with persona awareness
        evaluation_scores, explanations = await evaluate_conversation_with_deepseek(
            conversation_history, scenario, requirement_context, user_persona_info
        )
        
        scenario_score = sum(evaluation_scores.values()) / len(evaluation_scores) if evaluation_scores else 0
        print(f"🎯 场景得分: {scenario_score:.2f}/5.0")
        
        return {
            "scenario": {
                "title": scenario.get('title', '未命名场景'),
                "context": f"{user_persona_info.get('usage_context', {}).get('business_domain', '专业服务') if user_persona_info else scenario.get('context', '专业工作环境')} - {scenario.get('context', '专业工作环境')}",
                "user_profile": f"{user_persona_info.get('user_persona', {}).get('role', '用户') if user_persona_info else scenario.get('user_profile', '用户')}，{user_persona_info.get('user_persona', {}).get('experience_level', '中等经验') if user_persona_info else '中等经验'}，{user_persona_info.get('user_persona', {}).get('communication_style', '专业沟通') if user_persona_info else '专业沟通'}"
            },
            "conversation_history": conversation_history,
            "evaluation_scores": evaluation_scores,
            "explanations": explanations,
            "scenario_score": scenario_score,
            "evaluation_mode": evaluation_mode,
            "persona_enhanced": evaluation_mode == "auto" and user_persona_info is not None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ 场景评估异常: {str(e)}")
        return None

async def perform_deepseek_evaluations(evaluation_prompts: Dict, base_context: str, requirement_context: str) -> tuple:
    """
    Perform DeepSeek evaluations for all dimensions
    """
    try:
        # Standard evaluation prompts 
        if not evaluation_prompts:  # If prompts not provided, create them
            evaluation_prompts = {
                "fuzzy_understanding": f"""
{base_context}

请评估AI在模糊理解与追问能力方面的表现。

评分标准 (1-5分):
1分: 完全无法理解模糊表达，直接给出错误或无关回答
2分: 理解错误且未主动追问，可能误导用户
3分: 部分理解但引导不足，仅给出部分有用信息
4分: 基本理解模糊表达且有一定引导，但追问不够深入
5分: 准确理解模糊表达并有效引导用户澄清需求

请给出具体评分和详细理由。
""",
                "answer_correctness": f"""
{base_context}

请评估AI回答的准确性与专业性。

评分标准 (1-5分):
1分: 回答错误，包含危险信息或严重误导
2分: 表面看起来合理但核心内容错误
3分: 大部分正确但有明显缺漏或不够准确
4分: 基本准确专业但缺少规范引用或细节
5分: 完全准确且专业，有规范依据和实用指导

请给出具体评分和详细理由。
""",
                "persona_alignment": f"""
{base_context}

请评估AI与用户画像的匹配度。

评分标准 (1-5分):
1分: 沟通风格完全不符合用户背景
2分: 用词过于专业或过于简单，用户难以理解
3分: 基本可以理解但存在术语使用不当
4分: 沟通风格基本合适，偶有不匹配
5分: 完全贴合用户角色和沟通偏好

请给出具体评分和详细理由。
"""
            }
            
            # Add goal alignment if requirement context exists
            if requirement_context.strip():
                evaluation_prompts["goal_alignment"] = f"""
{base_context}

基于提供的需求文档，请评估AI是否达成了预期的目标对齐度。

评分标准 (1-5分):
1分: 完全偏离需求目标，未解决任何关键问题
2分: 部分相关但未达成主要目标
3分: 基本符合需求但有重要遗漏
4分: 很好地满足了大部分需求目标
5分: 完美对齐所有需求目标，超出预期

请给出具体评分和详细理由。
"""
        
        # Execute evaluations concurrently for better performance
        evaluation_results = {}
        explanations = {}
        
        for dimension, prompt in evaluation_prompts.items():
            try:
                print(f"  📊 Evaluating {dimension}...")
                response = await call_deepseek_api(prompt)
                score = extract_score_from_response(response)
                
                evaluation_results[dimension] = score
                explanations[dimension] = response
                
                print(f"  ✅ {dimension}: {score}/5")
                
            except Exception as e:
                print(f"  ❌ Failed to evaluate {dimension}: {str(e)}")
                evaluation_results[dimension] = 3.0  # Default score
                explanations[dimension] = f"评估失败: {str(e)}"
        
        return evaluation_results, explanations
        
    except Exception as e:
        print(f"❌ Evaluation process failed: {str(e)}")
        return {}, {}

def generate_evaluation_summary(evaluation_results: List[Dict], requirement_context: str = "") -> Dict:
    """
    Generate evaluation summary from results
    """
    if not evaluation_results:
        return {
            "overall_score": 0.0,
            "total_scenarios": 0,
            "total_conversations": 0,
            "framework": "评估失败",
            "dimensions": {}
        }
        
        # Calculate dimension averages
    all_scores = {}
    total_conversations = 0
    
    for result in evaluation_results:
        scores = result.get("evaluation_scores", {})
        conversation_history = result.get("conversation_history", [])
        total_conversations += len(conversation_history)
        
        for dimension, score in scores.items():
            if dimension not in all_scores:
                all_scores[dimension] = []
            all_scores[dimension].append(score)
    
    # Calculate averages
    dimension_averages = {}
    for dimension, scores in all_scores.items():
        dimension_averages[dimension] = sum(scores) / len(scores) if scores else 0
    
    overall_score = sum(dimension_averages.values()) / len(dimension_averages) if dimension_averages else 0
    
    return {
            "overall_score": round(overall_score, 2),
        "total_scenarios": len(evaluation_results),
        "total_conversations": total_conversations,
        "framework": "AI Agent 3维度评估框架",
        "dimensions": dimension_averages
    }

def generate_enhanced_recommendations(evaluation_results: List[Dict], user_persona_info: Dict = None) -> List[str]:
    """
    Generate enhanced recommendations based on evaluation results and user persona
    """
    recommendations = []
    
    if not evaluation_results:
        return [
            "无法生成推荐建议，请先完成有效的评估",
            "检查AI Agent配置和网络连接",
            "确保对话场景配置正确"
        ]
    
    # Analyze scores to identify weak areas
    all_scores = {}
    for result in evaluation_results:
        scores = result.get("evaluation_scores", {})
        for dimension, score in scores.items():
            if dimension not in all_scores:
                all_scores[dimension] = []
            all_scores[dimension].append(score)
    
    # Calculate averages and identify weak points
    weak_areas = []
    for dimension, scores in all_scores.items():
        avg_score = sum(scores) / len(scores) if scores else 0
        if avg_score < 3.0:
            weak_areas.append((dimension, avg_score))
    
    # Sort by score (weakest first)
    weak_areas.sort(key=lambda x: x[1])
    
    # Generate specific recommendations based on weak areas
    dimension_recommendations = {
        "fuzzy_understanding": [
            "加强AI对模糊问题的理解能力",
            "增强主动追问和澄清需求的机制",
            "提高对用户意图的推理准确性"
        ],
        "answer_correctness": [
            "提升回答的准确性和专业度",
            "加强知识库的完整性和时效性",
            "增加规范和标准的引用支持"
        ],
        "persona_alignment": [
            "优化AI的沟通风格适配能力",
            "根据用户背景调整回答的复杂度",
            "提高对不同用户群体的个性化服务"
        ],
        "goal_alignment": [
            "更好地理解和对齐业务目标",
            "增强对需求文档的深度理解",
            "提高解决方案的针对性和实用性"
        ]
    }
    
    # Add recommendations for weak areas
    for dimension, score in weak_areas[:3]:  # Focus on top 3 weak areas
        if dimension in dimension_recommendations:
            recommendations.extend(dimension_recommendations[dimension])
    
    # Add persona-specific recommendations if available
    if user_persona_info:
        persona = user_persona_info.get('user_persona', {})
        role = persona.get('role', '')
        
        if '工程师' in role:
            recommendations.append("增强对技术规范和标准的引用能力")
        elif '客服' in role:
            recommendations.append("优化客户服务场景的响应效率")
        elif '管理' in role:
            recommendations.append("提供更多决策支持和数据分析")
        
        communication_style = persona.get('communication_style', '')
        if '简洁' in communication_style:
            recommendations.append("优化回答的简洁性，突出核心要点")
        elif '详细' in communication_style:
            recommendations.append("提供更详细的解释和背景信息")
    
    # Add general improvement suggestions
    if len(recommendations) < 3:
        recommendations.extend([
            "加强多轮对话的上下文理解能力",
            "提高回答的逻辑性和结构化程度",
            "增强对特殊情况和边界条件的处理"
        ])
    
    # Limit to 5 recommendations and ensure uniqueness
    unique_recommendations = list(dict.fromkeys(recommendations))
    return unique_recommendations[:5]

# Keep the old API endpoint for backward compatibility
@app.post("/api/evaluate-agent")
async def evaluate_agent_legacy(request: dict):
    """
    Legacy API endpoint for backward compatibility
    """
    try:
        print("🔄 Legacy API endpoint called, redirecting to new implementation...")
        
        # Convert old format to new format
        agent_api_config = json.dumps(request.get("agent_api", {}))
        requirement_doc = request.get("requirement_doc", "")
        conversation_scenarios = json.dumps(request.get("conversation_scenarios", []))
        
        # Call the new implementation
        return await evaluate_agent_with_file(
            agent_api_config=agent_api_config,
            requirement_file=None,
            requirement_text=requirement_doc,
            conversation_scenarios=conversation_scenarios,
            coze_bot_id=request.get("coze_bot_id"),
            evaluation_mode="manual",
            extracted_persona=None
        )
        
    except Exception as e:
        print(f"❌ Legacy API call failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Legacy API evaluation failed: {str(e)}")

# Temporary endpoint for Coze compatibility (will be phased out)
@app.post("/evaluate-coze-auto")
async def evaluate_coze_auto(bot_id: str = None):
    """Temporary Coze compatibility endpoint"""
    try:
        # Import the legacy function temporarily
        from coze_auto_test import run_simplified_evaluation
        
        report = await run_simplified_evaluation(bot_id)
        
        # Return in the format expected by current frontend
        return {
            "success": True,
            "report": report,  # This contains evaluation_summary
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/schema")
async def get_api_schema():
    """Get API schema for integration"""
    return {
        "evaluation_request_example": {
            "agent_api": {
                "type": "http",
                "url": "https://your-agent.com/api/converse",
                "method": "POST"
            },
            "requirement_doc": "在墙面抹灰检测任务中，AI应识别出用户模糊描述并主动引导补充面积、位置、责任方等字段...",
            "conversation_scenarios": [
                {
                    "title": "高层建筑墙面空鼓问题",
                    "turns": [
                        "三楼有个地方空鼓了",
                        "是墙面",
                        "差不多两平米"
                    ]
                }
            ]
        },
        "response_format": {
            "evaluation_summary": {
                "overall_score": 4.67,
                "dimensions": {
                    "fuzzy_understanding": 5,
                    "answer_correctness": 4,
                    "persona_alignment": 5,
                    "goal_alignment": 4
                }
            }
        }
    }

def find_available_port(start_port: int = 8000, max_port: int = 8010) -> int:
    """Find an available port starting from start_port"""
    for port in range(start_port, max_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result != 0:
                return port
        except:
            continue
    return start_port

async def call_coze_agent_api(agent_id: str, access_token: str, message: str, region: str = "global") -> str:
    """Call Coze Agent API using v3 endpoint with polling for completion"""
    max_retries = 3
    
    # Determine API base URL - fix region detection
    base_url = "https://api.coze.cn" if region == "china" else "https://api.coze.com"
    print(f"🌍 Using region: {region}, base URL: {base_url}")
    
    for attempt in range(max_retries):
        try:
            chat_url = f"{base_url}/v3/chat"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Fix: Use proper agent_id instead of bot_id for v3 chat
            payload = {
                "bot_id": agent_id,  # This is correct for v3 API - bot_id is used for both bots and agents
                "user_id": f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "stream": False,
                "auto_save_history": True,
                "additional_messages": [
                    {
                        "role": "user",
                        "content": message,
                        "content_type": "text"
                    }
                ]
            }
            
            print(f"🔄 Coze Agent API 调用尝试 {attempt + 1}/{max_retries}")
            print(f"📍 URL: {chat_url}")
            print(f"🤖 Agent ID: {agent_id}")
            print(f"🔑 Token: {access_token[:20]}...")
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                # Start conversation
                response = await client.post(chat_url, headers=headers, json=payload)
                
                print(f"📡 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Coze Agent API 响应: {result}")
                    
                    if result.get("code") == 0 and "data" in result:
                        conversation_id = result["data"].get("conversation_id")
                        chat_id = result["data"].get("id")
                        status = result["data"].get("status")
                        
                        print(f"💬 对话ID: {conversation_id}")
                        print(f"📝 聊天ID: {chat_id}")
                        print(f"📊 状态: {status}")
                        
                        # Use the working GET endpoint for message retrieval
                        messages_url = f"{base_url}/v1/conversation/message/list?conversation_id={conversation_id}&chat_id={chat_id}"
                        
                        # If status is completed, try to get messages immediately
                        if status == "completed":
                            print("🎉 对话已完成，获取消息...")
                            messages_response = await client.get(messages_url, headers=headers)
                            
                            if messages_response.status_code == 200:
                                messages_result = messages_response.json()
                                if messages_result.get("code") == 0 and "data" in messages_result:
                                    messages = messages_result["data"]
                                    for msg in messages:
                                        if msg.get("role") == "assistant":
                                            content = msg.get("content", "")
                                            if content and len(content.strip()) > 0:
                                                print(f"✅ Coze Agent 成功响应")
                                                return content
                        
                        elif status == "in_progress":
                            # Enhanced polling for completion - increased for workflow-based agents
                            print("⏳ 对话处理中，开始轮询...")
                            max_polls = 40  # Increase to 40 polls for workflow agents
                            poll_interval = 4  # Increase to 4 seconds for better stability
                            
                            for poll in range(max_polls):
                                await asyncio.sleep(poll_interval)
                                
                                # Get messages using the working GET endpoint
                                messages_response = await client.get(messages_url, headers=headers)
                                print(f"📋 轮询 {poll + 1}/{max_polls}: {messages_response.status_code}")
                                
                                if messages_response.status_code == 200:
                                    messages_result = messages_response.json()
                                    
                                    if messages_result.get("code") == 0 and "data" in messages_result:
                                        messages = messages_result["data"]
                                        print(f"📋 找到 {len(messages)} 条消息")
                                        
                                        # Look for assistant response
                                        for msg in messages:
                                            if msg.get("role") == "assistant":
                                                content = msg.get("content", "")
                                                msg_type = msg.get("type", "")
                                                print(f"📝 助手消息类型: {msg_type}, 内容长度: {len(content)}")
                                                
                                                # Accept any non-empty content from assistant
                                                if content and len(content.strip()) > 0:
                                                    print(f"✅ Coze Agent 轮询成功响应")
                                                    return content
                                        
                                        # Check if there are any error messages
                                        for msg in messages:
                                            if msg.get("type") == "error":
                                                error_content = msg.get("content", "")
                                                print(f"❌ 发现错误消息: {error_content}")
                                                return f"Agent处理失败: {error_content}"
                                    else:
                                        error_code = messages_result.get("code", "unknown")
                                        error_msg = messages_result.get("msg", "unknown error")
                                        print(f"❌ 消息列表API错误: code={error_code}, msg={error_msg}")
                                else:
                                    print(f"❌ 消息列表API HTTP错误: {messages_response.status_code}")
                                
                                # Check if we should continue polling
                                if poll >= max_polls - 1:
                                    print("⏰ 轮询超时，尝试重试...")
                                    break
                            
                            # If agent didn't respond, try fallback to Coze Bot API
                            print("🔄 Agent未响应，尝试使用Coze Bot API作为备用...")
                            fallback_response = await call_coze_api_fallback(message, "7511993619423985674")
                            if fallback_response and "API调用失败" not in fallback_response:
                                print("✅ Coze Bot API备用成功")
                                return f"[备用Bot回复] {fallback_response}"
                            else:
                                print("❌ 备用API也失败")
                                return "Agent和备用Bot都未能响应，请检查配置"
                        
                        elif status == "failed":
                            error_msg = result["data"].get("last_error", {}).get("msg", "未知错误")
                            print(f"❌ 对话失败: {error_msg}")
                            return f"对话失败: {error_msg}"
                    
                    elif result.get("code") != 0:
                        error_msg = result.get("msg", "API调用失败")
                        print(f"❌ API错误: {error_msg}")
                        return f"API错误: {error_msg}"
                    
                    print(f"⚠️ Coze Agent API 未能获取有效响应")
                else:
                    response_text = response.text
                    print(f"⚠️ Coze Agent API HTTP错误: {response.status_code}")
                    print(f"响应内容: {response_text}")
                    
                    # Parse error response if possible
                    try:
                        error_result = response.json()
                        if "msg" in error_result:
                            return f"API调用失败: {error_result['msg']}"
                    except:
                        pass
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                        
        except Exception as e:
            print(f"❌ Coze Agent API调用异常 (尝试 {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue
    
    return "Coze Agent API调用失败，请检查Agent ID和Access Token是否正确"

# Add new endpoint for user persona extraction
@app.post("/api/extract-user-persona")
async def extract_user_persona_from_document(
    requirement_file: UploadFile = File(None),
    requirement_text: str = Form(None)
):
    """
    Extract user persona and context from requirement document using DeepSeek
    Uses improved document processing approach with temporary files
    """
    try:
        print("🔍============================================================🔍")
        print("   用户画像提取服务 (DeepSeek智能分析) - 优化版本")
        print("🔍============================================================🔍")
        
        # Extract requirement text
        requirement_content = ""
        
        if requirement_file and requirement_file.filename:
            print(f"📄 Processing uploaded file: {requirement_file.filename}")
            
            # Use improved document processing
            requirement_content = await process_uploaded_document_improved(requirement_file)
                
        elif requirement_text and requirement_text.strip():
            print("📝 Using provided text content")
            requirement_content = requirement_text.strip()
            # Clean the text using the same approach
            requirement_content = requirement_content.replace("\r", "").replace("　", "").strip()
            print(f"📄 文本内容长度: {len(requirement_content)} 字符")
        else:
            raise HTTPException(status_code=400, detail="请提供需求文档文件或文本内容")
        
        # Check if extraction was successful
        if not requirement_content or requirement_content.strip() == "":
            raise HTTPException(status_code=400, detail="文档内容提取失败或为空，请检查文件格式和内容")
        
        # Check for extraction errors
        if "解析失败" in requirement_content or "处理失败" in requirement_content:
            raise HTTPException(status_code=400, detail=f"文档处理错误: {requirement_content}")
        
        # Ensure minimum content length for meaningful analysis
        if len(requirement_content.strip()) < 50:
            raise HTTPException(
                status_code=400, 
                detail=f"文档内容过短({len(requirement_content)}字符)，无法进行有效的用户画像分析。请提供更详细的需求文档（建议至少100字符）"
            )
        
        print(f"📄 Document content successfully extracted: {len(requirement_content)} characters")
        print(f"📄 Content preview: {requirement_content[:200]}...")
        
        # Call DeepSeek to extract user persona and context
        extraction_result = await extract_user_persona_with_deepseek(requirement_content)
        
        print("✅ User persona extraction completed successfully")
        return {
            "success": True,
            "extraction_result": extraction_result,
            "document_preview": requirement_content[:300] + "..." if len(requirement_content) > 300 else requirement_content,
            "document_length": len(requirement_content),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ User persona extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"用户画像提取失败: {str(e)}")

async def extract_user_persona_with_deepseek(requirement_content: str) -> Dict[str, Any]:
    """
    Use DeepSeek to extract user persona, context, and role information from requirement document
    """
    
    extraction_prompt = f"""
请仔细分析以下需求文档，提取用户画像信息。请务必严格按照JSON格式返回，不要添加任何其他文字。

需求文档内容：
{requirement_content}

请返回以下格式的JSON（必须是有效的JSON格式，不要有任何额外文字）：

{{
    "user_persona": {{
        "role": "具体用户角色，如：银行客服代表、现场监理工程师等",
        "experience_level": "经验水平描述，如：2-8年客服经验、5年工程经验等", 
        "expertise_areas": ["专业领域1", "专业领域2"],
        "communication_style": "沟通风格，如：习惯使用专业术语、偏好简洁明了等",
        "work_environment": "工作环境描述，如：呼叫中心、建筑工地现场等"
    }},
    "usage_context": {{
        "primary_scenarios": ["主要使用场景1", "主要使用场景2"],
        "business_domain": "业务领域，如：银行客服、工程监理等",
        "interaction_goals": ["用户目标1", "用户目标2"],
        "pain_points": ["痛点问题1", "痛点问题2"]
    }},
    "ai_role_simulation": {{
        "simulated_user_type": "模拟用户类型的详细描述",
        "conversation_approach": "对话方式，如：快速提问、详细咨询等", 
        "language_characteristics": "语言特点，如：使用专业术语、口语化表达等",
        "typical_questions": ["典型问题1", "典型问题2", "典型问题3"]
    }},
    "extracted_requirements": {{
        "core_functions": ["核心功能需求1", "核心功能需求2"],
        "quality_expectations": ["质量期望1", "质量期望2"],
        "interaction_preferences": ["交互偏好1", "交互偏好2"]
    }}
}}

重要：只返回JSON内容，不要有任何解释或其他文字。"""

    try:
        print("🧠 Calling DeepSeek API for user persona extraction...")
        
        response = await call_deepseek_api(extraction_prompt)
        print(f"📝 DeepSeek raw response: {response[:200]}...")
        
        # Clean the response - remove any markdown formatting or extra text
        cleaned_response = response.strip()
        
        # Remove markdown code blocks if present
        if cleaned_response.startswith('```'):
            lines = cleaned_response.split('\n')
            cleaned_response = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned_response
        
        # Remove any text before the first { and after the last }
        start_idx = cleaned_response.find('{')
        end_idx = cleaned_response.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = cleaned_response[start_idx:end_idx+1]
            
            try:
                extraction_result = json.loads(json_str)
                print("✅ Successfully parsed extraction result from DeepSeek")
                
                # Validate the structure
                required_keys = ['user_persona', 'usage_context', 'ai_role_simulation', 'extracted_requirements']
                if all(key in extraction_result for key in required_keys):
                    return extraction_result
                else:
                    print("⚠️ JSON structure incomplete, using fallback")
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed: {e}, trying alternative parsing...")
        
        # If JSON parsing fails, try to extract specific information from the response
        print("📝 Creating enhanced structured response from text...")
        return create_enhanced_extraction_result(response, requirement_content)
        
    except Exception as e:
        print(f"❌ DeepSeek extraction error: {e}")
        # Return a basic fallback result
        return create_basic_fallback_result(requirement_content)

def create_enhanced_extraction_result(response: str, requirement_content: str) -> Dict[str, Any]:
    """
    Create an enhanced structured result when JSON parsing fails but we have DeepSeek response
    """
    # Try to extract information from both the response and the original content
    lines = response.split('\n') + requirement_content.split('\n')
    
    # Extract role information
    role = extract_role_from_content(requirement_content) or extract_info_from_lines(lines, ["角色", "用户", "身份", "代表"]) or "专业用户"
    
    # Extract experience level
    experience = extract_experience_from_content(requirement_content) or extract_info_from_lines(lines, ["经验", "年限", "水平"]) or "有经验用户"
    
    # Extract work environment
    work_env = extract_work_environment_from_content(requirement_content) or extract_info_from_lines(lines, ["环境", "现场", "地点", "中心"]) or "专业工作环境"
    
    # Extract business domain
    business_domain = extract_business_domain_from_content(requirement_content) or "专业服务"
    
    return {
        "user_persona": {
            "role": role,
            "experience_level": experience,
            "expertise_areas": extract_expertise_areas_from_content(requirement_content),
            "communication_style": extract_communication_style_from_content(requirement_content),
            "work_environment": work_env
        },
        "usage_context": {
            "primary_scenarios": extract_scenarios_from_content(requirement_content),
            "business_domain": business_domain,
            "interaction_goals": extract_goals_from_content(requirement_content),
            "pain_points": extract_pain_points_from_content(requirement_content)
        },
        "ai_role_simulation": {
            "simulated_user_type": f"基于{business_domain}领域的{role}",
            "conversation_approach": "结合实际工作场景的专业提问",
            "language_characteristics": "专业术语与实际需求相结合",
            "typical_questions": generate_typical_questions_from_content(requirement_content)
        },
        "extracted_requirements": {
            "core_functions": extract_requirements_from_content(requirement_content),
            "quality_expectations": extract_quality_expectations_from_content(requirement_content),
            "interaction_preferences": extract_interaction_preferences_from_content(requirement_content)
        }
    }

def extract_role_from_content(content: str) -> Optional[str]:
    """Extract user role from content"""
    role_patterns = [
        r'用户群体[：:]\s*([^\n]+)',
        r'主要用户[：:]\s*([^\n]+)',
        r'目标用户[：:]\s*([^\n]+)',
        r'用户角色[：:]\s*([^\n]+)'
    ]
    
    for pattern in role_patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
    
    # Look for specific role mentions
    if "客服" in content:
        return "客服代表"
    elif "监理" in content:
        return "现场监理工程师"
    elif "工程师" in content:
        return "工程师"
    elif "技术" in content:
        return "技术人员"
    
    return None

def extract_experience_from_content(content: str) -> Optional[str]:
    """Extract experience level from content"""
    exp_patterns = [
        r'(\d+[-~]\d+年[^，。\n]*经验)',
        r'(工作经验[：:][^，。\n]+)',
        r'(经验水平[：:][^，。\n]+)'
    ]
    
    for pattern in exp_patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
    
    return None

def extract_work_environment_from_content(content: str) -> Optional[str]:
    """Extract work environment from content"""
    env_patterns = [
        r'工作环境[：:]\s*([^，。\n]+)',
        r'环境[：:]\s*([^，。\n]+)'
    ]
    
    for pattern in env_patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
    
    # Look for specific environment mentions
    if "呼叫中心" in content:
        return "呼叫中心"
    elif "现场" in content or "工地" in content:
        return "施工现场"
    elif "办公室" in content:
        return "办公室环境"
    
    return None

def extract_business_domain_from_content(content: str) -> str:
    """Extract business domain from content"""
    if "银行" in content or "金融" in content:
        return "银行金融服务"
    elif "建筑" in content or "工程" in content:
        return "建筑工程"
    elif "客服" in content:
        return "客户服务"
    elif "技术" in content:
        return "技术支持"
    else:
        return "专业服务"

def extract_expertise_areas_from_content(content: str) -> List[str]:
    """Extract expertise areas from content"""
    areas = []
    
    if "客服" in content:
        areas.extend(["客户服务", "业务咨询"])
    if "金融" in content or "银行" in content:
        areas.extend(["金融产品", "银行业务"])
    if "工程" in content or "建筑" in content:
        areas.extend(["工程技术", "质量管理"])
    if "技术" in content:
        areas.extend(["技术支持", "系统操作"])
    
    return areas if areas else ["专业技术", "行业知识"]

def extract_communication_style_from_content(content: str) -> str:
    """Extract communication style from content"""
    if "专业术语" in content:
        return "习惯使用专业术语"
    elif "简洁" in content or "快速" in content:
        return "偏好简洁明了的沟通"
    elif "结构化" in content or "条理" in content:
        return "偏好结构化、条理清晰的回答"
    else:
        return "专业术语与通俗解释结合"

def extract_scenarios_from_content(content: str) -> List[str]:
    """Extract primary scenarios from content"""
    scenarios = []
    
    # Look for numbered lists or bullet points
    scenario_patterns = [
        r'\d+\.\s*([^\n]+)',
        r'-\s*([^\n]+场景[^\n]*)',
        r'•\s*([^\n]+)'
    ]
    
    for pattern in scenario_patterns:
        matches = re.findall(pattern, content)
        scenarios.extend([match.strip() for match in matches[:3]])  # Limit to 3
    
    if not scenarios:
        if "查询" in content:
            scenarios.append("信息查询")
        if "咨询" in content:
            scenarios.append("业务咨询")
        if "问题解决" in content or "处理" in content:
            scenarios.append("问题解决")
    
    return scenarios if scenarios else ["技术咨询", "问题解决"]

def extract_goals_from_content(content: str) -> List[str]:
    """Extract interaction goals from content"""
    goals = []
    
    if "准确" in content:
        goals.append("获取准确信息")
    if "快速" in content or "迅速" in content:
        goals.append("快速响应")
    if "解决" in content:
        goals.append("解决实际问题")
    if "效率" in content:
        goals.append("提高工作效率")
    
    return goals if goals else ["获取准确信息", "解决实际问题"]

def extract_pain_points_from_content(content: str) -> List[str]:
    """Extract pain points from content"""
    pain_points = []
    
    if "响应时间" in content or "慢" in content:
        pain_points.append("响应速度慢")
    if "准确" in content:
        pain_points.append("信息不够准确")
    if "压力" in content:
        pain_points.append("工作压力大")
    if "复杂" in content:
        pain_points.append("操作过于复杂")
    
    return pain_points if pain_points else ["信息获取困难", "响应不及时"]

def extract_quality_expectations_from_content(content: str) -> List[str]:
    """Extract quality expectations from content"""
    expectations = []
    
    if "准确率" in content or "95%" in content:
        expectations.append("高准确率(95%以上)")
    if "响应时间" in content or "3秒" in content:
        expectations.append("快速响应(3秒内)")
    if "合规" in content:
        expectations.append("符合合规要求")
    
    return expectations if expectations else ["高准确性", "快速响应", "专业可靠"]

def extract_interaction_preferences_from_content(content: str) -> List[str]:
    """Extract interaction preferences from content"""
    preferences = []
    
    if "结构化" in content:
        preferences.append("结构化回答")
    if "条理" in content:
        preferences.append("条理清晰")
    if "模板" in content:
        preferences.append("标准化模板")
    if "语音" in content:
        preferences.append("支持语音输入")
    
    return preferences if preferences else ["清晰明了", "逻辑清楚", "实用可行"]

def generate_typical_questions_from_content(content: str) -> List[str]:
    """Generate typical questions based on content analysis"""
    questions = []
    
    if "账户" in content:
        questions.append("客户账户余额怎么查询？")
    if "产品" in content:
        questions.append("这个金融产品的特点是什么？")
    if "流程" in content:
        questions.append("业务办理流程是怎样的？")
    if "工程" in content:
        questions.append("这个质量问题怎么处理？")
    if "规范" in content:
        questions.append("相关规范要求是什么？")
    
    return questions if questions else ["这个问题怎么解决？", "有什么需要注意的？", "能详细说明一下吗？"]

def extract_info_from_lines(lines: List[str], keywords: List[str]) -> Optional[str]:
    """
    Extract information from text lines based on keywords
    """
    for line in lines:
        for keyword in keywords:
            if keyword in line:
                # Try to extract the content after the keyword
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()
                # Try to extract content after common separators
                for sep in ['：', '是', '为']:
                    if sep in line:
                        parts = line.split(sep, 1)
                        if len(parts) > 1:
                            return parts[1].strip()
    return None

def extract_requirements_from_content(content: str) -> List[str]:
    """
    Extract core requirements from document content
    """
    requirements = []
    
    # Look for common requirement indicators
    requirement_keywords = ['功能', '需求', '要求', '目标', '期望']
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if any(keyword in line for keyword in requirement_keywords) and len(line) > 10:
            requirements.append(line[:100])  # Limit length
            if len(requirements) >= 3:  # Limit to 3 requirements
                break
    
    if not requirements:
        requirements = ["AI系统核心功能需求", "用户交互体验优化", "准确性和可靠性保障"]
    
    return requirements

def create_basic_fallback_result(requirement_content: str) -> Dict[str, Any]:
    """
    Create a basic fallback result when extraction completely fails
    """
    return {
        "user_persona": {
            "role": "专业用户",
            "experience_level": "中等经验水平",
            "expertise_areas": ["专业技术", "行业知识"],
            "communication_style": "专业与通俗并重",
            "work_environment": "专业工作场所"
        },
        "usage_context": {
            "primary_scenarios": ["技术咨询", "问题解决", "信息查询"],
            "business_domain": "专业服务",
            "interaction_goals": ["获取准确信息", "解决实际问题", "提高工作效率"],
            "pain_points": ["信息获取困难", "回答不够专业", "响应速度慢"]
        },
        "ai_role_simulation": {
            "simulated_user_type": "具有一定专业背景的实际用户",
            "conversation_approach": "结合实际工作场景的自然提问",
            "language_characteristics": "专业术语与日常语言结合",
            "typical_questions": ["这个问题怎么解决？", "有什么需要注意的地方？", "能详细说明一下吗？"]
        },
        "extracted_requirements": {
            "core_functions": ["核心功能实现", "用户体验优化", "专业准确性保障"],
            "quality_expectations": ["高准确性", "良好响应速度", "专业可靠"],
            "interaction_preferences": ["清晰易懂", "逻辑清楚", "实用可行"]
        }
    }

async def generate_conversation_scenarios_from_persona(user_persona_info: Dict) -> List[Dict]:
    """
    Generate realistic conversation scenarios based on extracted user persona using DeepSeek
    """
    try:
        persona = user_persona_info.get('user_persona', {})
        usage_context = user_persona_info.get('usage_context', {})
        ai_role = user_persona_info.get('ai_role_simulation', {})
        
        generation_prompt = f"""
基于以下用户画像信息，请生成3个逼真的对话测试场景。每个场景应该：
1. 体现该用户角色的实际工作需求
2. 包含该用户的沟通风格和语言习惯
3. 设计3-4轮渐进式对话，从模糊到具体

用户画像信息：
- 角色：{persona.get('role', '')}
- 经验水平：{persona.get('experience_level', '')}
- 工作环境：{persona.get('work_environment', '')}
- 沟通风格：{persona.get('communication_style', '')}
- 业务领域：{usage_context.get('business_domain', '')}
- 主要场景：{', '.join(usage_context.get('primary_scenarios', []))}
- 典型问题：{', '.join(ai_role.get('typical_questions', []))}

请严格按照以下JSON格式返回（不要添加任何其他文字）：

[
  {{
    "title": "场景1标题",
    "context": "业务上下文描述",
    "user_profile": "用户画像简述",
    "turns": [
      "第1轮：模糊或简短的问题",
      "第2轮：补充信息或澄清",
      "第3轮：进一步细节",
      "第4轮：具体需求（可选）"
    ]
  }},
  {{
    "title": "场景2标题",
    "context": "业务上下文描述",
    "user_profile": "用户画像简述",
    "turns": [
      "第1轮：模糊或简短的问题",
      "第2轮：补充信息或澄清",
      "第3轮：进一步细节"
    ]
  }},
  {{
    "title": "场景3标题",
    "context": "业务上下文描述",
    "user_profile": "用户画像简述",
    "turns": [
      "第1轮：模糊或简短的问题",
      "第2轮：补充信息或澄清",
      "第3轮：进一步细节"
    ]
  }}
]

重要：只返回JSON数组，不要有任何解释或其他文字。"""

        print("🎯 Generating conversation scenarios based on persona...")
        response = await call_deepseek_api(generation_prompt)
        
        # Clean and parse the response
        cleaned_response = response.strip()
        
        # Remove markdown code blocks if present
        if cleaned_response.startswith('```'):
            lines = cleaned_response.split('\n')
            cleaned_response = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned_response
        
        # Extract JSON array
        start_idx = cleaned_response.find('[')
        end_idx = cleaned_response.rfind(']')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = cleaned_response[start_idx:end_idx+1]
            
            try:
                scenarios = json.loads(json_str)
                if isinstance(scenarios, list) and len(scenarios) > 0:
                    print(f"✅ Generated {len(scenarios)} conversation scenarios")
                    return scenarios
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed: {e}, using fallback generation...")
        
        # Fallback: generate scenarios based on persona information
        return generate_fallback_scenarios_from_persona(user_persona_info)
        
    except Exception as e:
        print(f"❌ Scenario generation error: {e}")
        # Return basic fallback scenarios
        return generate_fallback_scenarios_from_persona(user_persona_info)

def generate_fallback_scenarios_from_persona(user_persona_info: Dict) -> List[Dict]:
    """
    Generate fallback scenarios when DeepSeek API fails
    """
    persona = user_persona_info.get('user_persona', {})
    usage_context = user_persona_info.get('usage_context', {})
    
    role = persona.get('role', '专业用户')
    business_domain = usage_context.get('business_domain', '专业服务')
    primary_scenarios = usage_context.get('primary_scenarios', [])
    
    # Generate scenarios based on role and domain
    if '客服' in role:
        return [
            {
                "title": "客户账户查询",
                "context": f"{business_domain}客服场景",
                "user_profile": f"{role}，{persona.get('experience_level', '有经验')}",
                "turns": [
                    "客户问账户余额",
                    "需要验证身份信息",
                    "具体是哪个账户"
                ]
            },
            {
                "title": "产品咨询",
                "context": f"{business_domain}产品咨询",
                "user_profile": f"{role}，{persona.get('communication_style', '专业沟通')}",
                "turns": [
                    "客户想了解新产品",
                    "询问具体功能",
                    "咨询费用和条件"
                ]
            },
            {
                "title": "业务办理",
                "context": f"{business_domain}业务处理",
                "user_profile": f"{role}，{persona.get('work_environment', '客服环境')}",
                "turns": [
                    "客户要办理业务",
                    "确认具体业务类型",
                    "询问所需材料"
                ]
            }
        ]
    elif '工程师' in role or '监理' in role:
        return [
            {
                "title": "现场质量问题",
                "context": f"{persona.get('work_environment', '工程现场')}",
                "user_profile": f"{role}，{persona.get('experience_level', '有经验')}",
                "turns": [
                    "发现质量问题",
                    "描述具体位置",
                    "询问处理方法"
                ]
            },
            {
                "title": "规范标准查询",
                "context": f"{business_domain}技术支持",
                "user_profile": f"{role}，{persona.get('communication_style', '专业术语')}",
                "turns": [
                    "需要查询相关规范",
                    "明确具体标准条文",
                    "确认适用条件"
                ]
            },
            {
                "title": "工艺流程咨询",
                "context": f"{business_domain}现场作业",
                "user_profile": f"{role}，{persona.get('work_environment', '施工现场')}",
                "turns": [
                    "咨询施工工艺",
                    "询问具体步骤",
                    "确认质量要求"
                ]
            }
        ]
    else:
        # Generic scenarios
        scenarios_list = []
        for i, scenario in enumerate(primary_scenarios[:3], 1):
            scenarios_list.append({
                "title": f"{scenario}咨询",
                "context": f"{business_domain}",
                "user_profile": f"{role}，{persona.get('experience_level', '中等经验')}",
                "turns": [
                    f"关于{scenario}的问题",
                    "需要更详细的信息",
                    "确认具体操作方法"
                ]
            })
        
        if not scenarios_list:
            scenarios_list = [
                {
                    "title": "专业咨询",
                    "context": business_domain,
                    "user_profile": f"{role}，专业工作场景",
                    "turns": [
                        "有个问题需要咨询",
                        "具体情况是这样的",
                        "应该怎么处理"
                    ]
                }
            ]
        
        return scenarios_list

# Remove the old fallback scenario functions and replace with simple scenario generation
async def generate_dynamic_conversation_scenarios(user_persona_info: Dict) -> List[Dict]:
    """
    Generate 2 realistic conversation scenarios with strict timeout - no fallbacks
    """
    try:
        persona = user_persona_info.get('user_persona', {})
        usage_context = user_persona_info.get('usage_context', {})
        
        # Generate scenario topics based on persona
        topic_generation_prompt = f"""
基于用户画像，生成2个真实的对话场景主题。请严格按照JSON格式返回：

用户角色：{persona.get('role', '')}
工作环境：{persona.get('work_environment', '')}
业务领域：{usage_context.get('business_domain', '')}
主要场景：{', '.join(usage_context.get('primary_scenarios', []))}

JSON格式：
[
  {{
    "title": "场景1标题",
    "context": "业务上下文",
    "scenario_type": "具体场景类型"
  }},
  {{
    "title": "场景2标题", 
    "context": "业务上下文",
    "scenario_type": "具体场景类型"
  }}
]

只返回JSON，不要其他文字。"""

        print("🎯 Generating scenario topics based on persona...")
        response = await call_deepseek_with_strict_timeout(topic_generation_prompt)
        
        # Parse scenario topics
        if response:
            cleaned_response = response.strip()
            if cleaned_response.startswith('```'):
                lines = cleaned_response.split('\n')
                cleaned_response = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned_response
            
            start_idx = cleaned_response.find('[')
            end_idx = cleaned_response.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_str = cleaned_response[start_idx:end_idx+1]
                parsed_scenarios = json.loads(json_str)
                if isinstance(parsed_scenarios, list) and len(parsed_scenarios) >= 2:
                    scenarios = parsed_scenarios[:2]  # Take first 2 scenarios
                    print(f"✅ Generated {len(scenarios)} scenarios from DeepSeek")
                    return scenarios
        
        # Simple hardcoded scenarios if API fails - no complex fallbacks
        role = persona.get('role', '用户')
        business_domain = usage_context.get('business_domain', '专业服务')
        
        if '工程师' in role or '监理' in role:
            return [
                {"title": "钢筋隐蔽工程验收", "context": f"{business_domain}现场验收", "scenario_type": "技术咨询"},
                {"title": "混凝土浇筑旁站监督", "context": f"{business_domain}现场监督", "scenario_type": "规范查询"}
            ]
        elif '客服' in role:
            return [
                {"title": "客户账户查询", "context": f"{business_domain}客服场景", "scenario_type": "业务咨询"},
                {"title": "产品功能咨询", "context": f"{business_domain}产品支持", "scenario_type": "产品咨询"}
            ]
        else:
            return [
                {"title": "专业技术咨询", "context": business_domain, "scenario_type": "技术支持"},
                {"title": "操作指导问题", "context": f"{business_domain}操作场景", "scenario_type": "操作指导"}
            ]
        
    except Exception as e:
        print(f"❌ Scenario generation failed: {str(e)}")
        raise Exception(f"场景生成失败: {str(e)}")

# Update the main conversation function to use new approach
async def conduct_dynamic_multi_scenario_evaluation(
    api_config: APIConfig, 
    user_persona_info: Dict, 
    requirement_context: str = ""
) -> List[Dict]:
    """
    Conduct dynamic multi-scenario evaluation with strict timeouts and no fallbacks
    """
    print("🚀 开始动态多场景对话评估...")
    
    # Generate 2 scenarios with strict timeout
    scenarios = await generate_dynamic_conversation_scenarios(user_persona_info)
    
    evaluation_results = []
    
    # Dimension names mapping for display
    dimension_names = {
        "fuzzy_understanding": "模糊理解",
        "answer_correctness": "回答准确性", 
        "persona_alignment": "用户匹配",
        "goal_alignment": "目标对齐"
    }
    
    # Process scenarios sequentially for better error handling
    for i, scenario_info in enumerate(scenarios, 1):
        try:
            print(f"📋 场景 {i}/2: {scenario_info.get('title', '未命名场景')}")
            
            # Conduct true dynamic conversation for this scenario
            conversation_history = await conduct_true_dynamic_conversation(
                api_config, scenario_info, user_persona_info
            )
            
            if conversation_history:
                # Evaluate conversation with enhanced detailed explanations
                try:
                    evaluation_scores, detailed_explanations, scenario_score = await evaluate_conversation_with_deepseek(
                        conversation_history, scenario_info, requirement_context, user_persona_info
                    )
                except Exception as e:
                    print(f"❌ 场景 {i} 评估失败: {str(e)}")
                    continue

                result = {
                    "scenario_title": scenario_info.get('title', f'场景 {i}'),
                    "scenario_context": scenario_info.get('context', '专业工作环境'),
                    "scenario_persona": f"{user_persona_info.get('user_persona', {}).get('role', '专业用户')} | {user_persona_info.get('usage_context', {}).get('business_domain', '专业服务')}",
                    "conversation_history": conversation_history,
                    "evaluation_scores": evaluation_scores,
                    "detailed_explanations": detailed_explanations,  # Add detailed explanations
                    "scenario_score": scenario_score,
                    "total_turns": len(conversation_history),
                    "persona_context_display": {
                        "user_role": user_persona_info.get('user_persona', {}).get('role', '专业用户'),
                        "business_domain": user_persona_info.get('usage_context', {}).get('business_domain', '专业服务'),
                        "experience_level": user_persona_info.get('user_persona', {}).get('experience_level', '中等经验'),
                        "communication_style": user_persona_info.get('user_persona', {}).get('communication_style', '专业沟通')
                    },
                    # Frontend display format
                    "scenario": {
                        "title": scenario_info.get('title', f'场景 {i}'),
                        "context": f"{user_persona_info.get('usage_context', {}).get('business_domain', '专业服务')} - {scenario_info.get('context', '专业工作环境')}",
                        "user_profile": f"{user_persona_info.get('user_persona', {}).get('role', '用户')}，{user_persona_info.get('user_persona', {}).get('experience_level', '中等经验')}，{user_persona_info.get('user_persona', {}).get('communication_style', '专业沟通')}"
                    },
                    "evaluation_scores_with_explanations": {
                        dimension: {
                            "score": score,
                            "explanation": detailed_explanations.get(dimension, {}).get("detailed_analysis", "未提供详细分析"),
                            "formatted_score": f"{dimension_names.get(dimension, dimension)}: {score}/5"
                        }
                        for dimension, score in evaluation_scores.items()
                    }
                }
                
                evaluation_results.append(result)
                print(f"🎯 场景 {i} 得分: {scenario_score:.2f}/5.0")
            else:
                print(f"❌ 场景 {i} 对话失败")
                
        except Exception as e:
            print(f"❌ 场景 {i} 评估失败: {str(e)}")
            continue
    
    if not evaluation_results:
        raise Exception("所有场景评估均失败，请检查AI Agent配置和网络连接")
    
    return evaluation_results

async def evaluate_conversation_with_deepseek(
    conversation_history: List[Dict], 
    scenario_info: Dict, 
    requirement_context: str,
    user_persona_info: Dict
) -> tuple:
    """
    Enhanced DeepSeek evaluation with detailed explanations for each rating criteria
    """
    try:
        print("🧠 开始DeepSeek智能评估 (基于提取的用户画像)...")
        
        persona = user_persona_info.get('user_persona', {})
        context = user_persona_info.get('usage_context', {})
        requirements = user_persona_info.get('extracted_requirements', {})
        
        # Build comprehensive context for detailed evaluation
        context_section = f"""
=== 用户画像基准 ===
用户角色: {persona.get('role', '专业用户')}
经验水平: {persona.get('experience_level', '中等经验')}
工作环境: {persona.get('work_environment', '专业环境')}
业务领域: {context.get('business_domain', '专业服务')}
沟通风格: {persona.get('communication_style', '专业沟通')}
专业领域: {', '.join(persona.get('expertise_areas', []))}

=== 场景背景 ===
场景标题: {scenario_info.get('title', '未知场景')}
场景描述: {scenario_info.get('context', '专业对话场景')}

=== 完整对话记录 ===
"""
        
        # Add conversation history to context
        for i, turn in enumerate(conversation_history, 1):
            context_section += f"第{i}轮 - {turn.get('role', '用户')}: {turn.get('content', '')[:100]}...\n"
            
        # Enhanced evaluation prompts with detailed analysis requirements
        evaluation_prompts = {
            "fuzzy_understanding": f"""
{context_section}

请详细分析上述完整对话中AI的模糊理解与追问能力，并给出1-5分评分。

评分标准：
5分：完全理解模糊问题，主动追问关键细节，引导用户提供必要信息
4分：基本理解模糊问题，有一定追问能力
3分：能处理部分模糊问题，追问不够深入
2分：对模糊问题理解有限，很少主动追问
1分：无法处理模糊问题，缺乏追问能力

请按以下格式回答：
评分：X/5
详细分析：
1. 模糊理解表现：[分析AI如何理解用户的模糊或不完整问题]
2. 追问质量：[分析AI的追问是否恰当、深入]
3. 信息获取：[分析AI是否成功获取了解决问题所需的关键信息]
4. 改进建议：[针对该用户画像的具体改进建议]
""",
            
            "answer_correctness": f"""
{context_section}

请详细分析上述完整对话中AI回答的准确性与专业性，并给出1-5分评分。

评分标准：
5分：回答完全准确，专业性强，符合行业标准
4分：回答基本准确，有一定专业性
3分：回答部分准确，专业性一般
2分：回答准确性有限，专业性不足
1分：回答不准确，缺乏专业性

请按以下格式回答：
评分：X/5
详细分析：
1. 准确性评估：[分析AI回答的事实准确性]
2. 专业性评估：[分析AI回答是否符合{persona.get('role', '专业用户')}的专业要求]
3. 完整性评估：[分析AI回答是否完整解决了用户问题]
4. 改进建议：[针对该用户画像的具体改进建议]
""",
            
            "persona_alignment": f"""
{context_section}

请详细分析上述完整对话中AI与用户画像的匹配度，并给出1-5分评分。

评分标准：
5分：完全匹配用户画像，沟通风格和专业度高度契合
4分：基本匹配用户画像，沟通较为恰当
3分：部分匹配用户画像，沟通风格一般
2分：匹配度有限，沟通风格不够恰当
1分：不匹配用户画像，沟通风格不合适

请按以下格式回答：
评分：X/5
详细分析：
1. 角色匹配：[分析AI是否理解用户的{persona.get('role', '专业用户')}身份]
2. 沟通风格：[分析AI的沟通方式是否符合用户的{persona.get('communication_style', '专业沟通')}偏好]
3. 专业契合：[分析AI的回答是否符合{context.get('business_domain', '专业服务')}领域要求]
4. 改进建议：[针对该用户画像的具体改进建议]
""",
            
            "goal_alignment": f"""
{context_section}

请详细分析上述完整对话中AI与用户目标的对齐度，并给出1-5分评分。

评分标准：
5分：完全理解并满足用户目标，主动提供相关帮助
4分：基本理解用户目标，提供有效帮助
3分：部分理解用户目标，帮助有限
2分：对用户目标理解不足，帮助不够
1分：不理解用户目标，无法提供有效帮助

请按以下格式回答：
评分：X/5
详细分析：
1. 目标理解：[分析AI是否准确理解了用户的真实需求和目标]
2. 解决效果：[分析AI的回答是否有效解决了用户问题]
3. 主动性：[分析AI是否主动提供了相关的额外帮助]
4. 改进建议：[针对该用户画像的具体改进建议]
"""
        }
        
        evaluation_results = {}
        detailed_explanations = {}
        
        # Evaluate each dimension with detailed analysis
        for dimension, prompt in evaluation_prompts.items():
            try:
                print(f"  📊 评估 {dimension} (场景: {scenario_info.get('title', '未知')[:20]}...)...")
                response = await call_deepseek_with_strict_timeout(prompt)
                
                # Extract score and detailed explanation
                score = extract_score_from_response(response)
                detailed_explanation = extract_detailed_explanation(response)
                
                evaluation_results[dimension] = score
                detailed_explanations[dimension] = detailed_explanation
                
                print(f"  ✅ {dimension}: {score}/5 (匹配{persona.get('role', '用户')}需求)")
                
            except Exception as e:
                print(f"  ❌ Failed to evaluate {dimension}: {str(e)}")
                raise Exception(f"评估维度 {dimension} 失败: {str(e)}")
        
        # Calculate overall score
        scenario_score = sum(evaluation_results.values()) / len(evaluation_results)
        print(f"🎯 场景整体得分: {scenario_score:.2f}/5.0")
        
        return evaluation_results, detailed_explanations, scenario_score
        
    except Exception as e:
        print(f"❌ 评估失败: {str(e)}")
        raise Exception(f"DeepSeek评估失败: {str(e)}")

def extract_detailed_explanation(response: str) -> Dict[str, str]:
    """
    Extract detailed explanation from DeepSeek response
    """
    try:
        explanation = {
            "score": "未知",
            "detailed_analysis": "未提供详细分析",
            "specific_points": []
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('评分：'):
                explanation["score"] = line.replace('评分：', '').strip()
            elif line.startswith('详细分析：'):
                current_section = "analysis"
            elif line and current_section == "analysis":
                if any(line.startswith(f"{i}.") for i in range(1, 10)):
                    explanation["specific_points"].append(line)
                elif line.startswith(('1.', '2.', '3.', '4.')):
                    explanation["specific_points"].append(line)
        
        # Combine all specific points into detailed analysis
        if explanation["specific_points"]:
            explanation["detailed_analysis"] = "\n".join(explanation["specific_points"])
        
        return explanation
        
    except Exception as e:
        print(f"Warning: Could not parse detailed explanation: {str(e)}")
        return {
            "score": "未知",
            "detailed_analysis": response[:500] + "..." if len(response) > 500 else response,
            "specific_points": []
        }

async def generate_single_initial_message(scenario_info: Dict, user_persona_info: Dict) -> str:
    """Generate ONLY the opening message - no full conversation"""
    persona = user_persona_info.get('user_persona', {})
    context = user_persona_info.get('usage_context', {})
    
    prompt = f"""
作为{persona.get('role', '用户')}，生成一个自然的开场问题。

用户身份: {persona.get('role', '用户')}
工作经验: {persona.get('experience_level', '中等经验')}
工作环境: {persona.get('work_environment', '工作场所')}
沟通风格: {persona.get('communication_style', '专业')}
业务领域: {context.get('business_domain', '专业服务')}

对话场景: {scenario_info.get('title', '专业咨询')}
场景背景: {scenario_info.get('context', '工作场景')}

请生成一个符合{persona.get('role', '用户')}身份的开场问题或描述，体现{scenario_info.get('title', '场景')}的特点。

要求:
- 像真实的{persona.get('role', '用户')}提问
- 体现{persona.get('experience_level', '经验水平')}
- 符合{scenario_info.get('title', '场景')}背景
- 只返回一句话，不要解释

示例格式: "现场发现...", "需要确认...", "关于...规范要求"
"""

    try:
        response = await call_deepseek_with_strict_timeout(prompt)
        if response and len(response.strip()) > 5:
            return response.strip().strip('"').strip("'")
    except Exception as e:
        print(f"⚠️ DeepSeek生成初始消息失败: {str(e)}")
    
    # Simple fallback based on scenario
    role = persona.get('role', '用户')
    if '工程师' in role or '监理' in role:
        return f"现场{scenario_info.get('title', '施工')}有技术问题需要确认"
    else:
        return f"关于{scenario_info.get('title', '业务')}有问题咨询"

async def generate_next_message_based_on_response(
    scenario_info: Dict, 
    user_persona_info: Dict, 
    conversation_history: List[Dict], 
    coze_response: str
) -> str:
    """Generate next message based ONLY on Coze's actual response"""
    persona = user_persona_info.get('user_persona', {})
    
    # Analyze Coze's response characteristics
    response_analysis = analyze_coze_response(coze_response)
    
    prompt = f"""
作为{persona.get('role', '用户')}，基于AI的回复，生成自然的后续消息。

你的身份: {persona.get('role', '用户')}
沟通风格: {persona.get('communication_style', '专业')}
经验水平: {persona.get('experience_level', '中等')}

AI刚才的回复:
{coze_response[:400]}

回复特征分析:
- 是否提供了具体信息: {response_analysis['has_specific_info']}
- 是否包含规范引用: {response_analysis['has_standards']}
- 回复完整度: {response_analysis['completeness']}

请生成符合{persona.get('role', '用户')}身份的后续消息:
1. 如果AI回答完整且解决问题 → 表达感谢并结束("谢谢，问题解决了")
2. 如果AI回答模糊 → 追问具体细节
3. 如果AI提供链接但需要具体内容 → 询问关键条文
4. 如果AI回答部分正确 → 补充追问相关问题

只返回后续消息内容，如需结束对话返回"END"。
"""

    try:
        response = await call_deepseek_with_strict_timeout(prompt)
        if response:
            message = response.strip().strip('"').strip("'")
            if message.upper() in ["END", "FINISH", "DONE"]:
                return ""
            return message if len(message) > 3 else ""
    except Exception:
        pass
    
    # Smart fallback based on turn number and AI response quality
    turn_num = len(conversation_history)
    
    if turn_num >= 4:  # Natural ending after several turns
        return ""
    
    # Generate contextual response based on role and AI response content
    role = persona.get('role', '用户')
    ai_response_lower = coze_response.lower()
    
    if '规范' in ai_response_lower and ('工程师' in role or '监理' in role):
        return "具体条文号是什么？现场操作要注意哪些要点？"
    elif '标准' in ai_response_lower or '要求' in ai_response_lower:
        return "这个标准的具体执行细节是什么？"
    elif '可以' in ai_response_lower or '建议' in ai_response_lower:
        return "好的，还有其他需要注意的吗？"
    elif len(coze_response) < 100:  # Short response, need more details
        return "能详细说明一下具体操作步骤吗？"
    else:
        return "明白了，谢谢"

def analyze_coze_response(response: str) -> Dict[str, bool]:
    """Analyze Coze response characteristics"""
    return {
        'has_specific_info': len(response) > 100 and ('条' in response or '第' in response or 'GB' in response),
        'has_standards': '规范' in response or '标准' in response or 'GB' in response,
        'completeness': len(response) > 150
    }

async def call_coze_with_strict_timeout(api_config: APIConfig, message: str) -> str:
    """Call Coze API with strict 2-minute timeout and no excessive retries"""
    timeout_seconds = 120  # 2 minutes total
    max_retries = 2  # Only 2 attempts max
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Coze调用 (尝试 {attempt + 1}/{max_retries})")
            
            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds)) as client:
                if api_config.type == 'coze-agent':
                    return await call_coze_agent_with_timeout(api_config, message, client)
                elif api_config.type == 'coze-bot' or hasattr(api_config, 'botId'):
                    return await call_coze_bot_with_timeout(api_config, message, client)
                else:
                    return await call_generic_api_with_timeout(api_config, message, client)
                    
        except asyncio.TimeoutError:
            print(f"⏰ 第{attempt + 1}次调用超时 (2分钟)")
            if attempt < max_retries - 1:
                continue
            else:
                raise Exception("Coze API调用超时，请检查网络或Agent配置")
        except Exception as e:
            print(f"❌ 第{attempt + 1}次调用失败: {str(e)}")
            if attempt < max_retries - 1:
                continue
            else:
                raise Exception(f"Coze API调用失败: {str(e)}")
    
    raise Exception("Coze API调用完全失败")

async def call_deepseek_with_strict_timeout(prompt: str) -> str:
    """Call DeepSeek API with strict timeout and no retries"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 300
    }
    
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0].get("message", {}).get("content", "").strip()
                    if content and len(content) > 5:
                        return content
            
            raise Exception(f"DeepSeek API错误: {response.status_code}")
            
    except Exception as e:
        raise Exception(f"DeepSeek API调用失败: {str(e)}")

async def call_coze_agent_with_timeout(api_config: APIConfig, message: str, client: httpx.AsyncClient) -> str:
    """Call Coze Agent API with timeout - no excessive polling"""
    base_url = "https://api.coze.cn" if api_config.region == "china" else "https://api.coze.com"
    chat_url = f"{base_url}/v3/chat"
    
    headers = {
        "Authorization": f"Bearer {api_config.headers.get('Authorization', '').replace('Bearer ', '')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "bot_id": api_config.agentId,
        "user_id": f"user_{datetime.now().strftime('%H%M%S')}",
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [{"role": "user", "content": message, "content_type": "text"}]
    }
    
    # Start conversation
    response = await client.post(chat_url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Agent API错误: {response.status_code}")
    
    result = response.json()
    if result.get("code") != 0:
        raise Exception(f"Agent响应错误: {result.get('msg', 'Unknown error')}")
    
    data = result.get("data", {})
    conversation_id = data.get("conversation_id")
    chat_id = data.get("id")
    status = data.get("status")
    
    if status == "completed":
        # Get messages immediately
        return await get_agent_messages(client, base_url, headers, conversation_id, chat_id)
    elif status == "in_progress":
        # Limited polling - max 20 attempts with 3-second intervals (1 minute total)
        messages_url = f"{base_url}/v1/conversation/message/list"
        for poll in range(20):
            await asyncio.sleep(3)
            
            params = {"conversation_id": conversation_id, "chat_id": chat_id}
            messages_response = await client.get(messages_url, headers=headers, params=params)
            
            if messages_response.status_code == 200:
                messages_result = messages_response.json()
                if messages_result.get("code") == 0:
                    messages = messages_result.get("data", [])
                    for msg in messages:
                        if msg.get("role") == "assistant" and msg.get("content"):
                            return msg.get("content", "").strip()
        
        raise Exception("Agent处理超时 (1分钟)")
    else:
        raise Exception(f"Agent状态异常: {status}")

async def get_agent_messages(client: httpx.AsyncClient, base_url: str, headers: Dict, conversation_id: str, chat_id: str) -> str:
    """Get agent messages with single call"""
    messages_url = f"{base_url}/v1/conversation/message/list"
    params = {"conversation_id": conversation_id, "chat_id": chat_id}
    
    response = await client.get(messages_url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"获取消息失败: {response.status_code}")
    
    result = response.json()
    if result.get("code") != 0:
        raise Exception(f"消息API错误: {result.get('msg')}")
    
    messages = result.get("data", [])
    for msg in messages:
        if msg.get("role") == "assistant" and msg.get("content"):
            return msg.get("content", "").strip()
    
    raise Exception("未找到Assistant回复")

async def call_coze_bot_with_timeout(api_config: APIConfig, message: str, client: httpx.AsyncClient) -> str:
    """Call Coze Bot API with timeout"""
    url = "https://api.coze.cn/open_api/v2/chat"
    headers = {
        "Authorization": "Bearer pat_aWWxLQe20D8km5FsKt5W99pWL72L5LNxjkontH91q3lqqTU0ExBKUBl1cUy4tm8c",
        "Content-Type": "application/json"
    }
    
    payload = {
        "conversation_id": f"conv_{datetime.now().strftime('%H%M%S')}",
        "bot_id": getattr(api_config, 'botId', '7511993619423985674'),
        "user": "test_user",
        "query": message,
        "stream": False
    }
    
    response = await client.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Bot API错误: {response.status_code}")
    
    result = response.json()
    messages = result.get("messages", [])
    
    for msg in messages:
        if msg.get("type") == "answer" and msg.get("content"):
            return msg.get("content", "").strip()
    
    raise Exception("Bot未返回有效回复")

async def call_generic_api_with_timeout(api_config: APIConfig, message: str, client: httpx.AsyncClient) -> str:
    """Call generic API with timeout"""
    headers = api_config.headers.copy()
    headers.setdefault("Content-Type", "application/json")
    
    payload = {"message": message, "query": message}
    
    response = await client.request(
        method=api_config.method,
        url=api_config.url,
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"API错误: {response.status_code}")
    
    result = response.json()
    return result.get("response", result.get("answer", result.get("message", str(result))))

async def generate_final_comprehensive_report(
    evaluation_results: List[Dict], 
    user_persona_info: Dict, 
    requirement_context: str
) -> Dict:
    """
    Generate comprehensive final report for dynamic evaluation with extracted persona/context display
    """
    if not evaluation_results:
        return {
            "overall_analysis": "评估失败：无有效对话数据",
            "extracted_persona_summary": user_persona_info,
            "cross_scenario_insights": [],
            "persona_alignment_analysis": "无法分析",
            "improvement_recommendations": ["请检查AI Agent配置和网络连接"],
            "detailed_metrics": {}
        }
    
    # Extract persona information for prominent display
    persona = user_persona_info.get('user_persona', {})
    context = user_persona_info.get('usage_context', {})
    requirements = user_persona_info.get('extracted_requirements', {})
    
    # Calculate comprehensive metrics
    all_scores = []
    total_turns = 0
    scenario_summaries = []
    dimension_averages = {}
    
    for result in evaluation_results:
        scores = result.get('evaluation_scores', {})
        if scores:
            all_scores.extend(scores.values())
            # Calculate dimension averages
            for dimension, score in scores.items():
                if dimension not in dimension_averages:
                    dimension_averages[dimension] = []
                dimension_averages[dimension].append(score)
        
        total_turns += result.get('total_turns', 0)
        
        scenario_summaries.append({
            "title": result.get('scenario_title', '未命名场景'),
            "score": result.get('scenario_score', 0),
            "turns": result.get('total_turns', 0),
            "key_strengths": extract_strengths_from_scores(scores),
            "improvement_areas": extract_weaknesses_from_scores(scores),
            "detailed_evaluations": result.get('evaluation_explanations', {})
        })
    
    # Calculate final dimension averages
    final_dimension_averages = {}
    for dimension, scores in dimension_averages.items():
        final_dimension_averages[dimension] = sum(scores) / len(scores) if scores else 0
    
    overall_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    # Generate enhanced analysis prompt with extracted persona emphasis
    analysis_prompt = f"""
基于以下动态对话评估结果和提取的用户画像，生成综合分析报告：

=== 从需求文档提取的用户画像信息 ===
用户角色: {persona.get('role', '未指定')}
经验水平: {persona.get('experience_level', '未指定')}
专业领域: {', '.join(persona.get('expertise_areas', ['未指定']))}
沟通风格: {persona.get('communication_style', '未指定')}
工作环境: {persona.get('work_environment', '未指定')}

业务上下文: {context.get('business_domain', '未指定')}
主要使用场景: {', '.join(context.get('primary_scenarios', ['未指定']))}
交互目标: {', '.join(context.get('interaction_goals', ['未指定']))}
关键痛点: {', '.join(context.get('pain_points', ['未指定']))}

核心功能需求: {', '.join(requirements.get('core_functions', ['未指定']))}
质量期望: {', '.join(requirements.get('quality_expectations', ['未指定']))}

=== 评估结果数据 ===
总体得分: {overall_score:.2f}/5.0
评估场景数: {len(evaluation_results)}
总对话轮次: {total_turns}

维度得分:
- 模糊理解能力: {final_dimension_averages.get('fuzzy_understanding', 0):.2f}/5.0
- 回答准确性: {final_dimension_averages.get('answer_correctness', 0):.2f}/5.0
- 用户匹配度: {final_dimension_averages.get('persona_alignment', 0):.2f}/5.0
- 目标对齐度: {final_dimension_averages.get('goal_alignment', 0):.2f}/5.0

场景详情:
{chr(10).join([f"场景{i+1}: {s['title']} - 得分{s['score']:.1f}/5.0 ({s['turns']}轮对话)" for i, s in enumerate(scenario_summaries)])}

请生成包含以下内容的综合分析：
1. 整体表现评价：基于提取的{persona.get('role', '用户角色')}需求，AI的整体表现如何？（150字内）
2. 用户画像匹配度分析：AI是否很好地适应了提取的用户角色和沟通风格？（100字内）
3. 业务目标达成度：是否满足了从需求文档中提取的业务目标和功能需求？（100字内）
4. 跨场景对比洞察：不同场景下的表现差异和规律（3-5个要点）
5. 针对性改进建议：基于提取的用户画像和业务需求的具体改进建议（5-8条）

请用专业但易懂的语言，重点突出与提取的用户画像和需求的匹配情况。
"""

    try:
        comprehensive_analysis = await call_deepseek_api_with_fallback(analysis_prompt)
        
        if comprehensive_analysis and comprehensive_analysis != "API评估暂时不可用，使用备用评分机制":
            # Parse the analysis response
            analysis_sections = parse_enhanced_comprehensive_analysis(comprehensive_analysis)
        else:
            # Fallback analysis with persona emphasis
            analysis_sections = generate_enhanced_fallback_analysis(overall_score, scenario_summaries, user_persona_info)
            
    except Exception as e:
        print(f"⚠️ 综合分析生成失败，使用备用分析: {str(e)[:50]}...")
        analysis_sections = generate_enhanced_fallback_analysis(overall_score, scenario_summaries, user_persona_info)
    
    # Generate persona-specific recommendations
    recommendations = generate_persona_specific_recommendations(evaluation_results, user_persona_info, final_dimension_averages)
    
    return {
        "overall_analysis": analysis_sections.get("overall_evaluation", "整体表现需要进一步分析"),
        "extracted_persona_summary": {
            "user_persona": persona,
            "usage_context": context,
            "extracted_requirements": requirements,
            "ai_role_simulation": user_persona_info.get('ai_role_simulation', {}),
            "extraction_source": "DeepSeek智能提取"
        },
        "persona_alignment_analysis": analysis_sections.get("persona_alignment", "用户画像匹配度有待评估"),
        "business_goal_achievement": analysis_sections.get("business_goals", "业务目标达成度需要分析"),
        "cross_scenario_insights": analysis_sections.get("cross_scenario_insights", []),
        "improvement_recommendations": recommendations,
        "detailed_metrics": {
            "overall_score": overall_score,
            "dimension_scores": final_dimension_averages,
            "total_scenarios": len(evaluation_results),
            "total_conversation_turns": total_turns,
            "average_turns_per_scenario": total_turns / len(evaluation_results) if evaluation_results else 0,
            "scenario_summaries": scenario_summaries
        },
        "evaluation_timestamp": datetime.now().isoformat(),
        "evaluation_mode": "dynamic_conversation_with_extracted_persona"
    }

def extract_strengths_from_scores(scores: Dict) -> List[str]:
    """Extract strengths based on evaluation scores"""
    strengths = []
    for dimension, score in scores.items():
        if score >= 4.0:
            if dimension == "fuzzy_understanding":
                strengths.append("模糊理解能力强")
            elif dimension == "answer_correctness":
                strengths.append("回答准确专业")
            elif dimension == "persona_alignment":
                strengths.append("用户匹配度高")
            elif dimension == "goal_alignment":
                strengths.append("目标对齐良好")
    return strengths

def extract_weaknesses_from_scores(scores: Dict) -> List[str]:
    """Extract improvement areas based on evaluation scores"""
    weaknesses = []
    for dimension, score in scores.items():
        if score < 3.5:
            if dimension == "fuzzy_understanding":
                weaknesses.append("需加强追问引导")
            elif dimension == "answer_correctness":
                weaknesses.append("专业准确性待提升")
            elif dimension == "persona_alignment":
                weaknesses.append("用户适配度需改善")
            elif dimension == "goal_alignment":
                weaknesses.append("目标对齐需优化")
    return weaknesses

def parse_enhanced_comprehensive_analysis(analysis_text: str) -> Dict:
    """Parse comprehensive analysis response into structured sections"""
    sections = {
        "overall_evaluation": "",
        "cross_scenario_insights": [],
        "persona_analysis": "",
        "business_goals": ""
    }
    
    lines = analysis_text.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if "整体表现" in line or "总体评价" in line:
            current_section = "overall_evaluation"
        elif "跨场景" in line or "对比洞察" in line:
            current_section = "cross_scenario_insights"
        elif "用户画像" in line or "匹配度" in line:
            current_section = "persona_analysis"
        elif "业务目标" in line or "业务达成" in line:
            current_section = "business_goals"
        elif current_section == "overall_evaluation" and not sections["overall_evaluation"]:
            sections["overall_evaluation"] = line
        elif current_section == "cross_scenario_insights" and line.startswith(('•', '-', '1.', '2.', '3.', '4.', '5.')):
            sections["cross_scenario_insights"].append(line.lstrip('•-123456789. '))
        elif current_section == "persona_analysis" and not sections["persona_analysis"]:
            sections["persona_analysis"] = line
        elif current_section == "business_goals" and not sections["business_goals"]:
            sections["business_goals"] = line
    
    return sections

def generate_enhanced_fallback_analysis(overall_score: float, scenario_summaries: List[Dict], user_persona_info: Dict) -> Dict:
    """Generate fallback analysis when DeepSeek API is unavailable"""
    persona = user_persona_info.get('user_persona', {})
    
    if overall_score >= 4.0:
        overall_eval = f"AI Agent整体表现优秀（{overall_score:.1f}/5.0），能够有效处理{persona.get('role', '用户')}的专业需求"
    elif overall_score >= 3.0:
        overall_eval = f"AI Agent表现良好（{overall_score:.1f}/5.0），基本满足使用需求，部分环节有改进空间"
    else:
        overall_eval = f"AI Agent表现需要改进（{overall_score:.1f}/5.0），建议重点优化对话策略和专业知识"
    
    insights = [
        f"共完成{len(scenario_summaries)}个场景的动态对话测试",
        f"平均每场景{sum(s['turns'] for s in scenario_summaries) / len(scenario_summaries):.1f}轮对话",
        "动态问题生成机制运行正常" if scenario_summaries else "对话生成需要优化"
    ]
    
    persona_analysis = f"与{persona.get('role', '用户')}角色的匹配度整体{('良好' if overall_score >= 3.5 else '有待提升')}"
    
    business_goals = f"基于提取的需求文档，业务目标达成度{('较好' if overall_score >= 3.5 else '需要改进')}"
    
    return {
        "overall_evaluation": overall_eval,
        "cross_scenario_insights": insights,
        "persona_alignment": persona_analysis,
        "business_goals": business_goals
    }

def generate_persona_specific_recommendations(evaluation_results: List[Dict], user_persona_info: Dict, dimension_averages: Dict) -> List[str]:
    """
    Generate persona-specific recommendations based on extracted user persona and evaluation results
    """
    recommendations = []
    
    if not evaluation_results:
        return [
            "无法生成推荐建议，请先完成有效的评估",
            "检查AI Agent配置和网络连接",
            "确保对话场景配置正确"
        ]
    
    persona = user_persona_info.get('user_persona', {})
    context = user_persona_info.get('usage_context', {})
    requirements = user_persona_info.get('extracted_requirements', {})
    
    # Overall performance assessment based on extracted persona
    overall_avg = sum(dimension_averages.values()) / len(dimension_averages) if dimension_averages else 0
    
    if overall_avg >= 4.5:
        recommendations.append(f"🟢 针对{persona.get('role', '用户')}的整体表现优秀！AI代理能够有效处理{context.get('business_domain', '业务')}需求")
    elif overall_avg >= 4.0:
        recommendations.append(f"🟡 对{persona.get('role', '用户')}的服务良好，基本满足{context.get('business_domain', '业务')}需求，有进一步优化空间")
    elif overall_avg >= 3.0:
        recommendations.append(f"🟠 服务{persona.get('role', '用户')}的能力中等，建议针对{context.get('business_domain', '业务领域')}特点进行改进")
    else:
        recommendations.append(f"🔴 需要显著改进对{persona.get('role', '用户')}的服务能力，特别是{context.get('business_domain', '业务')}相关功能")
    
    # Dimension-specific recommendations with persona context
    if dimension_averages.get('fuzzy_understanding', 0) < 3.5:
        pain_points = context.get('pain_points', [])
        pain_context = f"，特别是{', '.join(pain_points[:2])}" if pain_points else ""
        recommendations.append(f"💡 针对{persona.get('role', '用户')}的模糊理解能力需要加强：增加追问引导机制{pain_context}")
    
    if dimension_averages.get('answer_correctness', 0) < 3.5:
        expertise_areas = persona.get('expertise_areas', [])
        expertise_context = f"，特别是{', '.join(expertise_areas[:2])}领域" if expertise_areas else ""
        recommendations.append(f"📚 针对{persona.get('role', '用户')}的专业准确性需要提升：加强知识库建设{expertise_context}")
    
    if dimension_averages.get('persona_alignment', 0) < 3.5:
        comm_style = persona.get('communication_style', '专业沟通')
        recommendations.append(f"👥 用户匹配度有待改善：优化语言风格以适应{comm_style}，匹配{persona.get('experience_level', '用户经验水平')}")
    
    if dimension_averages.get('goal_alignment', 0) < 3.5:
        core_functions = requirements.get('core_functions', [])
        function_context = f"，重点关注{', '.join(core_functions[:2])}" if core_functions else ""
        recommendations.append(f"🎯 业务目标对齐度需要改进：确保回答能够满足{context.get('business_domain', '业务')}的实际需求{function_context}")
    
    # Add persona-specific targeted recommendations
    role = persona.get('role', '')
    work_env = persona.get('work_environment', '')
    
    if '客服' in role:
        recommendations.append(f"🎧 客服场景优化：针对{work_env}环境，提升响应效率和标准化回答")
        quality_expectations = requirements.get('quality_expectations', [])
        if quality_expectations:
            recommendations.append(f"⏱️ 服务质量提升：重点满足{', '.join(quality_expectations[:2])}等客服质量要求")
    elif '工程师' in role or '监理' in role:
        recommendations.append(f"🔧 技术专业性：加强对{work_env}环境下技术规范和标准的支持")
        if '规范' in str(context.get('primary_scenarios', [])):
            recommendations.append("📋 规范查询优化：增强对技术标准和施工规范的快速检索和解释能力")
    elif '管理' in role:
        recommendations.append("📊 管理决策支持：提供更多数据分析和决策建议功能")
    
    # Add interaction preference recommendations
    interaction_goals = context.get('interaction_goals', [])
    if interaction_goals:
        recommendations.append(f"🎯 交互目标优化：重点提升{', '.join(interaction_goals[:2])}的实现效果")
    
    # Quality expectations based recommendations  
    quality_expectations = requirements.get('quality_expectations', [])
    if quality_expectations:
        recommendations.append(f"⭐ 质量标准对齐：确保达到{', '.join(quality_expectations[:2])}等质量期望")
    
    # Limit to 6-8 most relevant recommendations
    unique_recommendations = list(dict.fromkeys(recommendations))
    return unique_recommendations[:8]

def extract_recommendations_from_response(response: str) -> List[str]:
    """Extract improvement recommendations from DeepSeek response"""
    try:
        # Look for numbered or bulleted recommendations
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(marker in line for marker in ['1.', '2.', '3.', '4.', '5.', '-', '•', '①', '②', '③']):
                # Clean the line and extract recommendation
                clean_rec = re.sub(r'^[\d\.\-\•①②③④⑤]\s*', '', line).strip()
                if clean_rec and len(clean_rec) > 10:
                    recommendations.append(clean_rec)
        
        # If no structured recommendations found, try to extract from content
        if not recommendations and response:
            # Split into sentences and look for actionable suggestions
            sentences = re.split(r'[。！？.]', response)
            for sentence in sentences:
                if any(keyword in sentence for keyword in ['建议', '应该', '需要', '可以', '改进', '提升', '优化']):
                    if len(sentence.strip()) > 15:
                        recommendations.append(sentence.strip())
        
        return recommendations[:5] if recommendations else [
            "增强对话理解能力",
            "提高回答准确性",
            "优化用户体验",
            "加强专业知识深度"
        ]
        
    except Exception:
        return [
            "增强对话理解能力",
            "提高回答准确性", 
            "优化用户体验",
            "加强专业知识深度"
        ]

@app.post("/api/validate-config")
async def validate_agent_config(agent_api_config: str = Form(...)):
    """
    Validate AI Agent configuration before evaluation
    """
    try:
        # Parse configuration
        api_config_dict = json.loads(agent_api_config)
        api_config = APIConfig(**api_config_dict)
        
        validation_results = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
        
        # Basic validation
        if not api_config.url:
            validation_results["errors"].append("API URL不能为空")
            validation_results["is_valid"] = False
        
        if not api_config.headers:
            validation_results["warnings"].append("未设置请求头，可能导致认证失败")
        
        # Coze-specific validation
        if api_config.type == "coze-agent":
            if not api_config.agentId:
                validation_results["errors"].append("Coze Agent ID不能为空")
                validation_results["is_valid"] = False
            
            auth_header = api_config.headers.get("Authorization", "")
            if not auth_header or not auth_header.startswith("Bearer "):
                validation_results["errors"].append("Coze Agent需要有效的Bearer Token")
                validation_results["is_valid"] = False
            
            if api_config.region not in ["global", "china"]:
                validation_results["warnings"].append("建议使用 'global' 或 'china' 作为region")
        
        elif api_config.type == "coze-bot":
            if not api_config.botId:
                validation_results["errors"].append("Coze Bot ID不能为空")
                validation_results["is_valid"] = False
        
        # Test connectivity (optional quick test)
        if validation_results["is_valid"]:
            try:
                # Quick connectivity test with timeout
                async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                    if api_config.type == "coze-agent":
                        # Test Coze Agent endpoint
                        test_url = f"https://api.coze.{'cn' if api_config.region == 'china' else 'com'}/v3/chat"
                        response = await client.post(
                            test_url,
                            headers=api_config.headers,
                            json={
                                "bot_id": api_config.agentId,
                                "user_id": "test_validation",
                                "stream": False,
                                "auto_save_history": False,
                                "additional_messages": [
                                    {"role": "user", "content": "test", "content_type": "text"}
                                ]
                            }
                        )
                        
                        if response.status_code == 401:
                            validation_results["errors"].append("认证失败：请检查Access Token是否有效")
                            validation_results["is_valid"] = False
                        elif response.status_code == 403:
                            validation_results["errors"].append("权限不足：请检查Token权限或Agent ID")
                            validation_results["is_valid"] = False
                        elif response.status_code in [200, 400]:  # 400 might be expected for test message
                            validation_results["suggestions"].append("✅ API连接测试成功")
                        else:
                            validation_results["warnings"].append(f"API返回状态码: {response.status_code}")
                    
                    else:
                        # Test custom API endpoint
                        response = await client.post(
                            api_config.url,
                            headers=api_config.headers,
                            json={"message": "test"}
                        )
                        
                        if response.status_code in [200, 400, 401]:
                            validation_results["suggestions"].append("✅ API端点可访问")
                        else:
                            validation_results["warnings"].append(f"API返回状态码: {response.status_code}")
                            
            except httpx.TimeoutException:
                validation_results["warnings"].append("API连接超时，请检查网络或URL")
            except Exception as e:
                validation_results["warnings"].append(f"连接测试失败: {str(e)[:50]}...")
        
        # Add helpful suggestions
        if validation_results["is_valid"]:
            validation_results["suggestions"].extend([
                "💡 建议先用简单问题测试AI Agent响应",
                "📝 确保Agent已发布且处于活跃状态",
                "🔄 如遇到问题，可尝试重新生成Access Token"
            ])
        
        return {
            "validation_result": validation_results,
            "config_summary": {
                "type": api_config.type,
                "url": api_config.url,
                "has_auth": bool(api_config.headers.get("Authorization")),
                "timeout": api_config.timeout
            }
        }
        
    except json.JSONDecodeError:
        return {
            "validation_result": {
                "is_valid": False,
                "errors": ["配置格式错误：请检查JSON格式"],
                "warnings": [],
                "suggestions": ["请确保配置信息为有效的JSON格式"]
            }
        }
    except Exception as e:
        return {
            "validation_result": {
                "is_valid": False,
                "errors": [f"配置验证失败: {str(e)}"],
                "warnings": [],
                "suggestions": ["请检查配置信息是否完整"]
            }
        }

async def call_deepseek_api_with_fallback(prompt: str, max_retries: int = 2) -> str:
    """Enhanced DeepSeek API call with better error handling and suppressed exceptions"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 500
    }
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
                response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        content = result["choices"][0].get("message", {}).get("content", "").strip()
                        if content and len(content) > 10:
                            return content
                
                if attempt < max_retries - 1:
                    continue
                    
        except Exception as e:
            if attempt < max_retries - 1:
                continue
    
    return "API评估暂时不可用，使用备用评分机制"

# Create alias function to redirect to new implementation
async def conduct_dynamic_conversation(api_config: APIConfig, scenario_info: Dict, user_persona_info: Dict) -> List[Dict]:
    """Redirect to true dynamic conversation implementation"""
    return await conduct_true_dynamic_conversation(api_config, scenario_info, user_persona_info)

async def conduct_true_dynamic_conversation(api_config: APIConfig, scenario_info: Dict, user_persona_info: Dict) -> List[Dict]:
    """
    TRUE dynamic conversation: DeepSeek generates one message at a time based on Coze's actual responses
    No pre-generated scenarios - pure turn-by-turn interaction
    """
    print(f"🗣️ 开始真正动态对话: {scenario_info.get('title', '未命名场景')}")
    
    conversation_history = []
    persona = user_persona_info.get('user_persona', {})
    context = user_persona_info.get('usage_context', {})
    
    # Step 1: Generate ONLY the initial message based on persona and scenario
    print("🎯 DeepSeek生成初始消息...")
    initial_message = await generate_single_initial_message(scenario_info, user_persona_info)
    if not initial_message:
        raise Exception("Failed to generate initial message")
    
    current_user_message = initial_message
    
    # Step 2: Conduct true turn-by-turn conversation (max 5 turns)
    for turn_num in range(1, 6):
        print(f"💬 第 {turn_num} 轮 - 用户消息: {current_user_message[:50]}...")
        
        # Add persona context for better AI understanding
        enhanced_message = f"[作为{persona.get('role', '用户')}，{persona.get('communication_style', '专业沟通')}] {current_user_message}"
        
        # Get Coze response with strict timeout
        coze_response = await call_coze_with_strict_timeout(api_config, enhanced_message)
        if not coze_response:
            print(f"❌ 第 {turn_num} 轮Coze无响应，终止对话")
            break
            
        # Record this turn
        conversation_history.append({
            "turn": turn_num,
            "user_message": current_user_message,
            "enhanced_message": enhanced_message,
            "ai_response": coze_response,
            "response_length": len(coze_response),
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"✅ Coze响应: {coze_response[:80]}...")
        
        # Generate next message based on Coze's actual response
        if turn_num < 5:  # Don't generate after last turn
            print(f"🤖 DeepSeek分析Coze回复，生成第{turn_num + 1}轮消息...")
            next_message = await generate_next_message_based_on_response(
                scenario_info, user_persona_info, conversation_history, coze_response
            )
            
            if not next_message or next_message.upper() in ["END", "FINISH", "DONE"]:
                print(f"🔚 对话自然结束于第 {turn_num} 轮")
                break
                
            current_user_message = next_message
        
    print(f"📊 动态对话完成，共 {len(conversation_history)} 轮")
    return conversation_history

if __name__ == "__main__":
    port = find_available_port()
    print(f"🚀 AI Agent评估平台启动在端口 {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 