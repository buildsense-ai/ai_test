import asyncio
import uvicorn
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
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
import traceback
import uuid
import hashlib
import time

# Database imports
try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False
    print("⚠️ PyMySQL not available. Database features disabled.")

# Coze SDK imports
try:
    from cozepy import COZE_CN_BASE_URL
    from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType
    COZE_SDK_AVAILABLE = True
except ImportError:
    COZE_SDK_AVAILABLE = False
    print("⚠️ Coze SDK not available. Using fallback HTTP requests.")

# Import configuration
import config

# ⭐ Memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil not available, memory monitoring disabled")

# Set up logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add enhanced debugging for cloud deployment issues
import traceback
import logging

# Set up detailed logging for debugging cloud deployment issues
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_memory_usage():
    """Check memory usage and prevent OOM crashes"""
    if not PSUTIL_AVAILABLE:
        print("⚠️ psutil not available, skipping memory check")
        return 0  # Return 0 instead of None for compatibility
    
    try:
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > config.MEMORY_CRITICAL_THRESHOLD:
            error_msg = f"服务器内存使用率危险: {memory_percent:.1f}%"
            print(f"❌ {error_msg}")
            raise HTTPException(status_code=507, detail=f"服务器内存不足 ({memory_percent:.1f}%)，请稍后重试")
        
        if memory_percent > config.MEMORY_WARNING_THRESHOLD:
            print(f"⚠️ 内存使用率警告: {memory_percent:.1f}%")
        
        return memory_percent
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ 内存检查失败: {str(e)}")
        return 0  # Return 0 instead of None for compatibility

# Document processing imports
try:
    import docx
    from PyPDF2 import PdfReader
    DOCUMENT_PROCESSING_AVAILABLE = True
except ImportError:
    DOCUMENT_PROCESSING_AVAILABLE = False

app = FastAPI(title="AI Agent Evaluation Platform", version="4.0.0")

# Add response compression middleware
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Create static directory if it doesn't exist
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Improved document processing functions based on user's approach
def read_docx_file(filepath: str) -> str:
    """Read content from DOCX file with enhanced cloud compatibility"""
    try:
        logger.info(f"📖 开始解析DOCX文件: {filepath}")
        print(f"📖 开始解析DOCX文件: {filepath}")
        
        # Check if file exists and is readable
        if not os.path.exists(filepath):
            error_msg = f"文件不存在: {filepath}"
            logger.error(error_msg)
            return f"错误：{error_msg}"
        
        file_size = os.path.getsize(filepath)
        logger.info(f"📄 文件大小: {file_size} 字节")
        print(f"📄 文件大小: {file_size} 字节")
        
        if file_size == 0:
            error_msg = "文件为空"
            logger.error(error_msg)
            return f"错误：{error_msg}"
        
        # Cloud-compatible processing with multiple fallback methods
        extraction_methods = [
            ("python-docx", lambda: _extract_with_python_docx(filepath)),
            ("zip-xml-advanced", lambda: _extract_with_zip_xml_advanced(filepath)),
            ("zip-xml-simple", lambda: _extract_with_zip_xml_simple(filepath)),
            ("raw-text-extraction", lambda: _extract_raw_text_from_docx(filepath))
        ]
        
        best_result = ""
        successful_method = "none"
        
        for method_name, extraction_func in extraction_methods:
            try:
                logger.info(f"🔄 尝试方法: {method_name}")
                print(f"🔄 尝试方法: {method_name}")
                
                result = extraction_func()
                
                if result and len(result) > len(best_result):
                    best_result = result
                    successful_method = method_name
                    logger.info(f"✅ {method_name} 成功，提取长度: {len(result)}")
                    print(f"✅ {method_name} 成功，提取长度: {len(result)}")
                    
                    # If we get a good result (>100 chars), use it immediately
                    if len(result) > 100:
                        break
                else:
                    logger.warning(f"⚠️ {method_name} 结果不佳: {len(result) if result else 0} 字符")
                    print(f"⚠️ {method_name} 结果不佳: {len(result) if result else 0} 字符")
                    
            except Exception as e:
                logger.warning(f"⚠️ {method_name} 失败: {str(e)}")
                print(f"⚠️ {method_name} 失败: {str(e)}")
                continue
        
        if not best_result:
            return "错误：所有解析方法均失败，建议转换为TXT格式后重试"
        
        # Validate extraction result
        if len(best_result) < 20:
            logger.warning(f"⚠️ 提取内容过短: {len(best_result)} 字符")
            print(f"⚠️ 提取内容过短: {len(best_result)} 字符")
            
            if len(best_result) < 10:
                return f"错误：提取内容过短({len(best_result)}字符)，建议转换为TXT格式：\n\n💡 解决方案：\n1. 使用Word打开文档，另存为.txt格式\n2. 或复制文档内容，直接粘贴到文本框中\n3. 检查文档是否包含主要为图片/表格内容"
        
        logger.info(f"✅ DOCX解析成功 (方法: {successful_method})，提取长度: {len(best_result)} 字符")
        print(f"✅ DOCX解析成功 (方法: {successful_method})，提取长度: {len(best_result)} 字符")
        
        # Debug: Show first part of content to verify extraction
        content_preview = best_result[:200] + "..." if len(best_result) > 200 else best_result
        logger.debug(f"📝 内容预览: {content_preview}")
        print(f"📝 内容预览: {content_preview}")
        
        return best_result
        
    except Exception as e:
        error_msg = f"DOCX文件处理异常: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(f"📋 异常详情: {traceback.format_exc()}")
        print(f"❌ {error_msg}")
        print(f"📋 异常详情: {traceback.format_exc()}")
        return f"错误：{error_msg}\n\n💡 云环境解决方案：\n1. 转换为TXT格式重新上传\n2. 复制文档内容直接粘贴\n3. 检查文档是否过于复杂"

def _extract_with_python_docx(filepath: str) -> str:
    """Method 1: Standard python-docx extraction"""
    from docx import Document
    
    doc = Document(filepath)
    full_text = []
    
    # Extract paragraphs
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            full_text.append(paragraph.text.strip())
    
    # Extract tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    full_text.append(cell.text.strip())
    
    return '\n'.join(full_text)

def _extract_with_zip_xml_advanced(filepath: str) -> str:
    """Method 2: Advanced ZIP+XML extraction with namespace handling"""
    import zipfile
    import xml.etree.ElementTree as ET
    
    with zipfile.ZipFile(filepath, 'r') as zip_file:
        # Try to get document.xml
        xml_content = zip_file.read('word/document.xml')
        
        # Parse with namespace awareness
        root = ET.fromstring(xml_content)
        
        # Define Word document namespaces
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'v': 'urn:schemas-microsoft-com:vml',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        }
        
        text_parts = []
        
        # Extract text from paragraphs
        for para in root.findall('.//w:p', namespaces):
            para_text = ""
            for text_elem in para.findall('.//w:t', namespaces):
                if text_elem.text:
                    para_text += text_elem.text
            if para_text.strip():
                text_parts.append(para_text.strip())
        
        # Extract text from tables
        for table in root.findall('.//w:tbl', namespaces):
            for row in table.findall('.//w:tr', namespaces):
                row_text = ""
                for cell in row.findall('.//w:tc', namespaces):
                    cell_text = ""
                    for text_elem in cell.findall('.//w:t', namespaces):
                        if text_elem.text:
                            cell_text += text_elem.text
                    if cell_text.strip():
                        row_text += cell_text.strip() + " "
                if row_text.strip():
                    text_parts.append(row_text.strip())
        
        return '\n'.join(text_parts)

def _extract_with_zip_xml_simple(filepath: str) -> str:
    """Method 3: Simple ZIP+XML extraction (cloud fallback)"""
    import zipfile
    import xml.etree.ElementTree as ET
    
    with zipfile.ZipFile(filepath, 'r') as zip_file:
        xml_content = zip_file.read('word/document.xml')
        root = ET.fromstring(xml_content)
        
        # Simple text extraction - get all text elements
        text_content = []
        for elem in root.iter():
            if elem.text and elem.text.strip():
                text_content.append(elem.text.strip())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_text = []
        for text in text_content:
            if text not in seen and len(text) > 1:  # Avoid single characters
                seen.add(text)
                unique_text.append(text)
        
        return ' '.join(unique_text)

def _extract_raw_text_from_docx(filepath: str) -> str:
    """Method 4: Raw text extraction from ZIP (last resort)"""
    import zipfile
    import re
    
    with zipfile.ZipFile(filepath, 'r') as zip_file:
        # Try to extract any readable text from the ZIP contents
        text_parts = []
        
        # Read document.xml as raw text and extract with regex
        try:
            xml_content = zip_file.read('word/document.xml').decode('utf-8', errors='ignore')
            
            # Use regex to find text between XML tags
            text_matches = re.findall(r'>([^<]+)<', xml_content)
            
            for match in text_matches:
                cleaned = match.strip()
                if len(cleaned) > 2 and not cleaned.isdigit():  # Skip numbers and short strings
                    text_parts.append(cleaned)
            
        except Exception:
            pass
        
        # Also try other XML files in the document
        for file_info in zip_file.filelist:
            if file_info.filename.endswith('.xml') and 'word/' in file_info.filename:
                try:
                    content = zip_file.read(file_info.filename).decode('utf-8', errors='ignore')
                    text_matches = re.findall(r'>([^<]+)<', content)
                    
                    for match in text_matches:
                        cleaned = match.strip()
                        if len(cleaned) > 2 and not cleaned.isdigit():
                            text_parts.append(cleaned)
                            
                except Exception:
                    continue
        
        # Remove duplicates and join
        unique_parts = list(dict.fromkeys(text_parts))  # Preserve order
        return ' '.join(unique_parts)

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
    """Process uploaded document using improved approach with comprehensive error handling"""
    if not file or not file.filename:
        logger.error("⚠️ 文档上传：文件为空或无文件名")
        print("⚠️ 文档上传：文件为空或无文件名")
        return "错误：未提供有效文件"
    
    # ⭐ Security: Validate filename
    if not validate_filename(file.filename):
        error_msg = f"不安全的文件名: {file.filename}"
        logger.error(f"❌ {error_msg}")
        print(f"❌ {error_msg}")
        return f"错误：{error_msg}"
    
    # Log file info with detailed debugging
    logger.info(f"📄 开始处理上传文件: {file.filename}")
    logger.info(f"📄 文件类型: {getattr(file, 'content_type', '未知')}")
    print(f"📄 开始处理上传文件: {file.filename}")
    print(f"📄 文件类型: {getattr(file, 'content_type', '未知')}")
    
    # Create temporary file
    suffix = os.path.splitext(file.filename)[1].lower()
    logger.info(f"📄 检测文件扩展名: {suffix}")
    print(f"📄 检测文件扩展名: {suffix}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        try:
            # Write uploaded content to temporary file
            logger.info("📤 读取上传文件内容...")
            print("📤 读取上传文件内容...")
            content = await file.read()
            
            if not content:
                logger.error("❌ 上传文件内容为空")
                print("❌ 上传文件内容为空")
                return "错误：上传文件内容为空"
            
            logger.info(f"📤 文件大小: {len(content)} 字节")
            print(f"📤 文件大小: {len(content)} 字节")
            
            # ⭐ Critical: File size limit to prevent memory issues
            if len(content) > config.MAX_FILE_SIZE:
                error_msg = f"文件大小 {len(content)} 字节超过10MB限制"
                logger.error(f"❌ {error_msg}")
                print(f"❌ {error_msg}")
                return f"错误：{error_msg}"
            
            tmp_file.write(content)
            tmp_file.flush()
            
            logger.info(f"💾 临时文件已创建: {tmp_file.name}")
            print(f"💾 临时文件已创建: {tmp_file.name}")
            
            # Process based on file extension with enhanced debugging
            try:
                if suffix in ['.doc', '.docx']:
                    logger.info("📖 使用Word文档解析器...")
                    print("📖 使用Word文档解析器...")
                    result = read_docx_file(tmp_file.name)
                elif suffix == '.pdf':
                    logger.info("📖 使用PDF文档解析器...")
                    print("📖 使用PDF文档解析器...")
                    result = read_pdf_file(tmp_file.name)
                elif suffix == '.txt':
                    logger.info("📖 使用文本文件解析器...")
                    print("📖 使用文本文件解析器...")
                    result = read_txt_file(tmp_file.name)
                else:
                    error_msg = f"不支持的文件格式: {suffix}。支持格式: Word (.docx), PDF (.pdf), 文本 (.txt)"
                    logger.error(f"❌ {error_msg}")
                    print(f"❌ {error_msg}")
                    return error_msg
            except Exception as parse_error:
                logger.error(f"❌ 文档解析异常: {str(parse_error)}")
                logger.error(f"📋 解析异常详情: {traceback.format_exc()}")
                print(f"❌ 文档解析异常: {str(parse_error)}")
                print(f"📋 解析异常详情: {traceback.format_exc()}")
                return f"错误：文档解析失败 - {type(parse_error).__name__}: {str(parse_error)}"
            
            # Validate result with enhanced debugging
            if not result:
                logger.error("❌ 文档解析结果为空")
                print("❌ 文档解析结果为空")
                return "错误：文档解析结果为空，可能文件已损坏或格式不正确"
            
            if len(result) < 10:
                logger.warning(f"⚠️ 文档解析结果过短: {len(result)} 字符")
                print(f"⚠️ 文档解析结果过短: {len(result)} 字符")
                return f"错误：文档内容过短({len(result)}字符)，可能解析失败"
            
            # Check for error messages in result
            error_indicators = ['error', 'exception', 'traceback', 'failed', 'Error:', 'Exception:', '处理失败', '解析失败']
            if any(indicator in result for indicator in error_indicators):
                logger.warning("⚠️ 解析结果中包含错误信息")
                print("⚠️ 解析结果中包含错误信息")
                return "错误：文档解析过程中出现错误，请检查文件格式或内容"
            
            # Debug: Log partial content to help with debugging
            content_preview = result[:500] + "..." if len(result) > 500 else result
            logger.info(f"✅ 文档处理成功，提取内容长度: {len(result)} 字符")
            logger.debug(f"📝 文档内容预览: {content_preview}")
            print(f"✅ 文档处理成功，提取内容长度: {len(result)} 字符")
            print(f"📝 文档内容预览: {content_preview}")
            
            return result
            
        except Exception as e:
            error_msg = f"文档处理异常: {str(e)}"
            logger.error(f"❌ {error_msg}")
            logger.error(f"📋 异常类型: {type(e).__name__}")
            logger.error(f"📋 异常详情: {traceback.format_exc()}")
            print(f"❌ {error_msg}")
            print(f"📋 异常类型: {type(e).__name__}")
            print(f"📋 异常详情: {traceback.format_exc()}")
            
            # Return a clean error message instead of the raw exception
            return f"错误：文档处理失败 - {type(e).__name__}: {str(e)}。请检查文件格式是否正确。"
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(tmp_file.name):
                    os.unlink(tmp_file.name)
                    logger.info(f"🗑️ 临时文件已清理: {tmp_file.name}")
                    print(f"🗑️ 临时文件已清理: {tmp_file.name}")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ 临时文件清理失败: {str(cleanup_error)}")
                print(f"⚠️ 临时文件清理失败: {str(cleanup_error)}")
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
    
    # Message processing options
    use_raw_messages: Optional[bool] = Field(default=False, description="Use raw user messages without persona enhancement")
    
    # Coze compatibility (temporary until full API support)
    coze_bot_id: Optional[str] = Field(default=None, description="Coze Bot ID for current implementation")

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

# Configuration - Using config.py for direct API key management
# All constants are now accessed directly from config module

print(f"✅ Configuration loaded from config.py - DeepSeek API configured")

# Conversation continuity management
class ConversationManager:
    """Manage conversation continuity across API calls"""
    
    def __init__(self, api_config: 'APIConfig'):
        self.api_config = api_config
        self.conversation_id = ""
        self.api_type = self._determine_api_type()
        
    def _determine_api_type(self) -> str:
        """Determine the API type based on URL"""
        if "/v1/chat-messages" in self.api_config.url or "dify" in self.api_config.url.lower():
            return "dify"
        elif "coze" in self.api_config.url.lower():
            return "coze"
        else:
            return "custom"
    
    def start_new_conversation(self) -> str:
        """Start a new conversation and return conversation ID"""
        if self.api_type == "dify":
            # For Dify, conversation_id will be extracted from first response
            self.conversation_id = ""
        else:
            # For other APIs, generate a unique conversation ID
            self.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        return self.conversation_id
    
    def get_conversation_id(self) -> str:
        """Get current conversation ID"""
        return self.conversation_id
    
    def update_conversation_id(self, new_id: str):
        """Update conversation ID (used when extracted from API response)"""
        if new_id and new_id != self.conversation_id:
            self.conversation_id = new_id
            print(f"🔗 更新对话ID: {new_id[:20]}...")

async def call_deepseek_api(prompt: str, max_retries: int = 2) -> str:
    """
    Call DeepSeek API with improved error handling
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
    
    for attempt in range(max_retries):
        try:
            timeout = httpx.Timeout(config.DEEPSEEK_TIMEOUT, connect=10.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(config.DEEPSEEK_API_URL, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"].strip()
                    else:
                        raise Exception("No valid response from API")
                elif response.status_code == 401:
                    raise Exception("API authentication failed - check API key")
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise Exception("API rate limited")
                else:
                    error_text = response.text if hasattr(response, 'text') else 'Unknown error'
                    raise Exception(f"API error {response.status_code}: {error_text}")
                    
        except (asyncio.TimeoutError, httpx.TimeoutException):
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            raise Exception(f"API timeout after {config.DEEPSEEK_TIMEOUT}s")
        except httpx.RequestError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise e
            
    raise Exception("All API attempts failed")

async def call_ai_agent_api(api_config: APIConfig, message: str, conversation_manager: ConversationManager = None, use_raw_message: bool = False) -> str:
    """Call AI Agent API - supports Coze, Dify, and custom APIs with conversation continuity"""
    try:
        # 📝 Debug log for message processing mode
        message_preview = message[:80] + "..." if len(message) > 80 else message
        if use_raw_message:
            print(f"🔍 [RAW MODE] {message_preview}")
        else:
            print(f"🔍 [ENHANCED MODE] {message_preview}")
        
        # Check if we should use Coze API (either explicit coze URL or fallback URL)
        if "coze" in api_config.url.lower() or "fallback" in api_config.url.lower():
            return await call_coze_api_fallback(message, use_raw_message=use_raw_message)
        # Check if this is a Dify API (based on URL pattern)
        elif "/v1/chat-messages" in api_config.url or "dify" in api_config.url.lower():
            conversation_id = conversation_manager.get_conversation_id() if conversation_manager else ""
            response_content, new_conversation_id = await call_dify_api(api_config, message, conversation_id, use_raw_message=use_raw_message)
            
            # Update conversation manager with new conversation ID
            if conversation_manager and new_conversation_id:
                conversation_manager.update_conversation_id(new_conversation_id)
            
            return response_content
        else:
            # Generic API support
            headers = api_config.headers.copy()
            headers.setdefault("Content-Type", "application/json")
            
            # Use appropriate payload field based on raw message mode
            if use_raw_message:
                payload = {"input": message, "question": message, "query": message}  # Raw user input fields
            else:
                payload = {"message": message, "query": message}  # Enhanced message fields
            
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
                    raw_response = ""
                    if "response" in result:
                        raw_response = result["response"]
                    elif "answer" in result:
                        raw_response = result["answer"]
                    elif "message" in result:
                        raw_response = result["message"]
                    else:
                        raw_response = str(result)
                    
                    # 🔧 UNIVERSAL FIX: Apply plugin extraction to generic API responses too
                    if raw_response:
                        cleaned_response = clean_ai_response(raw_response)
                        if cleaned_response:
                            print(f"🧹 通用API响应经过插件提取处理: {cleaned_response[:100]}...")
                            return cleaned_response
                        return raw_response
                    else:
                        return "Empty response from API"
                else:
                    return f"API调用失败: {response.status_code}"
                    
    except Exception as e:
        print(f"❌ AI Agent API调用异常: {str(e)}")
        return "AI Agent API调用失败，请检查配置"

async def call_dify_api(api_config: APIConfig, message: str, conversation_id: str = "", use_raw_message: bool = False) -> tuple:
    """
    Call Dify API with proper payload format and conversation continuity
    Returns: (response_content, conversation_id)
    """
    try:
        print(f"🔍 调用Dify API: {api_config.url}")
        
        headers = api_config.headers.copy()
        headers.setdefault("Content-Type", "application/json")
        
        # Dify API specific payload format with conversation continuity
        # 📝 Debug log for Dify message processing  
        message_preview = message[:60] + "..." if len(message) > 60 else message
        if use_raw_message:
            print(f"🔍 [DIFY RAW] {message_preview}")
            user_field = "evaluation-user-raw"
        else:
            print(f"🔍 [DIFY ENHANCED] {message_preview}")
            user_field = "evaluation-user"
            
        payload = {
            "inputs": {},
            "query": message,
            "response_mode": "streaming",
            "conversation_id": conversation_id,  # Use provided conversation_id for continuity
            "user": user_field,
            "files": []
        }
        
        print(f"📤 Dify API请求载荷: {json.dumps(payload, ensure_ascii=False)[:200]}...")
        if conversation_id:
            print(f"🔗 使用对话ID: {conversation_id[:20]}...")
        
        async with httpx.AsyncClient(timeout=httpx.Timeout(api_config.timeout)) as client:
            response = await client.post(api_config.url, headers=headers, json=payload)
            
            print(f"🔍 Dify API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                # Check if response is streaming
                content_type = response.headers.get("content-type", "").lower()
                
                if "text/event-stream" in content_type or payload.get("response_mode") == "streaming":
                    # Handle streaming response
                    response_text = response.text
                    print(f"🔍 处理Dify流式响应 ({len(response_text)} chars)")
                    
                    if not response_text.strip():
                        raise Exception("Empty streaming response from Dify API")
                    
                    # Parse Dify streaming format
                    lines = response_text.strip().split('\n')
                    collected_content = ""
                    conversation_id_extracted = conversation_id  # Start with input conversation_id
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        if line.startswith("data: "):
                            data_content = line[6:]  # Remove "data: " prefix
                            
                            # Skip end marker
                            if data_content.strip() in ['"[DONE]"', "[DONE]"]:
                                break
                            
                            try:
                                data_json = json.loads(data_content)
                                
                                # Extract conversation_id for future continuity
                                if "conversation_id" in data_json and data_json["conversation_id"]:
                                    conversation_id_extracted = data_json["conversation_id"]
                                
                                # Extract content from Dify response
                                if "answer" in data_json:
                                    collected_content += data_json["answer"]
                                elif "data" in data_json and "answer" in data_json["data"]:
                                    collected_content += data_json["data"]["answer"]
                                elif "message" in data_json:
                                    collected_content += data_json["message"]
                                    
                            except json.JSONDecodeError:
                                continue
                    
                    if collected_content:
                        print(f"✅ Dify流式响应解析成功: {collected_content[:100]}...")
                        # 🔧 UNIVERSAL FIX: Apply plugin extraction to Dify responses too
                        cleaned_content = clean_ai_response(collected_content)
                        if cleaned_content and cleaned_content != collected_content:
                            print(f"🧹 Dify响应经过插件提取处理: {cleaned_content[:100]}...")
                            collected_content = cleaned_content
                        
                        if conversation_id_extracted and conversation_id_extracted != conversation_id:
                            print(f"🔗 提取到对话ID: {conversation_id_extracted[:20]}...")
                        return collected_content.strip(), conversation_id_extracted
                    else:
                        print("❌ 未从Dify流式响应中提取到有效内容")
                        raise Exception("No valid content in Dify streaming response")
                
                else:
                    # Handle regular JSON response
                    result = response.json()
                    print(f"🔍 Dify JSON响应: {json.dumps(result, ensure_ascii=False)[:300]}...")
                    
                    # Try to extract answer from various possible response formats
                    response_content = ""
                    conversation_id_extracted = conversation_id
                    
                    if "answer" in result:
                        response_content = result["answer"].strip()
                    elif "data" in result and isinstance(result["data"], dict):
                        if "answer" in result["data"]:
                            response_content = result["data"]["answer"].strip()
                        elif "message" in result["data"]:
                            response_content = result["data"]["message"].strip()
                    elif "message" in result:
                        response_content = result["message"].strip()
                    else:
                        print(f"⚠️ 未知的Dify响应格式，尝试返回完整响应")
                        response_content = str(result)
                    
                    # Extract conversation_id from JSON response
                    if "conversation_id" in result and result["conversation_id"]:
                        conversation_id_extracted = result["conversation_id"]
                    
                    # 🔧 UNIVERSAL FIX: Apply plugin extraction to Dify JSON responses too
                    if response_content:
                        cleaned_content = clean_ai_response(response_content)
                        if cleaned_content:
                            response_content = cleaned_content
                            print(f"🧹 Dify JSON响应经过插件提取处理: {response_content[:100]}...")
                    
                    return response_content, conversation_id_extracted
            else:
                error_text = response.text if hasattr(response, 'text') else 'Unknown error'
                print(f"❌ Dify API HTTP错误 {response.status_code}: {error_text}")
                raise Exception(f"Dify API HTTP error {response.status_code}: {error_text}")
                
    except (asyncio.TimeoutError, httpx.TimeoutException):
        print(f"❌ Dify API超时 after {api_config.timeout}s")
        raise Exception(f"Dify API timeout after {api_config.timeout}s")
    except httpx.RequestError as e:
        print(f"❌ Dify API网络错误: {str(e)}")
        raise Exception(f"Dify API network error: {str(e)}")
    except Exception as e:
        print(f"❌ Dify API调用异常: {str(e)}")
        raise e

async def call_coze_api_fallback(message: str, bot_id: str = None, use_raw_message: bool = False) -> str:
    """
    Enhanced Coze API with proper plugin response extraction
    """
    if not bot_id:
        bot_id = config.DEFAULT_COZE_BOT_ID
    
    url = f"{config.COZE_API_BASE}/v3/chat"
    headers = {
        "Authorization": f"Bearer {config.COZE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "parameters": {},
        "bot_id": bot_id,
        "user_id": "123",
        "additional_messages": [
            {
                "content_type": "text",
                "type": "question",
                "role": "user",
                "content": message
            }
        ],
        "auto_save_history": True,
        "stream": True
    }

    # 📝 Clean debug logging
    message_preview = message[:60] + "..." if len(message) > 60 else message
    print(f"🔍 [COZE] {message_preview}")

    try:
        async with httpx.AsyncClient(timeout=config.COZE_TIMEOUT) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                response_text = response.text
                
                print(f"🔍 Coze API Response Status: {response.status_code}")
                print(f"🔍 Handling SSE streaming response ({len(response_text)} chars)")
                
                # Raw response length for debugging
                # print(f"🔍 RAW RESPONSE (first 1000 chars): {response_text[:1000]}...") # Disabled for cleaner output

                if "text/event-stream" in content_type or "stream" in response_text:
                    # Parse SSE streaming response
                    lines = response_text.strip().split('\n')
                    current_event = None
                    main_answer = ""
                    assistant_messages = []
                    collected_content = ""
                    plugin_responses = []  # 🔧 NEW: Collect plugin responses
                    
                    # 🔍 PATTERN SEARCH: Look for tool output patterns in raw response
                    import re
                    tool_output_patterns = [
                        r'"tool_output_content":"([^"]+)"',
                        r'"tool_output_content":\s*"([^"]+)"',
                        r'答案：([^"\\n]+)',
                        r'"answer":"([^"]+)"',
                        r'"response":"([^"]+)"',
                        r'"result":"([^"]+)"'
                    ]
                    
                    for pattern in tool_output_patterns:
                        matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL)
                        for match in matches:
                            # Clean up escape characters
                            cleaned_match = match.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
                            if len(cleaned_match.strip()) > 20:  # Substantial content
                                plugin_responses.append(cleaned_match.strip())
                    
                    for line in lines:
                        line = line.strip()
                        
                        if line.startswith("event:"):
                            current_event = line[6:].strip()
                        elif line.startswith("data:") and len(line) > 5:
                            data_content = line[5:].strip()
                            
                            if data_content in ["[DONE]", ""]:
                                continue
                                
                            try:
                                data_json = json.loads(data_content)
                                
                                if current_event == "conversation.message.delta":
                                    # This is streaming content chunk
                                    if "content" in data_json:
                                        content_chunk = data_json["content"]
                                        # Don't collect plugin invocation chunks
                                        if not (content_chunk.strip().startswith('{"name":"') or 
                                                '"plugin_id":' in content_chunk or
                                                '"arguments":' in content_chunk):
                                            collected_content += content_chunk
                                        
                                elif current_event == "conversation.message.completed":
                                    # This is a completed message
                                    if "content" in data_json:
                                        message_content = data_json["content"]
                                        role = data_json.get("role", "unknown")
                                        msg_type = data_json.get("type", "text")
                                        
                                        # 🔧 NEW: Enhanced plugin response handling
                                        if role == "assistant" and message_content:
                                            # Check if content is a plugin invocation JSON
                                            if (message_content.strip().startswith('{"name":"') and 
                                                '"arguments":' in message_content and
                                                '"plugin_id":' in message_content):
                                                print(f"🔧 Found plugin invocation: {message_content[:200]}...")
                                                
                                                # Try to extract tool output from plugin response
                                                try:
                                                    plugin_data = json.loads(message_content)
                                                    
                                                    # Look for tool output in various possible fields
                                                    tool_output_fields = [
                                                        'tool_output_content',
                                                        'output',
                                                        'result', 
                                                        'content',
                                                        'answer',
                                                        'response',
                                                        'text',
                                                        'data'
                                                    ]
                                                    
                                                    found_output = False
                                                    
                                                    # Check top-level fields
                                                    for field in tool_output_fields:
                                                        if field in plugin_data and plugin_data[field]:
                                                            tool_output = str(plugin_data[field])
                                                            if len(tool_output.strip()) > 10:  # Substantial content
                                                                print(f"✅ Extracted plugin output from {field}: {tool_output[:100]}...")
                                                                plugin_responses.append(tool_output)
                                                                found_output = True
                                                                break
                                                    
                                                    # Check nested arguments if not found yet
                                                    if not found_output and 'arguments' in plugin_data and isinstance(plugin_data['arguments'], dict):
                                                        args = plugin_data['arguments']
                                                        for field in tool_output_fields:
                                                            if field in args and args[field]:
                                                                tool_output = str(args[field])
                                                                if len(tool_output.strip()) > 10:
                                                                    print(f"✅ Extracted plugin output from args.{field}: {tool_output[:100]}...")
                                                                    plugin_responses.append(tool_output)
                                                                    found_output = True
                                                                    break
                                                    
                                                except json.JSONDecodeError as e:
                                                    print(f"⚠️ Failed to parse plugin JSON: {e}")
                                                
                                                continue  # Skip adding to assistant_messages
                                            
                                            # Regular assistant message
                                            assistant_messages.append({
                                                "content": message_content,
                                                "type": msg_type,
                                                "length": len(message_content)
                                            })
                                        
                                        # Set main answer if this is substantial content and not plugin invocation
                                        if (message_content and len(message_content) > 20 and 
                                            not (message_content.strip().startswith('{"name":"') and 
                                                 '"arguments":' in message_content and
                                                 '"plugin_id":' in message_content)):
                                            if not main_answer or len(message_content) > len(main_answer):
                                                main_answer = message_content
                                
                                elif current_event == "conversation.chat.completed":
                                    # Chat completion event - might have final answer
                                    if "last_message" in data_json and data_json["last_message"].get("content"):
                                        final_content = data_json["last_message"]["content"]
                                        if len(final_content) > 20:
                                            main_answer = final_content
                                
                                # 🔧 NEW: Check for tool output events
                                elif current_event == "conversation.message.plugin.finish":
                                    if "content" in data_json:
                                        plugin_output = data_json["content"]
                                        if len(plugin_output.strip()) > 10:
                                            print(f"✅ Plugin finish event with output: {plugin_output[:100]}...")
                                            plugin_responses.append(plugin_output)
                                
                                # 🔧 CRITICAL: Extract plugin content from stream_plugin_finish events
                                if current_event == "conversation.message.completed" and "content" in data_json:
                                    content = data_json["content"]
                                    # Check if this is a stream_plugin_finish event with tool_output_content
                                    if isinstance(content, str) and '"msg_type":"stream_plugin_finish"' in content:
                                        try:
                                            # Parse the JSON content to extract tool_output_content
                                            inner_json = json.loads(content)
                                            if inner_json.get("msg_type") == "stream_plugin_finish" and "data" in inner_json:
                                                data_str = inner_json["data"]
                                                if isinstance(data_str, str):
                                                    data_content = json.loads(data_str)
                                                    if "tool_output_content" in data_content:
                                                        tool_output = data_content["tool_output_content"]
                                                        if tool_output and len(tool_output.strip()) > 20:
                                                            print(f"✅ Extracted plugin output: {tool_output[:200]}...")
                                                            plugin_responses.append(tool_output)
                                        except (json.JSONDecodeError, KeyError) as e:
                                            print(f"⚠️ Failed to parse plugin content: {e}")
                                
                                # Minimal logging for debugging
                                # if current_event in ["conversation.message.completed", "conversation.message.delta"] and "content" in data_json:
                                #     content_preview = str(data_json["content"])[:100] if data_json["content"] else "empty"
                                #     print(f"🔍 {current_event}: {content_preview}...")
                                
                                # Check for tool output in tool_response type messages
                                if current_event == "conversation.message.completed" and data_json.get("type") == "tool_response":
                                    if "content" in data_json:
                                        tool_content = data_json["content"]
                                        if tool_content and len(str(tool_content).strip()) > 10:
                                            print(f"✅ Found tool response: {str(tool_content)[:200]}...")
                                            # Skip the generic "directly streaming reply" message
                                            if "directly streaming reply" not in str(tool_content):
                                                plugin_responses.append(str(tool_content))
                                
                                # Also check for direct content fields regardless of event
                                elif "content" in data_json and not data_json.get("msg_type"):
                                    content = data_json["content"]
                                    if (content and len(content) > 20 and 
                                        not any(keyword in content for keyword in [
                                            '用户编写的信息', '用户画像信息', '用户记忆点信息'
                                        ]) and
                                        not (content.strip().startswith('{"name":"') and 
                                             '"arguments":' in content and
                                             '"plugin_id":' in content)):
                                        if not main_answer or len(content) > len(main_answer):
                                            main_answer = content
                                
                            except json.JSONDecodeError as e:
                                continue
                    
                    # 🔧 ENHANCED: Priority order for response content 
                    print(f"🔍 Response content summary: {len(plugin_responses)} plugins, {len(assistant_messages)} messages, main_answer: {len(main_answer) if main_answer else 0} chars")
                    
                    # 1. Plugin responses (highest priority for technical queries)
                    if plugin_responses:
                        # Use the longest/most substantial plugin response
                        best_plugin_response = max(plugin_responses, key=len)
                        if len(best_plugin_response) > 20:
                            print(f"✅ Using plugin response ({len(best_plugin_response)} chars)")
                            return clean_ai_response(best_plugin_response)
                    
                    # 2. Main answer (from completed messages)
                    if main_answer and not any(keyword in main_answer for keyword in [
                        '用户编写的信息', '用户画像信息', '用户记忆点信息', 'wraped_text', 'origin_search_results'
                    ]):
                        print(f"✅ Using main answer ({len(main_answer)} chars): {main_answer[:100]}...")
                        return clean_ai_response(main_answer)
                    
                    # 3. Look for non-system assistant messages
                    for i, msg in enumerate(assistant_messages):
                        content = msg["content"]
                        if (not any(keyword in content for keyword in [
                            '用户编写的信息', '用户画像信息', '用户记忆点信息', 'wraped_text', 'origin_search_results'
                        ]) and
                        not (content.strip().startswith('{"name":"') and 
                             '"arguments":' in content and
                             '"plugin_id":' in content)):
                            print(f"✅ Using assistant message ({len(content)} chars): {content[:100]}...")
                            return clean_ai_response(content)
                    
                    # 4. Collected streaming content (delta)
                    if (collected_content and 
                        not any(keyword in collected_content for keyword in [
                            '用户编写的信息', '用户画像信息', '用户记忆点信息', 'wraped_text', 'origin_search_results'
                        ]) and
                        not (collected_content.strip().startswith('{"name":"') and 
                             '"arguments":' in collected_content and
                             '"plugin_id":' in collected_content)):
                        print(f"✅ Using streaming content ({len(collected_content)} chars): {collected_content[:100]}...")
                        return clean_ai_response(collected_content)
                    
                    # 5. Check for billing errors before returning empty
                    if "unpaid bills" in response_text or "code\":4027" in response_text:
                        print("💰 ❌ Coze账户余额不足或有未付账单")
                        print("💰 详情: https://console.volcengine.com/coze-pro/overview")
                        return "❌ API Error: Coze账户余额不足，请联系管理员充值账户后重试"
                    
                    # 6. If all content was system messages, return empty
                    print("❌ No conversational content found (system messages only)")
                    print(f"🔍 COMPLETE RAW RESPONSE FOR DEBUGGING: {response_text}")
                    return ""  # Return empty to trigger proper handling
                
                else:
                    # Handle regular JSON response
                    result = response.json()
                    print(f"🔍 Coze API Response Structure: {json.dumps(result, indent=2)[:500]}...")
                    
                    if result.get("code") == 0 and "data" in result:
                        data = result["data"]
                        
                        # Handle non-streaming response format
                        if "messages" in data and len(data["messages"]) > 0:
                            # Get the last assistant message
                            for msg in reversed(data["messages"]):
                                if msg.get("role") == "assistant" and msg.get("content"):
                                    print(f"✅ Found assistant response: {msg['content'][:100]}...")
                                    return clean_ai_response(msg["content"])
                            
                            # Fallback to any message content
                            for msg in data["messages"]:
                                if msg.get("content"):
                                    print(f"✅ Found fallback response: {msg['content'][:100]}...")
                                    return clean_ai_response(msg["content"])
                        
                        # Check for other possible response formats
                        if "answer" in data:
                            print(f"✅ Found answer field: {data['answer'][:100]}...")
                            return clean_ai_response(data["answer"])
                        
                        if "content" in data:
                            print(f"✅ Found content field: {data['content'][:100]}...")
                            return clean_ai_response(data["content"])
                        
                        print(f"⚠️ No response content found in data: {list(data.keys())}")
                        raise Exception("No valid response content in Coze API result")
                    else:
                        error_msg = result.get("msg", "Unknown Coze API error")
                        print(f"❌ Coze API returned error: {error_msg}")
                        raise Exception(f"Coze API error: {error_msg}")
            else:
                error_text = response.text if hasattr(response, 'text') else 'Unknown error'
                print(f"❌ HTTP error {response.status_code}: {error_text}")
                raise Exception(f"Coze API HTTP error {response.status_code}: {error_text}")
                
    except (asyncio.TimeoutError, httpx.TimeoutException):
        print(f"❌ Coze API timeout after {config.COZE_TIMEOUT}s")
        raise Exception(f"Coze API timeout after {config.COZE_TIMEOUT}s")
    except httpx.RequestError as e:
        print(f"❌ Coze API network error: {str(e)}")
        raise Exception(f"Coze API network error: {str(e)}")
    except Exception as e:
        print(f"❌ Coze API unexpected error: {str(e)}")
        raise e

def extract_score_from_response(response: str) -> float:
    """Extract numerical score from DeepSeek response (1-100 scale)"""
    try:
        # Look for patterns like "评分：85分", "得分：75", "85/100", etc.
        patterns = [
            r'评分[：:]\s*(\d+(?:\.\d+)?)',
            r'得分[：:]\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*分',
            r'(\d+(?:\.\d+)?)\s*/\s*100',
            r'(\d+(?:\.\d+)?)\s*星'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                score = float(match.group(1))
                # If score appears to be on 1-5 scale, convert to 1-100
                if score <= 5.0:
                    score = score * 20  # Convert 1-5 to 20-100
                return min(max(score, 1.0), 100.0)  # Clamp between 1-100
        
        # If no pattern found, try to find any number
        numbers = re.findall(r'\d+(?:\.\d+)?', response)
        if numbers:
            for num in numbers:
                score = float(num)
                if 1 <= score <= 5:
                    return score * 20  # Convert 1-5 to 20-100
                elif 1 <= score <= 100:
                    return score
        
        # Default fallback
        return 60.0  # Middle score
        
    except Exception:
        return 60.0  # Middle score on error

async def call_coze_api_sdk(bot_id: str, message: str) -> str:
    """
    Use official Coze SDK for API calls (preferred method)
    """
    if not COZE_SDK_AVAILABLE:
        print("⚠️ Coze SDK不可用，使用HTTP fallback")
        return await call_coze_api_fallback(message, bot_id)
    
    try:
        # Initialize Coze client with config settings
        coze = Coze(
            auth=TokenAuth(token=config.COZE_API_TOKEN), 
            base_url=COZE_CN_BASE_URL
        )
        
        # Generate a unique user ID for this conversation
        user_id = f"eval_user_{int(time.time())}"
        
        print(f"🔄 使用Coze SDK调用 Bot {bot_id}")
        
        # Collect response content
        response_content = ""
        token_count = 0
        
        # Track plugin responses like in the HTTP fallback method
        plugin_responses = []
        collected_content = ""
        
        # Create streaming chat
        for event in coze.chat.stream(
            bot_id=bot_id,
            user_id=user_id,
            additional_messages=[
                Message.build_user_question_text(message),
            ],
        ):
            # Enhanced logging for debugging
            print(f"[📡 EVENT] {event.event}")
            
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                content = event.message.content or ""
                print(f"[📦 DELTA CONTENT] {content[:100]}...")
                
                # 🔧 Enhanced plugin detection using existing patterns from HTTP fallback
                # Check if content contains plugin JSON data
                if ('"tool_output_content"' in content or 
                    '"plugin_id"' in content or
                    '"msg_type":"stream_plugin_finish"' in content):
                    
                    print(f"🔧 Detected plugin content in delta: {content[:150]}...")
                    
                    # Try to extract plugin tool output using same logic as HTTP fallback
                    try:
                        if '"tool_output_content"' in content:
                            # Extract tool_output_content directly
                            import re
                            match = re.search(r'"tool_output_content":"([^"]+)"', content)
                            if match:
                                tool_output = match.group(1).replace('\\n', '\n').replace('\\"', '"')
                                print(f"✅ Extracted tool_output_content: {tool_output[:100]}...")
                                plugin_responses.append(tool_output)
                                continue  # Skip adding to response_content to avoid duplication
                        
                        # Handle stream_plugin_finish format  
                        if '"msg_type":"stream_plugin_finish"' in content:
                            try:
                                import json
                                plugin_data = json.loads(content)
                                data_content = plugin_data.get('data', {})
                                if isinstance(data_content, str):
                                    # Parse nested JSON in data field
                                    try:
                                        data_obj = json.loads(data_content)
                                        tool_output = data_obj.get('tool_output_content', '')
                                        if tool_output and len(tool_output.strip()) > 5:
                                            print(f"✅ Extracted from stream_plugin_finish: {tool_output[:100]}...")
                                            plugin_responses.append(tool_output)
                                            continue
                                    except:
                                        pass
                                elif isinstance(data_content, dict):
                                    tool_output = data_content.get('tool_output_content', '')
                                    if tool_output and len(tool_output.strip()) > 5:
                                        print(f"✅ Extracted from nested JSON: {tool_output[:100]}...")
                                        plugin_responses.append(tool_output)
                                        continue
                            except json.JSONDecodeError:
                                print(f"⚠️ Failed to parse stream_plugin_finish JSON")
                        
                        # Try to parse as plugin invocation JSON
                        if '"plugin_id"' in content:
                            try:
                                import json
                                plugin_data = json.loads(content)
                                
                                # Look for tool output in various possible fields
                                tool_output_fields = [
                                    'tool_output_content', 'output', 'result', 
                                    'content', 'answer', 'response'
                                ]
                                
                                for field in tool_output_fields:
                                    if field in plugin_data and plugin_data[field]:
                                        tool_output = str(plugin_data[field])
                                        if len(tool_output.strip()) > 10:
                                            print(f"✅ Extracted plugin output from {field}: {tool_output[:100]}...")
                                            plugin_responses.append(tool_output)
                                            break
                                
                                # Also check in arguments field
                                if 'arguments' in plugin_data and isinstance(plugin_data['arguments'], dict):
                                    args = plugin_data['arguments']
                                    for field in tool_output_fields:
                                        if field in args and args[field]:
                                            tool_output = str(args[field])
                                            if len(tool_output.strip()) > 10:
                                                print(f"✅ Extracted tool output from args.{field}: {tool_output[:100]}...")
                                                plugin_responses.append(tool_output)
                                                break
                                continue  # Skip adding plugin JSON to response_content
                            except json.JSONDecodeError:
                                print(f"⚠️ Failed to parse plugin JSON")
                    
                    except Exception as e:
                        print(f"⚠️ Error processing plugin content: {e}")
                
                # Only add to collected content if it's not plugin invocation JSON
                if not ('"plugin_id"' in content and content.strip().startswith('{')):
                    collected_content += content
                    response_content += content
                
            # Handle direct plugin results (if SDK supports these attributes)
            elif hasattr(event, 'plugin_result') and event.plugin_result:
                plugin_content = str(event.plugin_result)
                response_content += f"\n{plugin_content}"
                plugin_responses.append(plugin_content)
                print(f"[🔌 PLUGIN RESULT] {plugin_content[:100]}...")
                
            # Handle tool outputs (alternative event type for plugins)
            elif hasattr(event, 'tool_output') and event.tool_output:
                tool_content = str(event.tool_output)
                response_content += f"\n{tool_content}"
                plugin_responses.append(tool_content)
                print(f"[🔧 TOOL OUTPUT] {tool_content[:100]}...")
                
            # Handle any other message content (fallback for other content types)
            elif hasattr(event, 'message') and hasattr(event.message, 'content') and event.message.content:
                if event.event != ChatEventType.CONVERSATION_MESSAGE_DELTA:  # Avoid duplicates
                    content = event.message.content
                    response_content += content
                    print(f"[📄 OTHER MESSAGE] {content[:100]}...")
                    
            elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                if hasattr(event.chat, 'usage') and event.chat.usage:
                    token_count = event.chat.usage.token_count
                print(f"[✅ CHAT COMPLETED] Token count: {token_count}")
                break
                
            # Log any unhandled events for debugging
            else:
                print(f"[❓ UNHANDLED EVENT] {event.event} - {type(event)}")
                # Try to extract any content from unknown event types
                if hasattr(event, 'content'):
                    content = str(event.content)
                    response_content += f"\n{content}"
                    print(f"[❓ UNKNOWN CONTENT] {content[:100]}...")
        
        # 🔧 Priority order for response content with plugin support (same as HTTP fallback)
        # 1. Plugin responses (highest priority for technical queries)
        if plugin_responses:
            # Use the longest/most substantial plugin response
            best_plugin_response = max(plugin_responses, key=len)
            if len(best_plugin_response) > 20:
                print(f"✅ Using plugin response ({len(best_plugin_response)} chars)")
                response_content = best_plugin_response
            
        # Apply the same cleaning as the HTTP fallback
        if response_content:
            response_content = clean_ai_response(response_content)
        
        if not response_content.strip():
            raise Exception("Empty response from Coze SDK")
            
        print(f"✅ SDK调用成功，响应长度: {len(response_content)}, Token: {token_count}")
        return response_content.strip()
        
    except Exception as e:
        print(f"❌ Coze SDK调用失败: {str(e)}")
        print("🔄 切换到HTTP fallback")
        return await call_coze_api_fallback(message, bot_id)

async def call_coze_api(bot_id: str, message: str) -> str:
    """
    Main Coze API call function - tries SDK first, then fallback
    """
    return await call_coze_api_sdk(bot_id, message)

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
    Generate enhanced recommendations based on evaluation results and user persona
    """
    recommendations = []
    
    if not evaluation_results:
        return [
            "无法生成推荐建议，请先完成有效的评估",
            "检查AI Agent配置和网络连接",
            "确保对话场景配置正确"
        ]
    
    persona = user_persona_info.get('user_persona', {}) if user_persona_info else {}
    context = user_persona_info.get('usage_context', {}) if user_persona_info else {}
    requirements = user_persona_info.get('extracted_requirements', {}) if user_persona_info else {}
    
    # Calculate dimension averages from evaluation results
    all_scores = {}
    for result in evaluation_results:
        scores = result.get("evaluation_scores", {})
        for dimension, score in scores.items():
            if dimension not in all_scores:
                all_scores[dimension] = []
            all_scores[dimension].append(score)
    
    dimension_averages = {}
    for dimension, scores in all_scores.items():
        dimension_averages[dimension] = sum(scores) / len(scores) if scores else 0
    
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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Simple health check endpoint for debugging"""
    try:
        memory_usage = check_memory_usage()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "memory_usage": memory_usage,
            "version": "4.0.0",
            "features": {
                "database": PYMYSQL_AVAILABLE,
                "coze_sdk": COZE_SDK_AVAILABLE,
                "document_processing": DOCUMENT_PROCESSING_AVAILABLE,
                "memory_monitoring": PSUTIL_AVAILABLE
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

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
            # ⭐ Security: Validate input length
            if len(agent_api_config) > 50000:  # 50KB limit
                raise HTTPException(status_code=413, detail="API配置过长，请检查配置内容")
            
            api_config_dict = json.loads(agent_api_config)
            
            # ⭐ Security: Validate API URL if present
            if 'url' in api_config_dict and not validate_api_url(api_config_dict['url']):
                raise HTTPException(status_code=400, detail="不安全的API URL")
            
            # Debug: log the received configuration structure
            print(f"🔍 Received API config structure: {json.dumps(api_config_dict, indent=2)}")
            logger.info(f"🔍 Received API config: {api_config_dict}")
            
            # Enhanced data cleaning for common frontend issues
            if isinstance(api_config_dict, dict):
                # Strategy 1: Look for common wrapping patterns
                if 'config' in api_config_dict and isinstance(api_config_dict['config'], dict):
                    print("⚠️ Detected config wrapped in 'config' key, unwrapping...")
                    api_config_dict = api_config_dict['config']
                elif 'api_config' in api_config_dict and isinstance(api_config_dict['api_config'], dict):
                    print("⚠️ Detected config wrapped in 'api_config' key, unwrapping...")
                    api_config_dict = api_config_dict['api_config']
                
                # Strategy 2: Fix the nested headers issue (common user error)
                if 'headers' in api_config_dict and isinstance(api_config_dict['headers'], dict):
                    headers = api_config_dict['headers']
                    
                    # Check if user pasted entire config into headers field
                    if 'url' in headers and 'method' in headers and 'type' in headers:
                        print("⚠️ Detected full config pasted in headers field, extracting...")
                        # The real config is nested in headers, extract it
                        real_config = headers.copy()
                        
                        # Clean the nested headers if it exists
                        if 'headers' in real_config and isinstance(real_config['headers'], dict):
                            real_config['headers'] = real_config['headers']
                        else:
                            real_config['headers'] = {'Content-Type': 'application/json'}
                        
                        api_config_dict = real_config
                        print(f"✅ Extracted real config from nested headers: {api_config_dict['type']}")
                    
                    # Check for duplicate nested structure in headers
                    elif any(key in headers for key in ['type', 'url', 'method', 'timeout']):
                        print("⚠️ Detected config properties mixed in headers, cleaning...")
                        # Extract only valid header properties
                        valid_headers = {}
                        for key, value in headers.items():
                            if key.lower() in ['authorization', 'content-type', 'user-agent', 'accept', 'x-api-key']:
                                valid_headers[key] = value
                        
                        # If no valid headers found, use default
                        if not valid_headers:
                            valid_headers = {'Content-Type': 'application/json'}
                        
                        api_config_dict['headers'] = valid_headers
                        print(f"✅ Cleaned headers: {valid_headers}")
                
                # Strategy 3: Ensure required fields and proper data types
                if 'timeout' in api_config_dict:
                    try:
                        api_config_dict['timeout'] = int(api_config_dict['timeout'])
                    except (ValueError, TypeError):
                        api_config_dict['timeout'] = 30
                        print("⚠️ Invalid timeout value, defaulting to 30 seconds")
                
                # Ensure headers is a dictionary
                if 'headers' not in api_config_dict or not isinstance(api_config_dict['headers'], dict):
                    print(f"⚠️ Missing or invalid headers, setting default")
                    api_config_dict['headers'] = {'Content-Type': 'application/json'}
                
                # Strategy 4: Validate required fields based on type
                config_type = api_config_dict.get('type', '')
                if config_type == 'custom-api':
                    if 'url' not in api_config_dict:
                        raise ValueError("Custom API configuration missing required 'url' field")
                    if 'method' not in api_config_dict:
                        api_config_dict['method'] = 'POST'
                        print("⚠️ Missing method, defaulting to POST")
                elif config_type in ['coze-agent', 'coze-bot']:
                    if 'url' not in api_config_dict:
                        # Set default Coze URL based on type
                        if config_type == 'coze-agent':
                            api_config_dict['url'] = 'https://api.coze.cn/open_api/v2/chat'
                        else:
                            api_config_dict['url'] = 'https://api.coze.cn/open_api/v2/chat'
                        print(f"⚠️ Missing URL for {config_type}, using default")
            
            print(f"🔧 Cleaned API config: {json.dumps(api_config_dict, indent=2)}")
            
            api_config = APIConfig(**api_config_dict)
            logger.info(f"✅ API config parsed successfully: {api_config.type}")
        except json.JSONDecodeError as je:
            error_msg = f"JSON格式错误: {str(je)}"
            logger.error(f"❌ JSON parsing failed: {error_msg}")
            logger.error(f"❌ Original config string: {agent_api_config}")
            raise HTTPException(status_code=400, detail=f"API配置JSON格式错误: {error_msg}")
        except ValueError as ve:
            error_msg = str(ve)
            logger.error(f"❌ Config validation failed: {error_msg}")
            logger.error(f"❌ Original config string: {agent_api_config}")
            raise HTTPException(status_code=400, detail=f"API配置验证失败: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ API config parsing failed: {error_msg}")
            logger.error(f"❌ Original config string: {agent_api_config}")
            raise HTTPException(status_code=400, detail=f"API配置解析失败: {error_msg}")
        
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
            # ⭐ Security: Sanitize user input
            requirement_context = sanitize_user_input(requirement_text, max_length=100000)
        
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
    extracted_persona: str = Form(None),  # JSON string of extracted persona
    use_raw_messages: bool = Form(False)  # Use raw user messages without persona enhancement
):
    """
    New dynamic evaluation endpoint implementing conversational workflow:
    1. Extract persona from document
    2. Generate 2 scenarios with dynamic conversations
    3. Conduct 2-3 rounds per scenario based on AI responses
    4. Generate comprehensive final report
    """
    # Add timeout protection for the entire evaluation (increased to 10 minutes)
    evaluation_timeout = 600  # 10 minutes total timeout
    
    # Check memory usage before starting evaluation
    memory_usage = check_memory_usage()
    if memory_usage and memory_usage > config.MEMORY_WARNING_THRESHOLD:
        logger.warning(f"⚠️ High memory usage detected: {memory_usage:.1f}%")
    
    try:
        # Wrap the entire evaluation in a timeout
        evaluation_result = await asyncio.wait_for(
            _perform_dynamic_evaluation_internal(
                agent_api_config, requirement_file, requirement_text, extracted_persona, use_raw_messages
            ),
            timeout=evaluation_timeout
        )
        return evaluation_result
        
    except asyncio.TimeoutError:
        logger.error(f"⏰ Dynamic evaluation timed out after {evaluation_timeout} seconds")
        raise HTTPException(
            status_code=408, 
            detail=f"评估超时：评估过程超过{evaluation_timeout//60}分钟限制。建议：1) 检查网络连接，2) 简化需求文档内容，3) 确认AI Agent响应速度正常，4) 重新启动服务器释放内存。"
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any other unexpected exceptions
        logger.error(f"❌ Unexpected error in dynamic evaluation: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"动态评估过程出现意外错误: {str(e)}. 请检查服务器日志获取详细信息。"
        )

async def _perform_dynamic_evaluation_internal(
    agent_api_config: str,
    requirement_file: UploadFile,
    requirement_text: str,
    extracted_persona: str,
    use_raw_messages: bool = False
) -> Dict:
    """
    Internal function to perform dynamic evaluation with proper error handling
    """
    try:
        logger.info("🚀 Starting dynamic evaluation...")
        print("🚀============================================================🚀")
        print("   AI Agent 动态对话评估平台 v4.0")
        print(f"🔍 消息处理模式: {'原始消息模式 (RAW)' if use_raw_messages else '增强消息模式 (ENHANCED)'}")
        print("🚀============================================================🚀")
        
        # Parse API configuration
        try:
            # ⭐ Security: Validate input length
            if len(agent_api_config) > 50000:  # 50KB limit
                raise HTTPException(status_code=413, detail="API配置过长，请检查配置内容")
            
            api_config_dict = json.loads(agent_api_config)
            
            # ⭐ Security: Validate API URL if present
            if 'url' in api_config_dict and not validate_api_url(api_config_dict['url']):
                raise HTTPException(status_code=400, detail="不安全的API URL")
            
            # Debug: log the received configuration structure
            print(f"🔍 Received API config structure: {json.dumps(api_config_dict, indent=2)}")
            logger.info(f"🔍 Received API config: {api_config_dict}")
            
            # Check if the config is wrapped in an extra layer (common frontend issue)
            if isinstance(api_config_dict, dict):
                # Look for common wrapping patterns
                if 'config' in api_config_dict and isinstance(api_config_dict['config'], dict):
                    print("⚠️ Detected config wrapped in 'config' key, unwrapping...")
                    api_config_dict = api_config_dict['config']
                elif 'headers' in api_config_dict and 'url' in api_config_dict.get('headers', {}):
                    print("⚠️ Detected config wrapped in 'headers' key, unwrapping...")
                    api_config_dict = api_config_dict['headers']
                elif 'api_config' in api_config_dict and isinstance(api_config_dict['api_config'], dict):
                    print("⚠️ Detected config wrapped in 'api_config' key, unwrapping...")
                    api_config_dict = api_config_dict['api_config']
            
            # Additional data cleaning for common frontend issues
            if isinstance(api_config_dict, dict):
                # Ensure timeout is an integer
                if 'timeout' in api_config_dict:
                    try:
                        api_config_dict['timeout'] = int(api_config_dict['timeout'])
                    except (ValueError, TypeError):
                        api_config_dict['timeout'] = 30
                
                # Ensure headers is a dictionary
                if 'headers' in api_config_dict and not isinstance(api_config_dict['headers'], dict):
                    print(f"⚠️ Invalid headers format: {type(api_config_dict['headers'])}, resetting to empty dict")
                    api_config_dict['headers'] = {}
            
            print(f"🔧 Cleaned API config: {json.dumps(api_config_dict, indent=2)}")
            
            api_config = APIConfig(**api_config_dict)
            logger.info(f"✅ API config parsed successfully: {api_config.type}")
        except Exception as e:
            logger.error(f"❌ API config parsing failed: {str(e)}")
            logger.error(f"❌ Original config string: {agent_api_config}")
            raise HTTPException(status_code=400, detail=f"API配置解析失败: {str(e)}")
        
        # Handle requirement document
        requirement_context = ""
        user_persona_info = None
        
        # Step 1: Process requirement document and extract persona
        try:
            # ⭐ Memory check before document processing
            memory_usage = check_memory_usage()
            if memory_usage > config.MEMORY_CRITICAL_THRESHOLD:
                raise HTTPException(status_code=507, detail=f"内存不足 ({memory_usage:.1f}%)")
            
            if requirement_file and requirement_file.filename:
                logger.info(f"📄 Processing uploaded file: {requirement_file.filename}")
                print(f"📄 Processing uploaded file: {requirement_file.filename}")
                requirement_context = await process_uploaded_document_improved(requirement_file)
            elif requirement_text:
                logger.info("📝 Using provided text content")
                # ⭐ Security: Sanitize user input
                requirement_context = sanitize_user_input(requirement_text, max_length=100000)
            
            if not requirement_context:
                raise HTTPException(status_code=400, detail="请提供需求文档或文本内容")
                
            logger.info(f"✅ Document processed, length: {len(requirement_context)} characters")
        except Exception as e:
            logger.error(f"❌ Document processing failed: {str(e)}")
            raise HTTPException(status_code=400, detail=f"文档处理失败: {str(e)}")
        
        # Step 2: Extract user persona from requirement document using DeepSeek
        try:
            if extracted_persona:
                try:
                    user_persona_info = json.loads(extracted_persona)
                    logger.info(f"🎭 Using provided persona: {user_persona_info.get('user_persona', {}).get('role', '未知角色')}")
                    print(f"🎭 使用提取的用户画像: {user_persona_info.get('user_persona', {}).get('role', '未知角色')}")
                except Exception as pe:
                    logger.warning(f"⚠️ Persona parsing failed: {str(pe)}")
                    print("⚠️ 画像数据解析失败，重新提取...")
                    user_persona_info = None
            
            if not user_persona_info:
                logger.info("🧠 Extracting user persona from document...")
                print("🧠 从需求文档中提取用户画像...")
                user_persona_info = await extract_user_persona_with_deepseek(requirement_context)
                if not user_persona_info:
                    raise HTTPException(status_code=400, detail="无法从需求文档中提取有效的用户画像信息")
                    
            logger.info("✅ User persona extracted successfully")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Persona extraction failed: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"用户画像提取失败: {str(e)}")
        
        # Step 3: Conduct dynamic multi-scenario evaluation
        try:
            # ⭐ Memory check before evaluation
            memory_usage = check_memory_usage()
            if memory_usage > config.MEMORY_CRITICAL_THRESHOLD:
                raise HTTPException(status_code=507, detail=f"内存不足 ({memory_usage:.1f}%)")
            
            logger.info("🎯 Starting dynamic conversation evaluation...")
            print("🎯 开始动态多轮对话评估...")
            evaluation_results = await conduct_dynamic_multi_scenario_evaluation(
                api_config, user_persona_info, requirement_context, use_raw_messages
            )
            
            if not evaluation_results:
                raise HTTPException(status_code=500, detail="动态对话评估失败，请检查AI Agent配置")
                
            logger.info(f"✅ Evaluation completed with {len(evaluation_results)} scenarios")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Evaluation failed: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"动态对话评估失败: {str(e)}")
        
        # Step 4: Generate comprehensive final report
        try:
            logger.info("📊 Generating comprehensive report...")
            print("📊 生成综合评估报告...")
            comprehensive_report = await generate_final_comprehensive_report(
                evaluation_results, user_persona_info, requirement_context
            )
            logger.info("✅ Report generated successfully")
        except Exception as e:
            logger.error(f"❌ Report generation failed: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Use fallback report generation
            comprehensive_report = {
                "improvement_recommendations": ["系统建议：加强对话理解能力", "系统建议：提高回答准确性"],
                "extracted_persona_summary": user_persona_info,
                "persona_alignment_analysis": "基于系统分析生成",
                "business_goal_achievement": "评估完成"
            }
        
        # Calculate overall summary
        try:
            # Calculate from scenario scores (which are now in 5-point scale)
            overall_score_5 = sum(r.get('scenario_score', 0) for r in evaluation_results) / len(evaluation_results) if evaluation_results else 0
            overall_score_100 = sum(r.get('scenario_score_100', 0) for r in evaluation_results) / len(evaluation_results) if evaluation_results else 0
            total_conversations = sum(len(r.get('conversation_history', [])) for r in evaluation_results)
            
            # Generate comprehensive evaluation summary  
            evaluation_summary = generate_evaluation_summary(evaluation_results, requirement_context)
            
            response_data = {
                "evaluation_summary": {
                    "overall_score": round(overall_score_5, 2),  # Keep for compatibility
                    "overall_score_100": round(overall_score_100, 2),  # Primary 100-point scale
                    "total_scenarios": len(evaluation_results),
                    "total_conversations": total_conversations,
                    "framework": "动态多轮对话评估 (100分制)",
                    "dimension_scores_100": evaluation_summary.get("dimensions_100", {}),
                    "dimension_scores": evaluation_summary.get("dimensions", {}),  # Keep for compatibility
                    "comprehensive_analysis": comprehensive_report,
                    "extracted_persona_display": {
                        "user_role": user_persona_info.get('user_persona', {}).get('role', '专业用户'),
                        "business_domain": user_persona_info.get('usage_context', {}).get('business_domain', '专业服务'),
                        "experience_level": user_persona_info.get('user_persona', {}).get('experience_level', '中等经验'),
                        "communication_style": user_persona_info.get('user_persona', {}).get('communication_style', '专业沟通'),
                        "work_environment": user_persona_info.get('user_persona', {}).get('work_environment', '专业工作环境'),
                        "primary_scenarios": user_persona_info.get('usage_context', {}).get('primary_scenarios', ['专业咨询']),
                        "pain_points": user_persona_info.get('usage_context', {}).get('pain_points', ['信息获取']),
                        "core_functions": user_persona_info.get('extracted_requirements', {}).get('core_functions', ['信息查询']),
                        "quality_expectations": user_persona_info.get('extracted_requirements', {}).get('quality_expectations', ['准确性']),
                        "extraction_method": "DeepSeek智能提取分析",
                        "document_length": len(requirement_context) if requirement_context else 0
                    },
                    "scoring_system": {
                        "scale": "0-100分制",
                        "grade_levels": {
                            "90-100": "优秀 (Excellent)",
                            "80-89": "良好 (Good)", 
                            "70-79": "中等 (Average)",
                            "60-69": "及格 (Pass)",
                            "50-59": "不及格 (Below Pass)",
                            "0-49": "需要改进 (Needs Improvement)"
                        }
                    }
                },
                "conversation_records": evaluation_results,
                "recommendations": comprehensive_report.get('improvement_recommendations', []),
                "extracted_persona_full": comprehensive_report.get('extracted_persona_summary', {}),
                "persona_alignment_analysis": comprehensive_report.get('persona_alignment_analysis', ''),
                "business_goal_achievement": comprehensive_report.get('business_goal_achievement', ''),
                "detailed_context_display": {
                    "requirement_document_summary": {
                        "content_length": len(requirement_context) if requirement_context else 0,
                        "content_preview": requirement_context[:500] + "..." if requirement_context and len(requirement_context) > 500 else requirement_context,
                        "analysis_basis": "基于上传的需求文档进行AI智能分析"
                    },
                    "evaluation_methodology": {
                        "conversation_generation": "DeepSeek动态生成对话场景",
                        "response_evaluation": "多维度100分制评估",
                        "persona_matching": "基于文档提取的用户画像进行个性化测试"
                    },
                    "technical_details": {
                        "api_type": "Dify API" if "/v1/chat-messages" in api_config.url else "Coze API" if "coze" in api_config.url.lower() else "自定义API",
                        "conversation_turns": total_conversations,
                        "evaluation_dimensions": len(evaluation_results[0].get('evaluation_scores', {})) if evaluation_results else 3
                    }
                },
                "evaluation_mode": "dynamic",
                "user_persona_info": user_persona_info,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"🎯 Dynamic evaluation completed successfully! Score: {overall_score_100:.2f}/100.0")
            print(f"🎯 动态评估完成！综合得分: {overall_score_100:.2f}/100.0")
            print(f"📊 评估场景: {len(evaluation_results)} 个")
            print(f"💬 对话轮次: {total_conversations} 轮")
            print(f"🎭 用户画像: {user_persona_info.get('user_persona', {}).get('role', '未知角色')}")
            
            # Monitor response size and optimize if needed
            import json
            import sys
            response_json = json.dumps(response_data, ensure_ascii=False, default=str)
            response_size_mb = sys.getsizeof(response_json) / (1024 * 1024)
            
            logger.info(f"📊 Response size: {response_size_mb:.2f} MB")
            print(f"📊 Response size: {response_size_mb:.2f} MB")
            
            # If response is too large (>50MB), optimize it
            if response_size_mb > 50:
                logger.warning(f"⚠️ Large response detected ({response_size_mb:.2f} MB), optimizing...")
                print(f"⚠️ Large response detected ({response_size_mb:.2f} MB), optimizing...")
                
                # Reduce conversation history verbosity for large responses
                for record in response_data.get("conversation_records", []):
                    for turn in record.get("conversation_history", []):
                        # Truncate very long AI responses
                        if len(turn.get("ai_response", "")) > 5000:
                            turn["ai_response"] = turn["ai_response"][:5000] + "\n...[响应已截断，完整内容请查看详细报告]"
                        
                        # Truncate very long evaluation explanations
                        for key, value in record.get("evaluation_scores_with_explanations", {}).items():
                            if isinstance(value, dict) and len(str(value.get("detailed_analysis", ""))) > 2000:
                                value["detailed_analysis"] = str(value["detailed_analysis"])[:2000] + "...[详细分析已截断]"
            
            # Store the response before attempting database save
            final_response = response_data.copy()
            
            # Auto-save to database if enabled (non-blocking)
            if config.ENABLE_AUTO_SAVE:
                try:
                    # Use asyncio.create_task to make database save non-blocking
                    async def save_to_db():
                        try:
                            session_id = await save_evaluation_to_database(response_data, requirement_context)
                            if session_id:
                                print(f"💾 评估结果已自动保存到数据库，会话ID: {session_id}")
                            else:
                                print("⚠️ 数据库自动保存失败，但评估结果仍然可用")
                        except Exception as e:
                            print(f"⚠️ 数据库保存异常，但不影响评估结果: {str(e)}")
                    
                    # Create background task for database save
                    asyncio.create_task(save_to_db())
                    
                    # Attempt quick database save with timeout
                    try:
                        session_id = await asyncio.wait_for(
                            save_evaluation_to_database(response_data, requirement_context),
                            timeout=5.0  # 5 second timeout for database save
                        )
                        if session_id:
                            final_response["database_session_id"] = session_id
                            print(f"💾 评估结果已自动保存到数据库，会话ID: {session_id}")
                    except asyncio.TimeoutError:
                        print("⚠️ 数据库保存超时，已创建后台任务继续保存")
                    except Exception as e:
                        print(f"⚠️ 数据库保存异常，但不影响评估结果: {str(e)}")
                        
                except Exception as e:
                    print(f"⚠️ 数据库保存模块异常: {str(e)}")
            
            # Final response validation and optimization
            try:
                # Ensure the response can be JSON serialized
                test_json = json.dumps(final_response, ensure_ascii=False, default=str)
                final_size_mb = sys.getsizeof(test_json) / (1024 * 1024)
                logger.info(f"✅ Final response ready: {final_size_mb:.2f} MB")
                print(f"✅ Final response ready: {final_size_mb:.2f} MB")
                
                # Add response metadata
                final_response["response_metadata"] = {
                    "size_mb": round(final_size_mb, 2),
                    "generation_time": datetime.now().isoformat(),
                    "optimized": response_size_mb > 50,
                    "version": "4.0"
                }
                
                return final_response
                
            except Exception as json_error:
                logger.error(f"❌ Response serialization failed: {str(json_error)}")
                print(f"❌ Response serialization failed: {str(json_error)}")
                
                # Return a minimal response if serialization fails
                return {
                    "evaluation_summary": {
                        "overall_score_100": round(overall_score_100, 2),
                        "total_scenarios": len(evaluation_results),
                        "error": "Full response too large, providing summary only"
                    },
                    "conversation_records": [],
                    "recommendations": ["系统建议：响应过大，请查看详细报告"],
                    "timestamp": datetime.now().isoformat(),
                    "error_info": "Response optimization failed"
                }
            
        except Exception as e:
            logger.error(f"❌ Response data assembly failed: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"响应数据组装失败: {str(e)}")
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any other unexpected exceptions
        logger.error(f"❌ Unexpected error in dynamic evaluation: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"动态评估过程出现意外错误: {str(e)}. 请检查服务器日志获取详细信息。"
        )

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
            "evaluation_scores_with_explanations": explanations,  # Add detailed explanations
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
    Generate evaluation summary from results - 100-point scale normalized
    """
    if not evaluation_results:
        return {
            "overall_score_100": 0.0,
            "overall_score": 0.0,  # Keep for compatibility
            "total_scenarios": 0,
            "total_conversations": 0,
            "framework": "AI Agent 4维度评估框架 (100分制)",
            "dimensions_100": {},
            "dimensions": {}  # Keep for compatibility
        }
        
    # Calculate dimension averages from 100-point scores
    all_scores_100 = {}
    total_conversations = 0
    
    for result in evaluation_results:
        # Use scenario_score_100 if available, fallback to converted scores
        scenario_score_100 = result.get("scenario_score_100", 0)
        if scenario_score_100 == 0:
            # Convert from 5-point scale if needed
            scenario_score_5 = result.get("scenario_score", 0)
            scenario_score_100 = scenario_score_5 * 20 if scenario_score_5 <= 5 else scenario_score_5
        
        scores = result.get("evaluation_scores", {})
        conversation_history = result.get("conversation_history", [])
        total_conversations += len(conversation_history)
        
        for dimension, score in scores.items():
            if dimension not in all_scores_100:
                all_scores_100[dimension] = []
            # Ensure score is in 100-point scale
            normalized_score = score * 20 if score <= 5 else score
            all_scores_100[dimension].append(normalized_score)
    
    # Calculate averages in 100-point scale
    dimension_averages_100 = {}
    dimension_averages_5 = {}  # For compatibility
    for dimension, scores in all_scores_100.items():
        avg_100 = sum(scores) / len(scores) if scores else 0
        dimension_averages_100[dimension] = round(avg_100, 2)
        dimension_averages_5[dimension] = round(avg_100 / 20, 2)  # For compatibility
    
    overall_score_100 = sum(dimension_averages_100.values()) / len(dimension_averages_100) if dimension_averages_100 else 0
    overall_score_5 = overall_score_100 / 20  # For compatibility
    
    return {
        "overall_score_100": round(overall_score_100, 2),
        "overall_score": round(overall_score_5, 2),  # Keep for compatibility
        "total_scenarios": len(evaluation_results),
        "total_conversations": total_conversations,
        "framework": "AI Agent 4维度评估框架 (100分制)",
        "dimensions_100": dimension_averages_100,
        "dimensions": dimension_averages_5  # Keep for compatibility
    }

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
    """
    Enhanced DeepSeek API call with config-based settings and proper error handling
    """
    headers = {
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800,
        "temperature": config.ENHANCED_TEMPERATURE
    }
    
    for attempt in range(max_retries):
        try:
            timeout = httpx.Timeout(config.DEEPSEEK_TIMEOUT, connect=10.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(config.DEEPSEEK_API_URL, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        content = result["choices"][0]["message"]["content"].strip()
                        if content and len(content) > 10:
                            return content
                        else:
                            raise Exception("DeepSeek returned empty or too short response")
                    else:
                        raise Exception("No valid choices in DeepSeek response")
                elif response.status_code == 401:
                    raise Exception("API authentication failed - check API key")
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise Exception("API rate limited")
                else:
                    error_text = response.text if hasattr(response, 'text') else 'Unknown error'
                    raise Exception(f"API error {response.status_code}: {error_text}")
                    
        except (asyncio.TimeoutError, httpx.TimeoutException):
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            raise Exception(f"API timeout after {config.DEEPSEEK_TIMEOUT}s")
        except httpx.RequestError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            if "empty" in str(e) or "short" in str(e):
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
            raise e
            
    raise Exception("All API attempts failed")

# Create alias function to redirect to new implementation
async def conduct_dynamic_conversation(api_config: APIConfig, scenario_info: Dict, user_persona_info: Dict) -> List[Dict]:
    """Redirect to true dynamic conversation implementation"""
    return await conduct_true_dynamic_conversation(api_config, scenario_info, user_persona_info)

async def conduct_true_dynamic_conversation(api_config: APIConfig, scenario_info: Dict, user_persona_info: Dict, use_raw_messages: bool = False) -> List[Dict]:
    """
    TRUE dynamic conversation: Correct flow implementation
    
    Flow: 
    1. DeepSeek generates user message based on persona → 
    2. Send RAW message to Coze (no enhancement) → 
    3. Extract Coze's actual response → 
    4. Pass Coze response to DeepSeek for next message generation
    
    Args:
        use_raw_messages: Legacy parameter (always uses raw messages now)
    """
    print(f"🗣️ 开始真正动态对话: {scenario_info.get('title', '未命名场景')}")
    print("🔄 正确流程: DeepSeek(基于画像生成消息) → 原始消息 → Coze → 响应 → DeepSeek(分析响应生成下轮)")
    
    conversation_history = []
    persona = user_persona_info.get('user_persona', {})
    context = user_persona_info.get('usage_context', {})
    
    # Initialize conversation manager for continuity
    conversation_manager = ConversationManager(api_config)
    conversation_manager.start_new_conversation()
    
    # Step 1: Generate ONLY the initial message based on persona and scenario
    try:
        initial_message = await generate_single_initial_message(scenario_info, user_persona_info)
        if not initial_message:
            raise Exception("Failed to generate initial message")
    except Exception as e:
        print(f"❌ 初始消息生成失败: {str(e)}")
        raise Exception(f"Dynamic conversation initialization failed: {str(e)}")
    
    current_user_message = initial_message
    failed_turns = 0  # Track failed turns
    
    # Step 2: Conduct true turn-by-turn conversation (optimized to 2-3 turns max)
    for turn_num in range(1, 4):  # Maximum 3 turns
        try:
            # 🐛 Debug log for message processing - ALWAYS use raw messages in dynamic conversation
            print(f"🔍 [TURN {turn_num}] DeepSeek生成的原始用户消息: {current_user_message}")
            
            # ALWAYS send raw user message to Coze (no persona enhancement in dynamic mode)
            # This is the correct flow: DeepSeek(persona) → raw message → Coze → response → DeepSeek(analyze)
            message_to_send = current_user_message
            print(f"🔍 [RAW MESSAGE] 发送原始消息到Coze: {message_to_send}")
            
            # Get AI response with timeout and conversation continuity
            ai_response = await call_coze_with_strict_timeout(api_config, message_to_send, conversation_manager, True)
            
            if not ai_response or len(ai_response.strip()) < 5:
                print(f"⚠️ 第{turn_num}轮AI响应为空或过短，可能是API问题")
                failed_turns += 1
                if failed_turns >= 2:  # Stop if too many failed turns
                    print("❌ 连续多轮API响应失败，可能是API配置或账户问题，请检查API密钥和账户余额")
                    break
                continue
            
            # Clean the AI response to extract meaningful content
            cleaned_response = clean_ai_response(ai_response)
            
            # If cleaned response is empty (system message), try to generate a fallback response
            if not cleaned_response:
                try:
                    fallback_prompt = f"""
作为一个专业的{user_persona_info.get('user_persona', {}).get('role', '助手')}，请对以下问题给出简短但有用的回复：

用户问题：{current_user_message}
回复要求：
1. 直接回答问题，不要说"我不知道"
2. 保持专业但友好的语调
3. 如果需要更多信息，可以简单询问
4. 回复控制在50字以内

请直接给出回复：
"""
                    
                    fallback_response = await call_deepseek_api_enhanced(fallback_prompt, temperature=0.3, max_tokens=100)
                    if fallback_response and len(fallback_response.strip()) > 5:
                        cleaned_response = fallback_response.strip()
                        failed_turns = 0  # Reset since we got a response
                    else:
                        failed_turns += 1
                        if failed_turns >= 2:
                            break
                        continue
                except Exception as e:
                    failed_turns += 1
                    if failed_turns >= 2:
                        break
                    continue
            
            # Reset failed turn counter on successful turn
            failed_turns = 0
            
            # Record this turn
            conversation_history.append({
                "turn": turn_num,
                "user_message": current_user_message,  # Raw message generated by DeepSeek
                "message_sent_to_ai": message_to_send,  # Same as user_message (always raw)
                "ai_response": cleaned_response,        # Actual Coze response
                "response_length": len(cleaned_response),
                "conversation_id": conversation_manager.get_conversation_id(),
                "flow_type": "deepseek_to_raw_to_coze",  # Indicate the correct flow
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ 第 {turn_num} 轮对话完成")
            
            # Generate next message based on AI's actual response (only if not the last turn)
            if turn_num < 3:  # Don't generate after last turn
                try:
                    next_message = await generate_next_message_based_on_response(
                        scenario_info, user_persona_info, conversation_history, cleaned_response
                    )
                    
                    if not next_message or next_message.upper() in ["END", "FINISH", "DONE"]:
                        print(f"🔚 对话自然结束于第 {turn_num} 轮")
                        break
                        
                    current_user_message = next_message
                    
                except Exception as e:
                    print(f"❌ 第{turn_num + 1}轮消息生成失败: {str(e)}")
                    break  # End conversation if next message generation fails
            
        except Exception as e:
            print(f"❌ 第 {turn_num} 轮对话异常: {str(e)}")
            failed_turns += 1
            if failed_turns >= 2:
                break
            continue
    
    if not conversation_history:
        raise Exception("Dynamic conversation completely failed - no successful turns")
    
    print(f"📊 真实动态对话完成，共 {len(conversation_history)} 轮")
    print(f"✅ 实现流程: DeepSeek(画像生成) → 原始消息 → Coze → 实际回复 → DeepSeek(分析回复)")
    return conversation_history

# DeepSeek Configuration

async def call_deepseek_api_enhanced(prompt: str, max_tokens: int = 500, temperature: float = 0.1, max_retries: int = 2) -> str:
    """
    Enhanced DeepSeek API call with better configuration and error handling
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.9,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    }
    
    # Single attempt - fail fast if there are issues
    try:
        # Increased timeout and added better error handling
        timeout = httpx.Timeout(config.DEEPSEEK_TIMEOUT, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(config.DEEPSEEK_API_URL, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    return content.strip()
                else:
                    raise Exception("No valid response choices in API response")
            elif response.status_code == 429:
                raise Exception(f"API rate limited (429)")
            elif response.status_code == 401:
                raise Exception(f"API authentication failed (401) - check API key")
            else:
                error_text = response.text if hasattr(response, 'text') else 'Unknown error'
                raise Exception(f"API error {response.status_code}: {error_text}")
                
    except asyncio.TimeoutError:
        raise Exception(f"API request timeout after {config.DEEPSEEK_TIMEOUT}s - try increasing timeout in config.py")
    except httpx.TimeoutException:
        raise Exception(f"API request timeout after {config.DEEPSEEK_TIMEOUT}s - try increasing timeout in config.py")
    except httpx.RequestError as e:
        raise Exception(f"Network error: {str(e)} - check internet connection")
    except Exception as e:
        # Re-raise without fallback
        raise e

# Add after the health check endpoint
@app.post("/api/download-report")
async def download_evaluation_report(
    request: Request,
    evaluation_data: str = Form(...),
    format: str = Form("json"),  # json, txt, docx
    include_transcript: bool = Form(False)
):
    """
    Generate and download evaluation report in specified format
    """
    try:
        # Parse evaluation data
        eval_results = json.loads(evaluation_data)
        
        # 🆕 自动保存评估结果到数据库（如果尚未保存）
        session_id = None
        if PYMYSQL_AVAILABLE and config.ENABLE_AUTO_SAVE:
            try:
                # 检查评估数据中是否已有session_id
                session_id = eval_results.get('session_id')
                if not session_id:
                    # 如果没有session_id，保存评估结果到数据库
                    requirement_context = eval_results.get('requirement_document', '')
                    session_id = await save_evaluation_to_database(eval_results, requirement_context)
                    print(f"✅ 评估结果已自动保存到数据库，会话ID: {session_id}")
                
                # 记录下载活动
                if session_id:
                    file_size = len(evaluation_data)  # 估算文件大小
                    await save_download_record(session_id, format, include_transcript, file_size, request)
                    print(f"📥 下载记录已保存: {format} 格式，包含对话记录: {include_transcript}")
                    
            except Exception as db_error:
                print(f"⚠️ 数据库保存失败，但报告生成将继续: {db_error}")
        
        # 生成并返回报告
        if format == "json":
            return generate_json_report(eval_results, include_transcript)
        elif format == "txt":
            return generate_txt_report(eval_results, include_transcript)
        elif format == "docx":
            return generate_docx_report(eval_results, include_transcript)
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

def generate_json_report(eval_results: Dict, include_transcript: bool = False) -> JSONResponse:
    """Generate JSON format report with complete evaluation information"""
    report_data = {
        "evaluation_summary": eval_results.get("evaluation_summary", {}),
        "overall_score": eval_results.get("overall_score", 0),
        "dimension_scores": eval_results.get("dimension_scores", {}),
        "detailed_analysis": eval_results.get("detailed_analysis", {}),
        "recommendations": eval_results.get("recommendations", []),
        "user_persona_info": eval_results.get("user_persona_info", {}),
        "detailed_context_display": eval_results.get("detailed_context_display", {}),
        "persona_alignment_analysis": eval_results.get("persona_alignment_analysis", ""),
        "business_goal_achievement": eval_results.get("business_goal_achievement", ""),
        "evaluation_mode": eval_results.get("evaluation_mode", "unknown"),
        "timestamp": eval_results.get("timestamp", datetime.now().isoformat())
    }
    
    if include_transcript:
        report_data["conversation_records"] = eval_results.get("conversation_records", [])
    
    return JSONResponse(
        content=report_data,
        headers={"Content-Disposition": "attachment; filename=evaluation_report.json"}
    )

def generate_txt_report(eval_results: Dict, include_transcript: bool = False) -> FileResponse:
    """Generate TXT format report"""
    import tempfile
    
    # Extract scoring information with proper 100-point scale
    overall_score = eval_results.get('evaluation_summary', {}).get('overall_score', eval_results.get('overall_score', 0))
    
    report_content = f"""
AI Agent Evaluation Report
=========================
Generated: {eval_results.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
Evaluation Mode: {eval_results.get('evaluation_mode', 'Unknown')}

OVERALL PERFORMANCE
------------------
Overall Score: {overall_score}/100.0

DIMENSION SCORES
---------------
"""
    
    # Use conversation_records to extract dimension scores
    conversation_records = eval_results.get('conversation_records', [])
    if conversation_records:
        for i, record in enumerate(conversation_records, 1):
            scenario_title = record.get('scenario', {}).get('title', f'Scenario {i}')
            report_content += f"\n{scenario_title}:\n"
            scores = record.get('evaluation_scores_with_explanations', record.get('evaluation_scores', {}))
            for dimension, score_data in scores.items():
                score = score_data.get('score', score_data) if isinstance(score_data, dict) else score_data
                dimension_name = dimension.replace('_', ' ').title()
                report_content += f"  {dimension_name}: {score}/100.0\n"
    
    report_content += f"\nDETAILED ANALYSIS\n{'-' * 16}\n"
    
    detailed_analysis = eval_results.get('detailed_analysis', {})
    for dimension, analysis in detailed_analysis.items():
        report_content += f"\n{dimension.upper()}:\n"
        if isinstance(analysis, dict):
            report_content += f"Score: {analysis.get('score', 'N/A')}\n"
            report_content += f"Analysis: {analysis.get('detailed_analysis', 'No details available')}\n"
        else:
            report_content += f"{analysis}\n"
    
    report_content += f"\nRECOMMENDations\n{'-' * 15}\n"
    recommendations = eval_results.get('recommendations', [])
    for i, rec in enumerate(recommendations, 1):
        report_content += f"{i}. {rec}\n"
    
    if include_transcript:
        report_content += f"\nCONVERSATION TRANSCRIPT\n{'-' * 22}\n"
        conversation_records = eval_results.get('conversation_records', [])
        for record in conversation_records:
            for turn in record.get('conversation', []):
                report_content += f"Turn {turn.get('turn', 'N/A')}: {turn.get('user_message', '')}\n"
                report_content += f"AI Response: {turn.get('ai_response', '')}\n\n"
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(report_content)
        tmp_file_path = tmp_file.name
    
    return FileResponse(
        path=tmp_file_path,
        filename="evaluation_report.txt",
        media_type="text/plain"
    )

def generate_docx_report(eval_results: Dict, include_transcript: bool = False) -> FileResponse:
    """Generate DOCX format report (if docx library is available)"""
    if not DOCUMENT_PROCESSING_AVAILABLE:
        raise HTTPException(status_code=500, detail="DOCX generation not available. Install python-docx.")
    
    import tempfile
    from docx import Document
    from docx.shared import Inches
    
    # Create document
    doc = Document()
    
    # Title
    title = doc.add_heading('AI Agent Evaluation Report', 0)
    
    # Summary section
    doc.add_heading('Executive Summary', level=1)
    overall_score = eval_results.get('overall_score', 'N/A')
    doc.add_paragraph(f'Overall Performance Score: {overall_score}/5.0')
    doc.add_paragraph(f'Generated: {eval_results.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}')
    
    # Dimension scores
    doc.add_heading('Performance Dimensions', level=1)
    dimension_scores = eval_results.get('dimension_scores', {})
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Dimension'
    hdr_cells[1].text = 'Score'
    
    for dimension, score in dimension_scores.items():
        row_cells = table.add_row().cells
        row_cells[0].text = dimension.replace('_', ' ').title()
        row_cells[1].text = f'{score}/5.0'
    
    # Detailed analysis
    doc.add_heading('Detailed Analysis', level=1)
    detailed_analysis = eval_results.get('detailed_analysis', {})
    for dimension, analysis in detailed_analysis.items():
        doc.add_heading(dimension.replace('_', ' ').title(), level=2)
        if isinstance(analysis, dict):
            doc.add_paragraph(f"Score: {analysis.get('score', 'N/A')}")
            doc.add_paragraph(analysis.get('detailed_analysis', 'No details available'))
        else:
            doc.add_paragraph(str(analysis))
    
    # Recommendations
    doc.add_heading('Recommendations', level=1)
    recommendations = eval_results.get('recommendations', [])
    for i, rec in enumerate(recommendations, 1):
        doc.add_paragraph(f'{i}. {rec}')
    
    # Conversation transcript (if requested)
    if include_transcript:
        doc.add_heading('Conversation Transcript', level=1)
        conversation_records = eval_results.get('conversation_records', [])
        for record in conversation_records:
            scenario_title = record.get('scenario', {}).get('title', 'Unknown Scenario')
            doc.add_heading(f'Scenario: {scenario_title}', level=2)
            for turn in record.get('conversation', []):
                doc.add_paragraph(f"Turn {turn.get('turn', 'N/A')}: {turn.get('user_message', '')}")
                doc.add_paragraph(f"AI Response: {turn.get('ai_response', '')}")
                doc.add_paragraph("")  # Empty line for spacing
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
    
    doc.save(tmp_file_path)
    
    return FileResponse(
        path=tmp_file_path,
        filename="evaluation_report.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

async def call_coze_with_strict_timeout(api_config: APIConfig, message: str, conversation_manager: ConversationManager = None, use_raw_message: bool = False) -> str:
    """
    Call AI Agent API with strict timeout for dynamic conversations and proper logging
    """
    try:
        # Add memory check before API call to prevent crashes
        memory_usage = check_memory_usage()
        if memory_usage > config.MEMORY_CRITICAL_THRESHOLD:
            raise Exception(f"Memory usage critical: {memory_usage:.1f}%. Please restart server.")
        
        # Use timeout wrapper for individual API calls
        response = await asyncio.wait_for(
            call_ai_agent_api(api_config, message, conversation_manager, use_raw_message),
            timeout=config.DEFAULT_REQUEST_TIMEOUT  # 2 minutes for individual calls
        )
        
        # Determine API type for proper logging (reduced verbosity)
        if "/v1/chat-messages" in api_config.url or "dify" in api_config.url.lower():
            print(f"✅ Dify API响应 ({len(response)} chars)")
        elif "coze" in api_config.url.lower():
            print(f"✅ Coze API响应 ({len(response)} chars)")
        else:
            print(f"✅ 自定义API响应 ({len(response)} chars)")
            
        return response
        
    except asyncio.TimeoutError:
        print(f"⏰ API调用超时 ({config.DEFAULT_REQUEST_TIMEOUT}秒)")
        return ""
    except Exception as e:
        print(f"❌ API调用失败: {str(e)}")
        return ""

async def generate_single_initial_message(scenario_info: Dict, user_persona_info: Dict) -> str:
    """
    Generate a single initial message based on scenario and user persona
    """
    try:
        persona = user_persona_info.get('user_persona', {})
        usage_context = user_persona_info.get('usage_context', {})
        ai_role = user_persona_info.get('ai_role_simulation', {})
        
        # Get fuzzy expressions and opening patterns for this role
        fuzzy_expressions = ai_role.get('fuzzy_expressions', [])
        opening_patterns = ai_role.get('opening_patterns', [])
        
        generation_prompt = f"""
你是一个{persona.get('role', '专业用户')}，工作环境是{persona.get('work_environment', '专业环境')}。
你的沟通风格：{persona.get('communication_style', '专业沟通')}
当前场景：{scenario_info.get('title', '专业咨询')}
场景背景：{scenario_info.get('context', '工作场景')}

请生成一个简短的初始问题或需求描述，要求：
1. 体现{persona.get('role', '用户')}的身份和背景
2. 表达方式要{persona.get('communication_style', '专业')}
3. 可以稍微模糊或不完整，需要AI追问澄清
4. 长度控制在10-30个字
5. 不要使用引号或特殊符号

示例风格参考（仅参考风格，不要照搬）：
{', '.join(fuzzy_expressions[:3]) if fuzzy_expressions else '有个问题需要咨询'}

直接输出问题内容，不要任何解释：
"""
        
        response = await call_deepseek_api_enhanced(generation_prompt, temperature=0.6, max_tokens=100)
        
        # Clean the response
        message = response.strip().strip('"').strip("'").strip('。').strip('？').strip('!')
        
        if message and len(message) > 3:
            print(f"✅ 生成初始消息: {message}")
            return message
        else:
            # Fallback to predefined patterns
            if opening_patterns:
                import random
                fallback = random.choice(opening_patterns)
                print(f"🔄 使用备用开场: {fallback}")
                return fallback
            else:
                return "有个问题需要咨询"
                
    except Exception as e:
        print(f"❌ 初始消息生成失败: {str(e)}")
        # Ultimate fallback
        return "请帮忙解决一个问题"

async def generate_next_message_based_on_response(
    scenario_info: Dict, 
    user_persona_info: Dict, 
    conversation_history: List[Dict], 
    coze_response: str
) -> str:
    """
    Generate next user message based on Coze's response and conversation context
    """
    try:
        persona = user_persona_info.get('user_persona', {})
        
        # Analyze the conversation so far
        turn_count = len(conversation_history)
        last_user_message = conversation_history[-1]['user_message'] if conversation_history else ""
        
        generation_prompt = f"""
你是一个{persona.get('role', '专业用户')}，正在与AI助手对话。
沟通风格：{persona.get('communication_style', '专业沟通')}
场景：{scenario_info.get('title', '专业咨询')}

对话历史：
{chr(10).join([f"第{turn['turn']}轮 - 我: {turn['user_message']}" for turn in conversation_history[-2:]])}
AI刚才回复: {coze_response[:200]}

现在是第{turn_count + 1}轮对话。基于AI的回复，请生成你的下一个问题或回应：

要求：
1. 自然地基于AI的回复内容继续对话
2. 可以追问细节、要求澄清、或提出新的相关问题  
3. 保持{persona.get('role', '用户')}的身份和{persona.get('communication_style', '沟通风格')}
4. 长度10-40个字
5. 如果AI已经充分回答了问题，可以回复"END"结束对话

直接输出下一句话，不要解释：
"""
        
        print(f"🤖 DeepSeek分析Coze回复内容: {coze_response[:50]}...")
        response = await call_deepseek_api_enhanced(generation_prompt, temperature=0.7, max_tokens=150)
        
        # Clean the response
        message = response.strip().strip('"').strip("'").strip('。').strip('？').strip('!')
        
        if message and len(message) > 2:
            # Check if it's an end signal
            if message.upper() in ["END", "FINISH", "DONE", "结束", "完成"]:
                print("🔚 DeepSeek判断对话应该结束")
                return "END"
            
            print(f"✅ DeepSeek基于Coze回复生成下轮消息: {message}")
            return message
        else:
            # If generation fails, end the conversation
            print("❌ DeepSeek生成下轮消息失败，结束对话")
            return "END"
            
    except Exception as e:
        print(f"❌ 下轮消息生成失败: {str(e)}")
        return "END"

async def evaluate_conversation_with_deepseek(
    conversation_history: List[Dict], 
    scenario_info: Dict, 
    requirement_context: str = "", 
    user_persona_info: Dict = None
) -> tuple:
    """
    Enhanced conversation evaluation with detailed explanations and 100-point scoring
    """
    try:
        print("🧠 开始DeepSeek智能评估...")
        
        # Build conversation context - ensure it uses the complete actual conversation
        conversation_text = "完整对话记录:\n"
        for turn in conversation_history:
            conversation_text += f"第{turn['turn']}轮:\n"
            conversation_text += f"用户: {turn['user_message']}\n"
            conversation_text += f"AI回答: {turn['ai_response']}\n\n"
        
        # Build evaluation context
        context_section = f"""
业务场景: {scenario_info.get('context', '通用AI助手场景')}
对话主题: {scenario_info.get('title', '')}
"""
        
        # Add persona information if available
        if user_persona_info:
            persona = user_persona_info.get('user_persona', {})
            context_section += f"""
用户角色: {persona.get('role', '')}
经验水平: {persona.get('experience_level', '')}
沟通风格: {persona.get('communication_style', '')}
工作环境: {persona.get('work_environment', '')}
"""
        
        if requirement_context:
            context_section += f"\n需求文档上下文:\n{requirement_context[:800]}"
        
        # Enhanced evaluation with detailed explanations
        evaluation_scores = {}
        detailed_explanations = {}
        
        # Define evaluation dimensions
        dimensions = {
            "fuzzy_understanding": "模糊理解与追问能力",
            "answer_correctness": "回答准确性与专业性",
            "persona_alignment": "用户匹配度"
        }
        
        if requirement_context:
            dimensions["goal_alignment"] = "目标对齐度"
        
        # Evaluate each dimension with optimized prompts (shorter but focused)
        for dimension, dimension_name in dimensions.items():
            eval_prompt = f"""
{context_section}

{conversation_text}

请评估AI在"{dimension_name}"方面的表现。

评分标准 (1-100分制):
90-100分: 优秀表现，完全符合要求，超出预期
80-89分: 良好表现，基本符合期望，有小幅提升空间
70-79分: 中等表现，满足基本要求，但有明显改进空间
60-69分: 及格表现，存在一些问题，需要改进
50-59分: 不及格表现，有重要缺陷
1-49分: 差劲表现，存在明显问题

请按以下格式简洁输出：

评分：XX分

详细分析：
[分析AI的具体表现，指出优势和不足]

改进建议：
[2-3条具体改进建议]
"""
            
            try:
                response = await call_deepseek_api_enhanced(eval_prompt, temperature=0.2, max_tokens=500)
                
                # Extract score (now on 100-point scale)
                score = extract_score_from_response(response)
                evaluation_scores[dimension] = score
                
                # Parse structured response with enhanced detail
                parsed_analysis = parse_evaluation_response_enhanced(response, score)
                
                # Store detailed explanation with enhanced structure
                detailed_explanations[dimension] = {
                    "score": score,
                    "score_out_of": 100,  # Make it clear this is out of 100
                    "detailed_analysis": parsed_analysis.get("detailed_analysis", response),
                    "specific_quotes": parsed_analysis.get("specific_quotes", ""),
                    "improvement_suggestions": parsed_analysis.get("improvement_suggestions", ""),
                    "comprehensive_evaluation": parsed_analysis.get("comprehensive_evaluation", ""),
                    "dimension_name": dimension_name,
                    "full_response": response,
                    "score_grade": get_score_grade(score)  # Add grade label
                }
                
                print(f"  ✅ {dimension_name}: {score}/100 ({get_score_grade(score)})")
                
            except Exception as e:
                print(f"  ❌ {dimension_name}评估失败: {str(e)}")
                evaluation_scores[dimension] = 60.0
                detailed_explanations[dimension] = {
                    "score": 60.0,
                    "score_out_of": 100,
                    "detailed_analysis": f"评估失败: {str(e)}，请重新尝试评估",
                    "specific_quotes": "由于技术原因，无法提供具体对话引用",
                    "improvement_suggestions": "建议检查AI Agent配置后重新评估",
                    "comprehensive_evaluation": "技术问题导致评估中断",
                    "dimension_name": dimension_name,
                    "full_response": f"评估异常: {str(e)}",
                    "score_grade": "及格"
                }
        
        # Calculate overall score (now average of 100-point scores)
        scenario_score = sum(evaluation_scores.values()) / len(evaluation_scores) if evaluation_scores else 60.0
        
        print(f"✅ 评估完成，场景得分: {scenario_score:.1f}/100")
        return evaluation_scores, detailed_explanations, scenario_score
        
    except Exception as e:
        print(f"❌ DeepSeek评估失败: {str(e)}")
        # Return fallback scores with proper 100-point structure
        fallback_scores = {
            "fuzzy_understanding": 60.0,
            "answer_correctness": 60.0,
            "persona_alignment": 60.0
        }
        fallback_explanations = {
            dim: {
                "score": 60.0, 
                "score_out_of": 100,
                "detailed_analysis": f"由于技术原因导致评估失败: {str(e)}。请检查网络连接和API配置后重试。",
                "specific_quotes": "无法获取具体对话引用，建议重新进行评估",
                "improvement_suggestions": "建议检查AI Agent配置和网络连接状况",
                "comprehensive_evaluation": "技术故障导致无法完成评估",
                "dimension_name": dim,
                "full_response": f"评估系统异常: {str(e)}",
                "score_grade": "及格"
            }
            for dim in fallback_scores.keys()
        }
        return fallback_scores, fallback_explanations, 60.0

def get_score_grade(score: float) -> str:
    """Convert numerical score to grade label"""
    if score >= 90:
        return "优秀"
    elif score >= 80:
        return "良好"
    elif score >= 70:
        return "中等"
    elif score >= 60:
        return "及格"
    else:
        return "不及格"

def parse_evaluation_response_enhanced(response: str, score: float) -> Dict[str, str]:
    """
    Parse enhanced evaluation response to extract different sections with better structure
    """
    try:
        # Initialize result
        result = {
            "detailed_analysis": "",
            "specific_quotes": "",
            "improvement_suggestions": "",
            "comprehensive_evaluation": ""
        }
        
        # Split response into lines
        lines = response.strip().split('\n')
        current_section = "detailed_analysis"
        
        for line in lines:
            line = line.strip()
            
            # Identify section headers
            if "详细分析" in line or "分析" in line:
                current_section = "detailed_analysis"
                continue
            elif "具体引用" in line or "引用" in line or "对话" in line:
                current_section = "specific_quotes"
                continue
            elif "改进建议" in line or "建议" in line:
                current_section = "improvement_suggestions"
                continue
            elif "综合评价" in line or "评价" in line:
                current_section = "comprehensive_evaluation"
                continue
            elif "评分" in line:
                continue  # Skip score lines
            
            # Add content to current section
            if line and not line.startswith("评分"):
                if result[current_section]:
                    result[current_section] += "\n" + line
                else:
                    result[current_section] = line
        
        # Ensure all sections have content with enhanced detail
        if not result["detailed_analysis"]:
            result["detailed_analysis"] = f"评分 {score} 分（{get_score_grade(score)}）。" + (response[:300] if response else "未提供详细分析")
            
        if not result["specific_quotes"]:
            result["specific_quotes"] = "具体对话引用：由于响应格式限制，未能提取具体引用内容。建议人工查看对话记录进行分析。"
            
        if not result["improvement_suggestions"]:
            result["improvement_suggestions"] = "建议继续优化AI回答质量，提升用户满意度。具体改进措施需要根据对话内容进一步分析。"
            
        if not result["comprehensive_evaluation"]:
            result["comprehensive_evaluation"] = f"该维度得分{score}分，属于{get_score_grade(score)}水平。"
        
        return result
        
    except Exception as e:
        print(f"⚠️ 解析评估响应失败: {str(e)}")
        return {
            "detailed_analysis": f"评分 {score} 分（{get_score_grade(score)}）。" + (response[:300] if response else "解析失败，未提供详细分析"),
            "specific_quotes": "由于解析异常，无法提供具体对话引用",
            "improvement_suggestions": "建议重新进行评估以获取详细建议",
            "comprehensive_evaluation": f"该维度得分{score}分，但由于解析问题，无法提供完整评价。"
        }

async def generate_final_comprehensive_report(
    evaluation_results: List[Dict], 
    user_persona_info: Dict, 
    requirement_context: str
) -> Dict:
    """
    Generate comprehensive final report with enhanced analysis
    """
    try:
        print("📊 生成综合分析报告...")
        
        # Extract key information
        total_scenarios = len(evaluation_results)
        overall_scores = [r.get('scenario_score', 0) for r in evaluation_results]
        avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        
        persona = user_persona_info.get('user_persona', {})
        context = user_persona_info.get('usage_context', {})
        
        # Generate improvement recommendations
        recommendations = []
        
        if avg_score < 3.0:
            recommendations.extend([
                f"🔴 针对{persona.get('role', '用户')}的整体服务能力需要显著改进",
                f"📚 加强{context.get('business_domain', '专业')}领域的知识库建设",
                "💡 提升对模糊需求的理解和追问能力"
            ])
        elif avg_score < 4.0:
            recommendations.extend([
                f"🟡 对{persona.get('role', '用户')}的服务基本满足需求，有优化空间",
                "🎯 针对用户沟通风格进行个性化优化",
                "📈 继续提升专业知识的准确性"
            ])
        else:
            recommendations.extend([
                f"🟢 对{persona.get('role', '用户')}的服务表现优秀",
                "✨ 保持当前优势，持续优化用户体验",
                "🚀 可以考虑扩展更多专业场景支持"
            ])
        
        return {
            "improvement_recommendations": recommendations,
            "extracted_persona_summary": user_persona_info,
            "persona_alignment_analysis": f"基于{total_scenarios}个场景的评估，AI对{persona.get('role', '用户')}的适配程度为{avg_score:.2f}/5.0",
            "business_goal_achievement": f"在{context.get('business_domain', '专业服务')}领域的目标达成度良好，平均得分{avg_score:.2f}分"
        }
        
    except Exception as e:
        print(f"❌ 综合报告生成失败: {str(e)}")
        return {
            "improvement_recommendations": ["系统建议：加强对话理解能力", "系统建议：提高回答准确性"],
            "extracted_persona_summary": user_persona_info,
            "persona_alignment_analysis": "基于系统分析生成",
            "business_goal_achievement": "评估完成"
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

async def extract_user_persona_with_deepseek(requirement_content: str) -> Dict[str, Any]:
    """
    Use DeepSeek to extract user persona, context, and role information from requirement document
    Enhanced with better document analysis and content matching
    """
    
    # Debug: Log the document content for troubleshooting
    logger.info(f"🎭 开始用户画像提取，文档长度: {len(requirement_content)}")
    logger.debug(f"📝 文档内容前1000字符: {requirement_content[:1000]}")
    print(f"🎭 开始用户画像提取，文档长度: {len(requirement_content)}")
    print(f"📝 文档内容前500字符: {requirement_content[:500]}")
    
    # Pre-analysis: Check for construction/civil engineering keywords
    construction_keywords = ['建筑', '施工', '工程', '监理', '现场', '质量检查', '安全规范', '建筑施工', '土建', '钢筋', '混凝土', '基础工程', '结构工程', '安装工程', '装修工程']
    civil_keywords = ['民用建筑', '工业建筑', '基础设施', '道路工程', '桥梁工程', '水电工程', '暖通工程', '消防工程', '园林工程', '市政工程']
    
    found_construction = [kw for kw in construction_keywords if kw in requirement_content]
    found_civil = [kw for kw in civil_keywords if kw in requirement_content]
    
    logger.info(f"🔍 检测到建筑关键词: {found_construction}")
    logger.info(f"🔍 检测到土建关键词: {found_civil}")
    print(f"🔍 检测到建筑关键词: {found_construction}")
    print(f"🔍 检测到土建关键词: {found_civil}")
    
    # First, perform content analysis to identify key domain indicators
    content_analysis_prompt = f"""
请仔细分析以下需求文档的内容，并识别关键信息：

文档内容：
{requirement_content[:1500]}

请识别：
1. 文档主要涉及的行业/领域（如：建筑工程、土木工程、银行金融、客服咨询、技术支持等）
2. 主要业务类型（如：施工现场监理、工程质量检查、规范查询、客户服务、故障排除等）
3. 用户可能的工作角色（如：土建工程师、建筑监理、银行客服、技术工程师等）
4. 使用场景特征（如：建筑现场作业、施工监理、办公室工作、移动办公等）

**特别注意**：如果文档涉及建筑、施工、工程监理等内容，请准确识别为建筑工程领域。

只输出关键词，用逗号分隔，不要解释：
行业领域：
业务类型：
用户角色：
使用场景：
"""
    
    try:
        # Step 1: Analyze document content
        logger.info("🔍 开始文档内容分析...")
        print("🔍 开始文档内容分析...")
        
        content_analysis = await call_deepseek_api_enhanced(content_analysis_prompt, temperature=0.2, max_tokens=200)
        logger.info(f"📋 内容分析结果: {content_analysis}")
        print(f"📋 内容分析结果: {content_analysis}")
        
        # Parse analysis results
        analysis_lines = content_analysis.strip().split('\n')
        domain_hints = {}
        
        for line in analysis_lines:
            if '：' in line:
                key, value = line.split('：', 1)
                domain_hints[key.strip()] = value.strip()
        
        logger.info(f"🔍 解析得到的领域提示: {domain_hints}")
        print(f"🔍 解析得到的领域提示: {domain_hints}")
        
        # Step 2: Enhanced extraction with domain-specific guidance
        extraction_prompt = f"""
你是一位专业的需求分析师，请根据以下需求文档进行用户画像分析。

**分析原则：** 
- 基于文档实际内容进行客观分析
- 识别文档中描述的主要用户群体和使用场景
- 重点关注最终用户的角色和需求，而非系统开发者

**文档内容分析：**
行业领域：{domain_hints.get('行业领域', '未识别')}
业务类型：{domain_hints.get('业务类型', '未识别')}  
用户角色：{domain_hints.get('用户角色', '未识别')}
使用场景：{domain_hints.get('使用场景', '未识别')}

**需求文档原文：**
{requirement_content}

**分析要求：**
1. 准确识别文档中描述的用户角色和工作场景
2. 分析用户的专业背景和工作环境特点
3. 提取典型的对话场景和交互需求
4. 关注用户的沟通风格和表达习惯

请严格按照JSON格式输出：

{{
    "user_persona": {{
        "role": "基于文档内容的具体用户角色（必须与{domain_hints.get('行业领域', '文档领域')}高度匹配）",
        "experience_level": "基于文档推断的经验水平详细描述", 
        "expertise_areas": ["与文档主题直接相关的专业领域1", "相关专业领域2"],
        "communication_style": "符合该行业特点的沟通风格（包括模糊表达特征）",
        "work_environment": "与文档业务场景匹配的工作环境详细描述",
        "work_pressure": "该角色典型的工作压力和时间约束"
    }},
    "usage_context": {{
        "primary_scenarios": ["基于文档的主要使用场景1", "相关使用场景2"],
        "business_domain": "与文档内容严格对应的具体业务领域",
        "interaction_goals": ["与文档需求直接相关的交互目标1", "相关目标2"],
        "pain_points": ["文档中体现的痛点问题1", "相关痛点2"],
        "usage_timing": ["符合该业务特点的使用时机1", "相关时机2"]
    }},
    "ai_role_simulation": {{
        "simulated_user_type": "基于文档内容的用户类型详细描述",
        "conversation_approach": "符合该行业的对话方式偏好", 
        "language_characteristics": "该行业用户的语言特点（包括专业术语、表达习惯）",
        "typical_questions": ["该角色在此业务场景下的典型问题1", "典型问题2", "典型问题3"],
        "fuzzy_expressions": ["该行业常见的模糊表达1", "模糊表达2", "模糊表达3"],
        "opening_patterns": ["该角色常用的开场方式1", "开场方式2"],
        "situational_variations": "该角色在不同工作情况下的表达差异"
    }},
    "extracted_requirements": {{
        "core_functions": ["文档中明确提到的核心功能需求1", "核心需求2"],
        "quality_expectations": ["文档中体现的质量期望1", "质量期望2"],
        "interaction_preferences": ["基于业务特点的交互偏好1", "偏好2"]
    }}
}}"""

        print("🧠 开始增强的用户画像提取...")
        
        # Call API with enhanced error handling
        response = await call_deepseek_api_enhanced(extraction_prompt, temperature=0.3, max_tokens=1000)
        print(f"📝 DeepSeek extraction response: {response[:300]}...")
        
        # Clean and parse response
        cleaned_response = response.strip()
        
        # Remove markdown code blocks if present
        if cleaned_response.startswith('```'):
            lines = cleaned_response.split('\n')
            start_line = 1
            end_line = len(lines) - 1
            
            # Find actual JSON start and end
            for i, line in enumerate(lines):
                if line.strip().startswith('{'):
                    start_line = i
                    break
            
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip().endswith('}'):
                    end_line = i
                    break
                    
            cleaned_response = '\n'.join(lines[start_line:end_line + 1])
        
        # Find JSON boundaries
        start_idx = cleaned_response.find('{')
        end_idx = cleaned_response.rfind('}')
        
        if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
            raise Exception("DeepSeek response does not contain valid JSON structure")
        
        json_str = cleaned_response[start_idx:end_idx+1]
        
        try:
            extraction_result = json.loads(json_str)
            print("✅ Successfully parsed enhanced extraction result from DeepSeek")
            
            # Validate the structure
            required_keys = ['user_persona', 'usage_context', 'ai_role_simulation', 'extracted_requirements']
            if not all(key in extraction_result for key in required_keys):
                raise Exception(f"JSON structure incomplete, missing keys: {[k for k in required_keys if k not in extraction_result]}")
            
            # Post-processing validation: ensure role matches domain
            user_role = extraction_result.get('user_persona', {}).get('role', '')
            business_domain = extraction_result.get('usage_context', {}).get('business_domain', '')
            
            # Domain consistency check
            domain_mapping = {
                '建筑': ['工程', '监理', '施工', '建筑'],
                '工程': ['工程师', '监理', '技术', '现场'],  
                '银行': ['客服', '金融', '银行', '理财'],
                '金融': ['客服', '金融', '银行', '理财'],
                '客服': ['客服', '服务', '咨询', '接待'],
                '技术': ['技术', '工程师', '开发', '运维']
            }
            
            # Check if role matches domain
            domain_keywords = domain_hints.get('行业领域', '').lower()
            role_keywords = user_role.lower()
            
            consistency_check = False
            for domain_key, valid_roles in domain_mapping.items():
                if domain_key in domain_keywords:
                    if any(role_word in role_keywords for role_word in valid_roles):
                        consistency_check = True
                        break
            
            if not consistency_check and domain_keywords:
                print(f"⚠️ 角色一致性检查失败，重新调整角色匹配")
                # Adjust role to match domain
                extraction_result = adjust_role_for_domain_consistency(extraction_result, domain_hints)
            
            print(f"✅ 最终提取角色: {extraction_result.get('user_persona', {}).get('role', '未知')}")
            print(f"✅ 业务领域: {extraction_result.get('usage_context', {}).get('business_domain', '未知')}")
            
            return extraction_result
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse DeepSeek response as JSON: {str(e)}")
            
    except Exception as e:
        print(f"⚠️ Enhanced persona extraction failed: {str(e)}")
        print("🔄 Using domain-aware fallback persona generation...")
        
        # Return domain-aware fallback result
        fallback_result = create_domain_aware_fallback_result(requirement_content, domain_hints if 'domain_hints' in locals() else {})
        print("✅ Domain-aware fallback persona generated successfully")
        return fallback_result

def adjust_role_for_domain_consistency(extraction_result: Dict, domain_hints: Dict) -> Dict:
    """
    Perform light adjustment for domain consistency while preserving DeepSeek's analysis
    """
    domain = domain_hints.get('行业领域', '').lower()
    current_role = extraction_result.get('user_persona', {}).get('role', '')
    
    print(f"🔍 领域一致性检查: 域={domain}, 角色={current_role}")
    
    # Only perform light validation without forcing changes
    if domain and current_role:
        # Log the extracted role and domain for debugging
        print(f"✅ 提取的角色与领域: {current_role} in {domain}")
        
        # Basic domain-role matching suggestions (not enforced)
        suggested_domains = {
            '建筑': '建筑工程',
            '工程': '工程技术', 
            '银行': '银行服务',
            '金融': '金融服务',
            '客服': '客户服务',
            '医疗': '医疗健康',
            '教育': '教育培训'
        }
        
        # Suggest business domain if not specific enough
        current_domain = extraction_result.get('usage_context', {}).get('business_domain', '')
        if not current_domain or current_domain in ['专业服务', '未知']:
            for keyword, suggested_domain in suggested_domains.items():
                if keyword in domain:
                    extraction_result['usage_context']['business_domain'] = suggested_domain
                    print(f"💡 建议业务领域: {suggested_domain}")
                    break
    
    return extraction_result

def create_domain_aware_fallback_result(requirement_content: str, domain_hints: Dict) -> Dict[str, Any]:
    """
    Create a domain-aware fallback result when parsing fails
    Enhanced with better construction/civil engineering detection
    """
    logger.info("🔄 创建领域感知的回退结果...")
    print("🔄 创建领域感知的回退结果...")
    
    # Extract domain information with enhanced construction detection
    domain = domain_hints.get('行业领域', extract_business_domain_from_content(requirement_content))
    role = domain_hints.get('用户角色', extract_role_from_content(requirement_content))
    
    logger.info(f"🏢 检测到领域: {domain}")
    logger.info(f"👤 检测到角色: {role}")
    print(f"🏢 检测到领域: {domain}")
    print(f"👤 检测到角色: {role}")
    
    # Enhanced construction/civil engineering detection
    construction_indicators = ['建筑', '施工', '工程', '监理', '现场', '质量', '安全', '规范', '建设', '土建', '结构', '基础']
    if any(indicator in requirement_content for indicator in construction_indicators):
        logger.info("🏗️ 强制设置为建筑工程领域")
        print("🏗️ 强制设置为建筑工程领域")
        domain = '建筑工程'
        role = '土建工程师' if not role or '技术' in role else role
    
    # Ensure role matches domain with enhanced construction handling
    if '建筑' in domain.lower() or '工程' in domain.lower() or '施工' in domain.lower():
        # More accurate civil engineering role detection
        if '监理' in requirement_content:
            role = '建筑工程监理'
        elif '施工' in requirement_content:
            role = '施工工程师'
        elif '设计' in requirement_content:
            role = '建筑设计师'
        elif '质量' in requirement_content:
            role = '质量工程师'
        else:
            role = '土建工程师'  # Default for construction
        
        business_domain = '建筑工程'
        typical_questions = ["这个规范要求是什么？", "施工标准符合吗？", "质量检查怎么做？", "安全措施到位吗？", "这个材料符合标准吗？"]
        fuzzy_expressions = ["这个地方有问题", "标准不太对", "需要检查一下", "质量有点问题", "不太符合规范"]
    elif '银行' in domain.lower() or '金融' in domain.lower():
        role = role if '客服' in role or '银行' in role else '银行客服代表'
        business_domain = '银行金融服务'
        typical_questions = ["客户问这个怎么办？", "这个业务怎么处理？", "政策是什么？"]
        fuzzy_expressions = ["客户不满意", "又是那个问题", "怎么解释呢"]
    elif '客服' in domain.lower():
        role = role if '客服' in role else '客服专员'
        business_domain = '客户服务'
        typical_questions = ["客户投诉怎么处理？", "这个问题怎么解决？", "服务标准是什么？"]
        fuzzy_expressions = ["客户又投诉了", "老问题了", "不知道怎么说"]
    else:
        role = role or '专业用户'
        business_domain = domain or '专业服务'
        typical_questions = ["这个怎么处理？", "规范要求是什么？", "还有其他方案吗？"]
        fuzzy_expressions = ["有点问题", "不太对", "怎么处理？"]

    return {
        "user_persona": {
            "role": role,
            "experience_level": "中等经验专业用户",
            "expertise_areas": [business_domain, "相关专业知识"],
            "communication_style": "专业但有时表达不完整，贴合行业特点",
            "work_environment": f"{business_domain}工作环境",
            "work_pressure": "正常工作压力，注重效率和准确性"
        },
        "usage_context": {
            "primary_scenarios": [f"{business_domain}咨询", "工作支持"],
            "business_domain": business_domain,
            "interaction_goals": ["获取准确信息", "解决工作问题"],
            "pain_points": ["信息不够具体", "回答时间较长"],
            "usage_timing": ["工作时间", "遇到问题时", "需要确认时"]
        },
        "ai_role_simulation": {
            "simulated_user_type": f"基于{business_domain}的{role}",
            "conversation_approach": "直接提问，有时表达模糊",
            "language_characteristics": f"{business_domain}专业术语与日常表达混合",
            "typical_questions": typical_questions,
            "fuzzy_expressions": fuzzy_expressions,
            "opening_patterns": ["关于这个...", "需要咨询...", "有个问题...", "想了解..."],
            "situational_variations": "工作繁忙时表达简短，正常情况下会详细描述"
        },
        "extracted_requirements": {
            "core_functions": ["准确信息查询", "专业问题解答"],
            "quality_expectations": ["回答准确", "响应及时", "专业性强"],
            "interaction_preferences": ["简洁明了", "包含具体示例", "提供操作指导"]
        }
    }

def extract_role_from_content(content: str) -> Optional[str]:
    """Extract user role from content"""
    if "客服" in content:
        return "客服代表"
    elif "监理" in content:
        return "现场监理工程师"
    elif "工程师" in content:
        return "工程师"
    elif "技术" in content:
        return "技术人员"
    return None

def extract_business_domain_from_content(content: str) -> str:
    """Extract business domain from content with enhanced construction detection"""
    logger.debug(f"🔍 分析业务领域，内容前200字符: {content[:200]}")
    
    # Enhanced construction/civil engineering detection
    construction_keywords = ['建筑', '施工', '工程', '监理', '现场', '质量检查', '安全规范', '建筑施工', '土建', '钢筋', '混凝土', '基础工程', '结构工程']
    civil_keywords = ['民用建筑', '工业建筑', '基础设施', '道路工程', '桥梁工程', '水电工程', '暖通工程', '消防工程']
    
    construction_count = sum(1 for kw in construction_keywords if kw in content)
    civil_count = sum(1 for kw in civil_keywords if kw in content)
    
    logger.debug(f"🏗️ 建筑关键词匹配数: {construction_count}")
    logger.debug(f"🏗️ 土建关键词匹配数: {civil_count}")
    
    if construction_count > 0 or civil_count > 0:
        logger.info("✅ 识别为建筑工程领域")
        return "建筑工程"
    elif "银行" in content or "金融" in content:
        return "银行金融服务"
    elif "客服" in content:
        return "客户服务"
    elif "技术" in content and "工程" not in content:  # Avoid misclassifying engineering as tech support
        return "技术支持"
    else:
        return "专业服务"

async def conduct_dynamic_multi_scenario_evaluation(
    api_config: APIConfig,
    user_persona_info: Dict,
    requirement_context: str,
    use_raw_messages: bool = False
) -> List[Dict]:
    """
    Conduct dynamic multi-scenario evaluation based on extracted user persona
    """
    try:
        print("🎯 开始动态多场景评估...")
        
        # Generate 2 dynamic scenarios based on user persona
        scenarios = await generate_dynamic_scenarios_from_persona(user_persona_info)
        
        if not scenarios:
            print("⚠️ 无法生成动态场景，使用默认场景")
            scenarios = [
                {
                    "title": "基础咨询场景",
                    "context": f"{user_persona_info.get('usage_context', {}).get('business_domain', '专业服务')}咨询",
                    "user_profile": user_persona_info.get('user_persona', {}).get('role', '专业用户')
                },
                {
                    "title": "问题解决场景", 
                    "context": f"{user_persona_info.get('usage_context', {}).get('business_domain', '专业服务')}问题处理",
                    "user_profile": user_persona_info.get('user_persona', {}).get('role', '专业用户')
                }
            ]
        
        evaluation_results = []
        
        for i, scenario_info in enumerate(scenarios, 1):
            print(f"📋 场景 {i}/{len(scenarios)}: {scenario_info.get('title', '未命名场景')}")
            
            try:
                # Conduct true dynamic conversation for this scenario
                conversation_history = await conduct_true_dynamic_conversation(
                    api_config, scenario_info, user_persona_info, use_raw_messages
                )
                
                if not conversation_history:
                    print(f"⚠️ 场景 {i} 对话失败，跳过")
                    continue
                
                # Evaluate the conversation
                evaluation_scores, detailed_explanations, scenario_score = await evaluate_conversation_with_deepseek(
                    conversation_history, scenario_info, requirement_context, user_persona_info
                )
                
                # Convert scenario score to 5-point scale for consistency
                scenario_score_5 = scenario_score / 20.0 if scenario_score > 5 else scenario_score
                
                # Create evaluation result
                evaluation_result = {
                    "scenario": {
                        "title": scenario_info.get('title', f'场景 {i}'),
                        "context": scenario_info.get('context', '动态生成场景'),
                        "user_profile": scenario_info.get('user_profile', user_persona_info.get('user_persona', {}).get('role', '专业用户'))
                    },
                    "conversation_history": conversation_history,
                    "evaluation_scores": evaluation_scores,
                    "detailed_explanations": detailed_explanations,
                    "scenario_score": round(scenario_score_5, 2),  # Use 5-point scale
                    "scenario_score_100": round(scenario_score, 2),  # Also provide 100-point scale
                    "evaluation_mode": "dynamic",
                    "timestamp": datetime.now().isoformat()
                }
                
                evaluation_results.append(evaluation_result)
                print(f"✅ 场景 {i} 评估完成，得分: {scenario_score_5:.2f}/5.0")
                
            except Exception as e:
                print(f"❌ 场景 {i} 评估失败: {str(e)}")
                continue
        
        if not evaluation_results:
            raise Exception("所有场景评估均失败")
        
        print(f"🎯 动态多场景评估完成，共完成 {len(evaluation_results)} 个场景")
        return evaluation_results
        
    except Exception as e:
        print(f"❌ 动态多场景评估失败: {str(e)}")
        raise e

async def generate_dynamic_scenarios_from_persona(user_persona_info: Dict) -> List[Dict]:
    """
    Generate dynamic scenarios based on extracted user persona
    """
    try:
        persona = user_persona_info.get('user_persona', {})
        context = user_persona_info.get('usage_context', {})
        
        # Generate scenarios based on primary scenarios from persona
        primary_scenarios = context.get('primary_scenarios', ['专业咨询', '工作支持'])
        business_domain = context.get('business_domain', '专业服务')
        role = persona.get('role', '专业用户')
        
        scenarios = []
        
        # Generate first scenario based on primary use case
        if len(primary_scenarios) >= 1:
            scenarios.append({
                "title": f"{primary_scenarios[0]}场景",
                "context": f"{business_domain} - {primary_scenarios[0]}",
                "user_profile": f"{role}，{persona.get('experience_level', '中等经验')}"
            })
        
        # Generate second scenario based on secondary use case or pain points
        if len(primary_scenarios) >= 2:
            scenarios.append({
                "title": f"{primary_scenarios[1]}场景",
                "context": f"{business_domain} - {primary_scenarios[1]}",
                "user_profile": f"{role}，{persona.get('experience_level', '中等经验')}"
            })
        elif context.get('pain_points'):
            # Create scenario based on pain points
            pain_point = context['pain_points'][0] if context['pain_points'] else '效率提升'
            scenarios.append({
                "title": f"{pain_point}解决场景",
                "context": f"{business_domain} - 解决{pain_point}问题",
                "user_profile": f"{role}，{persona.get('experience_level', '中等经验')}"
            })
        
        return scenarios[:2]  # Return maximum 2 scenarios
        
    except Exception as e:
        print(f"❌ 动态场景生成失败: {str(e)}")
        return []

@app.post("/api/test-with-raw-coze-conversation")
async def test_with_raw_coze_conversation(
    agent_api_config: str = Form(...),
    coze_conversation_json: str = Form(...),
    use_raw_message: bool = Form(True)
):
    """
    Test AI Agent with raw Coze conversation JSON - extracts user message and sends it directly
    """
    try:
        print("🧪 开始原始Coze对话测试...")
        
        # Parse API configuration
        api_config_dict = json.loads(agent_api_config)
        api_config = APIConfig(**api_config_dict)
        
        # Parse Coze conversation JSON
        coze_data = json.loads(coze_conversation_json)
        
        # Extract raw user message
        raw_user_message = extract_user_message_from_coze_json(coze_data)
        
        if not raw_user_message:
            raise HTTPException(status_code=400, detail="无法从Coze对话JSON中提取用户消息")
        
        print(f"✅ 提取到原始用户消息: {raw_user_message}")
        
        # Call AI Agent with raw message
        ai_response = await call_ai_agent_api(api_config, raw_user_message, use_raw_message=use_raw_message)
        
        return {
            "status": "success",
            "raw_user_message": raw_user_message,
            "ai_response": ai_response,
            "use_raw_message": use_raw_message,
            "message_processing_mode": "RAW" if use_raw_message else "ENHANCED",
            "timestamp": datetime.now().isoformat()
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON解析失败: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Raw Coze conversation test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")

@app.post("/api/extract-user-persona")
async def extract_user_persona(
    requirement_file: UploadFile = File(None),
    requirement_text: str = Form(None)
):
    """
    Extract user persona from requirement document
    """
    try:
        logger.info("🎭 开始用户画像提取...")
        print("🎭 开始用户画像提取...")
        
        # Handle requirement document
        requirement_context = ""
        
        if requirement_file and requirement_file.filename:
            logger.info(f"📄 Processing uploaded file: {requirement_file.filename}")
            print(f"📄 Processing uploaded file: {requirement_file.filename}")
            requirement_context = await process_uploaded_document_improved(requirement_file)
        elif requirement_text:
            logger.info("📝 Using provided text content")
            print("📝 Using provided text content")
            requirement_context = requirement_text
        
        if not requirement_context:
            raise HTTPException(status_code=400, detail="请提供需求文档或文本内容")
            
        logger.info(f"✅ Document processed, length: {len(requirement_context)} characters")
        print(f"✅ Document processed, length: {len(requirement_context)} characters")
        
        # Extract user persona using enhanced algorithm
        user_persona_info = await extract_user_persona_with_deepseek(requirement_context)
        
        if not user_persona_info:
            raise HTTPException(status_code=400, detail="无法从需求文档中提取有效的用户画像信息")
        
        return {
            "status": "success",
            "extraction_result": user_persona_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Persona extraction failed: {str(e)}")
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        print(f"❌ Persona extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"用户画像提取失败: {str(e)}")

@app.post("/api/debug-document-processing")
async def debug_document_processing(
    requirement_file: UploadFile = File(None),
    requirement_text: str = Form(None)
):
    """
    Debug endpoint to test document processing and persona extraction separately
    This helps identify where the issue occurs in cloud deployment
    """
    try:
        result = {
            "document_processing": {},
            "persona_extraction": {},
            "domain_analysis": {},
            "errors": []
        }
        
        # Step 1: Document Processing
        requirement_context = ""
        
        if requirement_file and requirement_file.filename:
            logger.info(f"🧪 Debug: Processing file {requirement_file.filename}")
            try:
                requirement_context = await process_uploaded_document_improved(requirement_file)
                result["document_processing"] = {
                    "status": "success",
                    "filename": requirement_file.filename,
                    "content_length": len(requirement_context),
                    "content_preview": requirement_context[:300] + "..." if len(requirement_context) > 300 else requirement_context,
                    "file_type": getattr(requirement_file, 'content_type', 'unknown')
                }
            except Exception as e:
                error_msg = f"Document processing failed: {str(e)}"
                result["document_processing"] = {
                    "status": "error",
                    "error": error_msg,
                    "traceback": traceback.format_exc()
                }
                result["errors"].append(error_msg)
                
        elif requirement_text:
            requirement_context = requirement_text
            result["document_processing"] = {
                "status": "success",
                "source": "text_input",
                "content_length": len(requirement_context),
                "content_preview": requirement_context[:300] + "..." if len(requirement_context) > 300 else requirement_context
            }
        
        if not requirement_context:
            result["errors"].append("No document content available")
            return result
        
        # Step 2: Domain Analysis
        try:
            domain = extract_business_domain_from_content(requirement_context)
            role = extract_role_from_content(requirement_context)
            
            # Construction keywords analysis
            construction_keywords = ['建筑', '施工', '工程', '监理', '现场', '质量检查', '安全规范', '建筑施工', '土建', '钢筋', '混凝土', '基础工程', '结构工程']
            found_keywords = [kw for kw in construction_keywords if kw in requirement_context]
            
            result["domain_analysis"] = {
                "status": "success",
                "detected_domain": domain,
                "detected_role": role,
                "construction_keywords_found": found_keywords,
                "total_construction_keywords": len(found_keywords),
                "is_construction_content": len(found_keywords) > 0
            }
        except Exception as e:
            error_msg = f"Domain analysis failed: {str(e)}"
            result["domain_analysis"] = {
                "status": "error",
                "error": error_msg
            }
            result["errors"].append(error_msg)
        
        # Step 3: Persona Extraction
        try:
            user_persona_info = await extract_user_persona_with_deepseek(requirement_context)
            result["persona_extraction"] = {
                "status": "success",
                "extracted_role": user_persona_info.get('user_persona', {}).get('role', 'N/A'),
                "business_domain": user_persona_info.get('usage_context', {}).get('business_domain', 'N/A'),
                "extraction_method": "deepseek_api",
                "full_result": user_persona_info
            }
        except Exception as e:
            error_msg = f"Persona extraction failed: {str(e)}"
            result["persona_extraction"] = {
                "status": "error",
                "error": error_msg,
                "traceback": traceback.format_exc()
            }
            result["errors"].append(error_msg)
            
            # Try fallback method
            try:
                fallback_result = create_domain_aware_fallback_result(requirement_context, {})
                result["persona_extraction"]["fallback_result"] = {
                    "role": fallback_result.get('user_persona', {}).get('role', 'N/A'),
                    "business_domain": fallback_result.get('usage_context', {}).get('business_domain', 'N/A'),
                    "method": "fallback"
                }
            except Exception as fallback_error:
                result["persona_extraction"]["fallback_error"] = str(fallback_error)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Debug endpoint failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# Database related functions
def get_database_connection():
    """
    Create database connection
    """
    if not PYMYSQL_AVAILABLE or not config.ENABLE_DATABASE_SAVE:
        return None
    
    try:
        connection = pymysql.connect(**config.DATABASE_CONFIG)
        return connection
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return None

def generate_session_id() -> str:
    """
    Generate unique session ID for evaluation
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_suffix = uuid.uuid4().hex[:8]
    return f"EVAL_{timestamp}_{random_suffix}"

async def save_evaluation_to_database(evaluation_data: Dict, requirement_context: str = "") -> str:
    """
    Save evaluation results to database
    Returns session_id if successful, None if failed
    """
    if not PYMYSQL_AVAILABLE or not config.ENABLE_DATABASE_SAVE:
        print("📝 Database save disabled or PyMySQL not available")
        return None
    
    connection = get_database_connection()
    if not connection:
        print("❌ Cannot connect to database")
        return None
    
    session_id = generate_session_id()
    
    try:
        with connection.cursor() as cursor:
            # Insert main evaluation session
            insert_session_sql = """
                INSERT INTO ai_evaluation_sessions (
                    session_id, overall_score, total_scenarios, total_conversations,
                    evaluation_mode, evaluation_framework, requirement_document,
                    ai_agent_config, user_persona_info, evaluation_summary, recommendations
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            evaluation_summary = evaluation_data.get('evaluation_summary', {})
            
            # Convert 100-point scale to 5-point scale for database storage
            overall_score = evaluation_summary.get('overall_score_100', evaluation_summary.get('overall_score', 0))
            if overall_score > 5:  # If it's 100-point scale, convert to 5-point scale
                overall_score_5_point = overall_score / 20.0  # Convert 100-point to 5-point
            else:
                overall_score_5_point = overall_score
            
            cursor.execute(insert_session_sql, (
                session_id,
                round(overall_score_5_point, 2),  # Store as 5-point scale
                evaluation_summary.get('total_scenarios', 0),
                evaluation_summary.get('total_conversations', 0),
                evaluation_data.get('evaluation_mode', 'manual'),
                evaluation_summary.get('framework', 'AI Agent 3维度评估框架'),
                requirement_context[:5000] if requirement_context else None,  # Limit length
                json.dumps(evaluation_data.get('ai_agent_config', {})),
                json.dumps(evaluation_data.get('user_persona_info', {})),
                json.dumps(evaluation_summary),
                json.dumps(evaluation_data.get('recommendations', []))
            ))
            
            # Insert conversation scenarios and records
            conversation_records = evaluation_data.get('conversation_records', [])
            
            for scenario_index, record in enumerate(conversation_records):
                scenario = record.get('scenario', {})
                conversation_history = record.get('conversation_history', [])
                evaluation_scores = record.get('evaluation_scores_with_explanations', {})
                
                # Insert scenario
                insert_scenario_sql = """
                    INSERT INTO ai_conversation_scenarios (
                        session_id, scenario_index, scenario_title, scenario_context,
                        user_profile, scenario_score, conversation_turns
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                # Convert scenario score to 5-point scale for database storage
                scenario_score = record.get('scenario_score_100', record.get('scenario_score', 0))
                if scenario_score > 5:  # If it's 100-point scale, convert to 5-point scale
                    scenario_score_5_point = scenario_score / 20.0
                else:
                    scenario_score_5_point = scenario_score
                
                cursor.execute(insert_scenario_sql, (
                    session_id,
                    scenario_index,
                    scenario.get('title', f'场景 {scenario_index + 1}'),
                    scenario.get('context', ''),
                    scenario.get('user_profile', ''),
                    round(scenario_score_5_point, 2),  # Store as 5-point scale
                    len(conversation_history)
                ))
                
                scenario_id = cursor.lastrowid
                
                # Insert conversation turns
                for turn in conversation_history:
                    insert_turn_sql = """
                        INSERT INTO ai_conversation_turns (
                            session_id, scenario_id, turn_number, user_message,
                            enhanced_message, ai_response, response_length
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(insert_turn_sql, (
                        session_id,
                        scenario_id,
                        turn.get('turn', 0),
                        turn.get('user_message', ''),
                        turn.get('enhanced_message', ''),
                        turn.get('ai_response', ''),
                        len(turn.get('ai_response', ''))
                    ))
                
                # Insert evaluation scores
                for dimension_name, score_data in evaluation_scores.items():
                    if isinstance(score_data, dict):
                        insert_score_sql = """
                            INSERT INTO ai_evaluation_scores (
                                session_id, scenario_id, dimension_name, dimension_label,
                                score, detailed_analysis, specific_quotes,
                                improvement_suggestions, full_response
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        dimension_labels = {
                            'fuzzy_understanding': '模糊理解与追问能力',
                            'answer_correctness': '回答准确性与专业性',
                            'persona_alignment': '用户匹配度',
                            'goal_alignment': '目标对齐度'
                        }
                        
                        # Convert dimension score to 5-point scale for database storage
                        dimension_score = score_data.get('score', 0)
                        if dimension_score > 5:  # If it's 100-point scale, convert to 5-point scale
                            dimension_score_5_point = dimension_score / 20.0
                        else:
                            dimension_score_5_point = dimension_score
                        
                        cursor.execute(insert_score_sql, (
                            session_id,
                            scenario_id,
                            dimension_name,
                            dimension_labels.get(dimension_name, dimension_name),
                            round(dimension_score_5_point, 2),  # Store as 5-point scale
                            score_data.get('detailed_analysis', ''),
                            score_data.get('specific_quotes', ''),
                            score_data.get('improvement_suggestions', ''),
                            score_data.get('full_response', '')
                        ))
        
        connection.commit()
        print(f"✅ Evaluation data saved to database with session_id: {session_id}")
        return session_id
        
    except Exception as e:
        connection.rollback()
        print(f"❌ Failed to save evaluation to database: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return None
    finally:
        connection.close()

async def save_download_record(session_id: str, download_format: str, include_transcript: bool, 
                             file_size: int = None, request: Request = None) -> bool:
    """
    Record download activity
    """
    if not PYMYSQL_AVAILABLE or not config.ENABLE_DATABASE_SAVE:
        return False
    
    connection = get_database_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            client_ip = request.client.host if request else None
            user_agent = request.headers.get("user-agent") if request else None
            
            insert_sql = """
                INSERT INTO ai_report_downloads (
                    session_id, download_format, include_transcript,
                    file_size, download_ip, user_agent
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_sql, (
                session_id, download_format, include_transcript,
                file_size, client_ip, user_agent
            ))
        
        connection.commit()
        return True
        
    except Exception as e:
        print(f"❌ Failed to save download record: {str(e)}")
        return False
    finally:
        connection.close()

def extract_user_message_from_coze_json(coze_conversation_json: Dict) -> str:
    """
    Extract raw user message from Coze conversation JSON structure
    
    Expected Coze JSON structure:
    {
        "additional_messages": [
            {
                "content_type": "text",
                "type": "question",
                "role": "user", 
                "content": "SBS卷材搭接处热熔质量检查情况？节点部位附加层要做闭水试验"
            }
        ]
    }
    """
    try:
        # 🐛 Debug log for Coze JSON parsing
        print(f"🔍 [COZE JSON] Extracting user message from: {json.dumps(coze_conversation_json, ensure_ascii=False)[:200]}...")
        
        # Try to extract from additional_messages (most common)
        if "additional_messages" in coze_conversation_json:
            additional_messages = coze_conversation_json["additional_messages"]
            if isinstance(additional_messages, list) and len(additional_messages) > 0:
                first_message = additional_messages[0]
                if isinstance(first_message, dict) and "content" in first_message:
                    raw_content = first_message["content"].strip()
                    print(f"🔍 [EXTRACTED] Raw user message: {raw_content}")
                    return raw_content
        
        # Try to extract from messages array
        if "messages" in coze_conversation_json:
            messages = coze_conversation_json["messages"]
            if isinstance(messages, list):
                for message in messages:
                    if (isinstance(message, dict) and 
                        message.get("role") == "user" and 
                        "content" in message):
                        raw_content = message["content"].strip()
                        print(f"🔍 [EXTRACTED] Raw user message from messages: {raw_content}")
                        return raw_content
        
        # Try direct content field
        if "content" in coze_conversation_json:
            raw_content = coze_conversation_json["content"].strip()
            print(f"🔍 [EXTRACTED] Raw user message from content: {raw_content}")
            return raw_content
        
        # Fallback - look for any text content
        for key, value in coze_conversation_json.items():
            if isinstance(value, str) and len(value.strip()) > 5:
                print(f"🔍 [FALLBACK] Using field '{key}': {value.strip()}")
                return value.strip()
        
        print("❌ [EXTRACTION FAILED] No user message found in Coze JSON")
        return ""
        
    except Exception as e:
        print(f"❌ [EXTRACTION ERROR] Failed to extract user message: {str(e)}")
        return ""

def clean_ai_response(response: str) -> str:
    """
    Clean AI response to extract meaningful content and filter out system messages
    Enhanced to properly handle plugin tool outputs
    """
    try:
        original_response = response
        print(f"🧹 Cleaning AI response: {response[:100]}...")
        
        # 🔧 NEW: First check if this is a plugin tool output that we want to preserve
        if response and not response.strip().startswith('{"name":"'):
            # This might be actual tool output content, preserve it
            pass
        elif (response.strip().startswith('{"name":"') and 
            '"arguments":' in response and
            '"plugin_id":' in response):
            # This is a plugin invocation JSON - try to extract tool output
            try:
                plugin_data = json.loads(response)
                tool_output_fields = ['tool_output_content', 'output', 'result', 'content', 'answer']
                
                for field in tool_output_fields:
                    if field in plugin_data and plugin_data[field]:
                        tool_output = str(plugin_data[field])
                        if len(tool_output.strip()) > 10:
                            print(f"🔧 Extracted {field} from plugin JSON: {tool_output[:80]}...")
                            return clean_ai_response(tool_output)  # Recursive clean
                
                # Check nested arguments
                if 'arguments' in plugin_data and isinstance(plugin_data['arguments'], dict):
                    args = plugin_data['arguments']
                    for field in tool_output_fields:
                        if field in args and args[field]:
                            tool_output = str(args[field])
                            if len(tool_output.strip()) > 10:
                                print(f"🔧 Extracted args.{field} from plugin JSON: {tool_output[:80]}...")
                                return clean_ai_response(tool_output)  # Recursive clean
                
                print("🚫 No useful tool output found in plugin JSON, filtering out")
                return ""  # Return empty if no tool output found
                
            except json.JSONDecodeError:
                print("🚫 Backup filter: Detected malformed plugin JSON, filtering out")
                return ""
        
        # Check for pure system messages (skip only if entire response is system content)
        system_only_indicators = [
            '"msg_type":"time_capsule_recall"',
            '"msg_type":"conversation_summary"', 
            '"msg_type":"system_message"'
        ]
        
        # If the response is ONLY a system message, skip it
        if (response.strip().startswith('{"msg_type"') and 
            any(indicator in response for indicator in system_only_indicators) and
            len(response.strip()) < 2000):  # Short responses that are likely pure system messages
            print("🚫 Detected pure system message, skipping this response")
            return ""  # Return empty to trigger conversation end
        
        # If response looks like JSON, try to extract the actual answer
        if response.strip().startswith('{'):
            try:
                # Handle multiple JSON objects in response (streaming format)
                json_objects = []
                lines = response.strip().split('\n')
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('data: '):
                        line = line[6:]  # Remove 'data: ' prefix
                    
                    if line and line.startswith('{') and line.endswith('}'):
                        try:
                            json_obj = json.loads(line)
                            json_objects.append(json_obj)
                        except json.JSONDecodeError:
                            continue
                
                # If no JSON objects found, try parsing the entire response
                if not json_objects:
                    try:
                        json_objects = [json.loads(response)]
                    except json.JSONDecodeError:
                        pass
                
                # Extract meaningful content from JSON objects
                meaningful_content = ""
                
                for json_obj in json_objects:
                    # Skip system messages
                    if json_obj.get('msg_type') in ['time_capsule_recall', 'conversation_summary', 'system_message']:
                        continue
                    
                    # Extract content from various possible fields
                    content_fields = [
                        'tool_output_content',
                        'content', 
                        'answer',
                        'message',
                        'text',
                        'response'
                    ]
                    
                    for field in content_fields:
                        if field in json_obj and json_obj[field]:
                            content = str(json_obj[field])
                            
                            # Clean up escape characters
                            content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
                            
                            # Filter out evaluation-related content
                            evaluation_keywords = [
                                '用户编写的信息',
                                '用户画像信息', 
                                '用户记忆点信息',
                                '避免使用隐私和敏感信息',
                                '以下信息来源于用户与你对话',
                                'wraped_text',
                                'origin_search_results'
                            ]
                            
                            if not any(keyword in content for keyword in evaluation_keywords):
                                # Look for "答案：" pattern and extract content after it
                                if "答案：" in content:
                                    answer_part = content.split("答案：", 1)[1]
                                    answer_part = answer_part.replace("参考依据：", "").replace("依据来源：", "")
                                    meaningful_content = answer_part.strip()
                                    break
                                elif len(content.strip()) > 10:  # Substantial content
                                    meaningful_content = content.strip()
                                    break
                
                if meaningful_content:
                    print(f"✅ Extracted from JSON: {meaningful_content[:80]}...")
                    return meaningful_content
                    
            except Exception as e:
                print(f"⚠️ JSON parsing failed: {str(e)}")
        
        # Handle streaming format patterns - enhanced for stream_plugin_finish
        if '"msg_type":"stream_plugin_finish"' in response:
            try:
                import re
                # Try multiple patterns to extract content
                patterns = [
                    r'"tool_output_content":"([^"]+)"',
                    r'"content":"([^"]+)"',
                    r'"answer":"([^"]+)"',
                    r'"text":"([^"]+)"'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, response)
                    if match:
                        content = match.group(1)
                        content = content.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
                        
                        # Filter out evaluation content
                        if not any(keyword in content for keyword in [
                            '用户编写的信息', '用户画像信息', '用户记忆点信息',
                            'wraped_text', 'origin_search_results'
                        ]):
                            if "答案：" in content:
                                answer_part = content.split("答案：", 1)[1]
                                answer_part = answer_part.replace("参考依据：", "").replace("依据来源：", "")
                                cleaned_answer = answer_part.strip()
                                if len(cleaned_answer) > 5:  # Ensure substantial content
                                    print(f"✅ Extracted from stream_plugin_finish: {cleaned_answer[:80]}...")
                                    return cleaned_answer
                            elif len(content.strip()) > 5:  # Substantial content
                                print(f"✅ Extracted from stream_plugin_finish: {content.strip()[:80]}...")
                                return content.strip()
                            
                # If no patterns matched, try to parse the JSON directly
                try:
                    json_data = json.loads(response)
                    data_field = json_data.get('data', {})
                    if isinstance(data_field, str):
                        # Sometimes data is a JSON string
                        try:
                            data_obj = json.loads(data_field)
                            tool_output = data_obj.get('tool_output_content', '')
                            if tool_output and len(tool_output.strip()) > 5:
                                print(f"✅ Extracted from nested JSON: {tool_output[:80]}...")
                                return tool_output.strip()
                        except:
                            pass
                except:
                    pass
                    
            except Exception as e:
                print(f"⚠️ Stream plugin parsing failed: {str(e)}")
                pass
        
        # Handle plain text with "答案：" pattern
        if "答案：" in response and not any(keyword in response for keyword in [
            '用户编写的信息', '用户画像信息', '用户记忆点信息'
        ]):
            answer_part = response.split("答案：", 1)[1]
            lines = answer_part.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('参考依据：') and not line.startswith('依据来源：'):
                    return line
        
        # Final fallback - return original if it's clean text
        cleaned = response.strip()
        
        # 🔧 DEBUGGING: Check what content is being filtered
        print(f"🔍 CONTENT FILTER DEBUG: Original length: {len(cleaned)} chars")
        print(f"🔍 CONTENT FILTER DEBUG: First 200 chars: {cleaned[:200]}...")
        
        # Final filter check for system content (REDUCED STRICTNESS)
        high_priority_system_patterns = [
            '"msg_type":"time_capsule_recall"',
            '"msg_type":"conversation_summary"',
            '"msg_type":"system_message"'
        ]
        
        # Only filter if it's clearly a system message AND short
        if (any(pattern in cleaned for pattern in high_priority_system_patterns) and 
            len(cleaned.strip()) < 1000):  # Only filter short system messages
            print(f"🚫 Final filter caught system content pattern, returning empty")
            return ""
        
        # 🔧 NEW: Allow evaluation-related content but warn
        evaluation_patterns = [
            '用户编写的信息', '用户画像信息', '用户记忆点信息',
            'wraped_text', 'origin_search_results'
        ]
        
        if any(pattern in cleaned for pattern in evaluation_patterns):
            print(f"⚠️ WARNING: Content contains evaluation pattern but allowing it: {cleaned[:100]}...")
            # Don't return empty - let it through with warning
        
        print(f"✅ Cleaned response: {cleaned[:80]}...")
        return cleaned
        
    except Exception as e:
        print(f"❌ 响应清理异常: {str(e)}")
        return original_response.strip() if len(original_response.strip()) < 500 else ""

async def test_coze_plugin_extraction():
    """
    Test function to debug Coze API plugin content extraction
    """
    print("🧪 Testing Coze API plugin extraction...")
    
    # Test with a simple question that should trigger plugin
    test_message = "地下室防水卷材搭接宽度不够，基层处理好像也有问题"
    test_bot_id = "7498244859505999924"  # Default test bot ID
    
    try:
        # Try the HTTP fallback method first
        print("1️⃣ Testing HTTP fallback method...")
        result = await call_coze_api_fallback(test_message, test_bot_id)
        print(f"✅ HTTP fallback result: {result[:200]}...")
        print(f"📏 Result length: {len(result)} characters")
        
        # Test if result contains substantial content
        if len(result) > 100:
            print("✅ HTTP fallback appears to work correctly")
        else:
            print("❌ HTTP fallback returned minimal content")
            
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return None

# ⭐ Security and validation functions
def validate_filename(filename: str) -> bool:
    """Validate uploaded filename for security"""
    if not filename:
        return False
    
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    
    # Check for dangerous extensions
    if any(filename.lower().endswith(ext) for ext in config.BLOCKED_EXTENSIONS):
        return False
    
    # Check for allowed extensions
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in config.ALLOWED_EXTENSIONS:
        return False
    
    # Check filename length
    if len(filename) > config.MAX_FILENAME_LENGTH:
        return False
    
    return True

def sanitize_user_input(text: str, max_length: int = None) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    
    if max_length is None:
        max_length = config.MAX_INPUT_LENGTH
    
    # Remove null bytes and control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length] + "...[内容截断]"
    
    return text.strip()

def validate_api_url(url: str) -> bool:
    """Validate API URL for security"""
    if not url:
        return False
    
    # Check for valid HTTP/HTTPS URLs
    if not (url.startswith('http://') or url.startswith('https://')):
        return False
    
    # Prevent local network access
    blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
    blocked_patterns = [r'192\.168\.', r'10\.', r'172\.(1[6-9]|2\d|3[01])\.']
    
    for host in blocked_hosts:
        if host in url.lower():
            return False
    
    for pattern in blocked_patterns:
        if re.search(pattern, url):
            return False
    
    return True

@app.post("/api/convert-docx-to-text")
async def convert_docx_to_text(
    requirement_file: UploadFile = File(...),
):
    """
    Cloud-compatible DOCX to text conversion endpoint
    Provides detailed extraction methods and fallback options
    """
    try:
        if not requirement_file or not requirement_file.filename:
            raise HTTPException(status_code=400, detail="未提供文件")
        
        if not requirement_file.filename.lower().endswith('.docx'):
            raise HTTPException(status_code=400, detail="仅支持DOCX格式文件")
        
        # Validate file
        if not validate_filename(requirement_file.filename):
            raise HTTPException(status_code=400, detail="不安全的文件名")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            try:
                content = await requirement_file.read()
                
                if len(content) > config.MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="文件过大，请使用小于10MB的文件")
                
                tmp_file.write(content)
                tmp_file.flush()
                
                # Try all extraction methods and return best result
                extraction_results = {}
                
                # Method 1: python-docx
                try:
                    result1 = _extract_with_python_docx(tmp_file.name)
                    extraction_results['python_docx'] = {
                        'success': True,
                        'content': result1,
                        'length': len(result1),
                        'method': 'python-docx library'
                    }
                except Exception as e:
                    extraction_results['python_docx'] = {
                        'success': False,
                        'error': str(e),
                        'method': 'python-docx library'
                    }
                
                # Method 2: ZIP+XML Advanced
                try:
                    result2 = _extract_with_zip_xml_advanced(tmp_file.name)
                    extraction_results['zip_xml_advanced'] = {
                        'success': True,
                        'content': result2,
                        'length': len(result2),
                        'method': 'ZIP+XML with namespaces'
                    }
                except Exception as e:
                    extraction_results['zip_xml_advanced'] = {
                        'success': False,
                        'error': str(e),
                        'method': 'ZIP+XML with namespaces'
                    }
                
                # Method 3: ZIP+XML Simple
                try:
                    result3 = _extract_with_zip_xml_simple(tmp_file.name)
                    extraction_results['zip_xml_simple'] = {
                        'success': True,
                        'content': result3,
                        'length': len(result3),
                        'method': 'Simple ZIP+XML parsing'
                    }
                except Exception as e:
                    extraction_results['zip_xml_simple'] = {
                        'success': False,
                        'error': str(e),
                        'method': 'Simple ZIP+XML parsing'
                    }
                
                # Method 4: Raw text extraction
                try:
                    result4 = _extract_raw_text_from_docx(tmp_file.name)
                    extraction_results['raw_extraction'] = {
                        'success': True,
                        'content': result4,
                        'length': len(result4),
                        'method': 'Raw text extraction with regex'
                    }
                except Exception as e:
                    extraction_results['raw_extraction'] = {
                        'success': False,
                        'error': str(e),
                        'method': 'Raw text extraction with regex'
                    }
                
                # Find best result
                best_result = None
                best_method = None
                best_length = 0
                
                for method, result in extraction_results.items():
                    if result['success'] and result['length'] > best_length:
                        best_result = result['content']
                        best_method = method
                        best_length = result['length']
                
                return {
                    "success": best_result is not None,
                    "best_method": best_method,
                    "best_content": best_result,
                    "content_length": best_length,
                    "extraction_ratio": (best_length / len(content) * 100) if len(content) > 0 else 0,
                    "all_methods": extraction_results,
                    "recommendations": _generate_conversion_recommendations(extraction_results, len(content)),
                    "filename": requirement_file.filename,
                    "file_size": len(content)
                }
                
            finally:
                try:
                    if os.path.exists(tmp_file.name):
                        os.unlink(tmp_file.name)
                except:
                    pass
                    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ DOCX转换失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文档转换失败: {str(e)}")

def _generate_conversion_recommendations(extraction_results: Dict, file_size: int) -> List[str]:
    """Generate recommendations based on extraction results"""
    recommendations = []
    
    successful_methods = [method for method, result in extraction_results.items() if result['success']]
    
    if not successful_methods:
        recommendations.extend([
            "🚨 所有提取方法均失败，建议:",
            "1. 使用Microsoft Word打开文档，另存为.txt格式",
            "2. 检查文档是否包含复杂的图片、表格或特殊格式",
            "3. 尝试复制文档内容，直接粘贴到评估平台的文本框中",
            "4. 检查文档是否损坏或使用了不兼容的格式"
        ])
    elif len(successful_methods) == 1:
        best_method = successful_methods[0]
        best_result = extraction_results[best_method]
        extraction_ratio = best_result['length'] / file_size * 100 if file_size > 0 else 0
        
        if extraction_ratio < 5:
            recommendations.extend([
                f"⚠️ 提取率较低 ({extraction_ratio:.1f}%)，建议:",
                "1. 文档可能包含大量图片或表格，提取的主要是文本内容",
                "2. 使用Word另存为.txt格式可能获得更好效果",
                "3. 检查提取的内容是否包含主要信息"
            ])
        elif extraction_ratio < 15:
            recommendations.append("✅ 提取成功，但内容相对较少，建议检查是否提取了主要信息")
        else:
            recommendations.append("✅ 提取成功，内容丰富，可以正常使用")
    else:
        recommendations.append("✅ 多种方法提取成功，文档处理良好")
    
    # Cloud deployment specific recommendations
    recommendations.extend([
        "",
        "💡 云环境部署建议:",
        "1. 如果在云端遇到问题，优先使用.txt格式",
        "2. 保持文档内容简洁，避免过于复杂的格式",
        "3. 定期验证文档处理功能是否正常"
    ])
    
    return recommendations

@app.post("/api/enhanced-document-processing")
async def enhanced_document_processing(
    requirement_file: UploadFile = File(None),
    requirement_text: str = Form(None)
):
    """
    Enhanced document processing with cloud compatibility diagnostics
    """
    try:
        result = {
            "document_processing": {},
            "cloud_compatibility": {},
            "performance_metrics": {},
            "recommendations": []
        }
        
        if requirement_file and requirement_file.filename:
            # Process file with enhanced diagnostics
            start_time = time.time()
            
            try:
                # Check system environment
                result["cloud_compatibility"] = {
                    "python_docx_available": True,
                    "zipfile_available": True,
                    "xml_parser_available": True,
                    "temp_file_access": True
                }
                
                # Test dependencies
                try:
                    from docx import Document
                    result["cloud_compatibility"]["python_docx_available"] = True
                except ImportError:
                    result["cloud_compatibility"]["python_docx_available"] = False
                
                try:
                    import zipfile
                    import xml.etree.ElementTree as ET
                    result["cloud_compatibility"]["zipfile_available"] = True
                    result["cloud_compatibility"]["xml_parser_available"] = True
                except ImportError:
                    result["cloud_compatibility"]["zipfile_available"] = False
                    result["cloud_compatibility"]["xml_parser_available"] = False
                
                # Test temp file access
                try:
                    with tempfile.NamedTemporaryFile(delete=True) as test_tmp:
                        test_tmp.write(b"test")
                        result["cloud_compatibility"]["temp_file_access"] = True
                except Exception:
                    result["cloud_compatibility"]["temp_file_access"] = False
                
                # Process document
                processed_content = await process_uploaded_document_improved(requirement_file)
                
                processing_time = time.time() - start_time
                
                result["document_processing"] = {
                    "status": "success" if not processed_content.startswith("错误") else "error",
                    "filename": requirement_file.filename,
                    "file_size": len(await requirement_file.read()),  # Read size for metrics
                    "content_length": len(processed_content),
                    "content_preview": processed_content[:300] + "..." if len(processed_content) > 300 else processed_content,
                    "processing_time": processing_time
                }
                
                # Reset file position after reading size
                await requirement_file.seek(0)
                
                result["performance_metrics"] = {
                    "processing_time_seconds": processing_time,
                    "extraction_rate": "fast" if processing_time < 2 else "normal" if processing_time < 5 else "slow",
                    "extraction_ratio": (len(processed_content) / result["document_processing"]["file_size"] * 100) if result["document_processing"]["file_size"] > 0 else 0
                }
                
                # Generate recommendations
                if result["document_processing"]["status"] == "error":
                    result["recommendations"].extend([
                        "🚨 文档处理失败，建议:",
                        "1. 转换为.txt格式重新上传",
                        "2. 检查文档是否损坏",
                        "3. 使用文本内容直接粘贴方式"
                    ])
                elif result["performance_metrics"]["extraction_ratio"] < 5:
                    result["recommendations"].extend([
                        "⚠️ 提取率较低，建议:",
                        "1. 检查文档是否主要包含图片或表格",
                        "2. 考虑使用Word转换为纯文本格式",
                        "3. 验证提取的内容是否包含关键信息"
                    ])
                else:
                    result["recommendations"].append("✅ 文档处理成功，可以正常使用")
                
                # Cloud-specific recommendations
                if not all(result["cloud_compatibility"].values()):
                    result["recommendations"].extend([
                        "",
                        "🌐 云环境兼容性问题:",
                        "1. 某些依赖库可能不可用",
                        "2. 建议使用.txt格式作为备选方案",
                        "3. 联系管理员检查服务器配置"
                    ])
                
            except Exception as e:
                result["document_processing"] = {
                    "status": "error",
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
        
        elif requirement_text:
            result["document_processing"] = {
                "status": "success",
                "source": "text_input",
                "content_length": len(requirement_text),
                "content_preview": requirement_text[:300] + "..." if len(requirement_text) > 300 else requirement_text
            }
            
            result["recommendations"].append("✅ 文本内容处理成功")
        
        else:
            result["document_processing"] = {
                "status": "error",
                "error": "未提供文件或文本内容"
            }
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Enhanced document processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"增强文档处理失败: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test mode
        import asyncio
        asyncio.run(test_coze_plugin_extraction())
    else:
        # Run normal server
        port = find_available_port(config.DEFAULT_PORT)
        print(f"🚀 AI Agent评估平台启动在端口 {port}")
        uvicorn.run(app, host=config.DEFAULT_HOST, port=port) 