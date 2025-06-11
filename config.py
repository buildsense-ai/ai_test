# AI Evaluation Platform Configuration
# Direct configuration file with hardcoded values for simple deployment

# DeepSeek API Configuration
DEEPSEEK_API_KEY = "sk-d2513b4c4626409599a73ba64b2e9033"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"  # Fixed URL

# Timeout settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2

# Logging configuration
LOG_LEVEL = "INFO"

# Server Configuration
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_WORKERS = 1
DEFAULT_LOG_LEVEL = "info"

# API Timeout Settings (Increased to prevent timeout errors)
DEFAULT_TIMEOUT = 60
DEEPSEEK_TIMEOUT = 60  # Increased from 20 to 60 seconds
COZE_TIMEOUT = 60

# Document Processing Settings
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_FORMATS = ['.docx', '.pdf', '.txt']

# Evaluation Settings
DEFAULT_TEMPERATURE = 0.1
ENHANCED_TEMPERATURE = 0.2
MAX_RETRIES = 2
MAX_CONVERSATION_TURNS = 5

# Application Settings
APP_TITLE = "AI Agent Evaluation Platform"
APP_VERSION = "4.0.0"
DEBUG_MODE = False

# Coze API Configuration (Updated with working credentials)
COZE_API_TOKEN = "pat_DiraOZEjagK8c6NNPJKionQsCj99zZduVyGkYO8YojolSQ8WAjBdF2CgbXNLMaFi"  # Primary token
COZE_API_KEY = COZE_API_TOKEN  # For SDK compatibility - always same as token
COZE_API_BASE_URL = "https://api.coze.cn"  # Primary base URL
COZE_API_BASE = COZE_API_BASE_URL  # For compatibility - always same as base URL

# Default Bot/Agent IDs (Updated with working bot)
DEFAULT_COZE_BOT_ID = "7498244859505999924"  # New working bot ID
DEFAULT_COZE_AGENT_ID = "default_agent_id"

# Coze Agent Configuration
COZE_AGENT_API_BASE = "https://api.coze.com/v1/workflow/run"

# Database Configuration
DATABASE_CONFIG = {
    'host': 'gz-cdb-e0aa423v.sql.tencentcdb.com',
    'port': 20236,
    'user': 'root',
    'password': 'Aa@114514',
    'database': 'ai_evaluation_db',
    'charset': 'utf8mb4',
    'autocommit': True
    # cursorclass will be set in code when needed
}

# Enable database features
ENABLE_DATABASE_SAVE = True
ENABLE_AUTO_SAVE = True
DATA_RETENTION_DAYS = 365

# Security Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_INPUT_LENGTH = 100000  # 100KB for text inputs
MAX_CONFIG_LENGTH = 50000  # 50KB for API configs
MAX_FILENAME_LENGTH = 255
EVALUATION_TIMEOUT = 480  # 8 minutes for evaluation
DEFAULT_REQUEST_TIMEOUT = 120  # 2 minutes for individual API calls

# File Upload Security
ALLOWED_EXTENSIONS = {'.docx', '.pdf', '.txt'}
BLOCKED_EXTENSIONS = {'.exe', '.bat', '.cmd', '.sh', '.scr', '.com', '.pif', '.vbs', '.js'}

# Rate Limiting (per minute)
MAX_EVALUATIONS_PER_MINUTE = 10
MAX_UPLOADS_PER_MINUTE = 20
MAX_API_CALLS_PER_MINUTE = 100

# Database Connection Pool
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30

# ⭐ Memory Management
MEMORY_WARNING_THRESHOLD = 85  # 85% memory usage warning
MEMORY_CRITICAL_THRESHOLD = 95  # 95% memory usage critical

print("📝 Configuration loaded: DeepSeek API key configured") 
print("🔒 Security settings loaded") 