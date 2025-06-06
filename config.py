# Configuration file with hardcoded values for deployment

# DeepSeek API Configuration
DEEPSEEK_API_KEY = "sk-d2513b4c4626409599a73ba64b2e9033"  # Working DeepSeek API key
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"  # Fixed URL

# Coze API Configuration  
COZE_API_KEY = "pat_aWWxLQe20D8km5FsKt5W99pWL72L5LNxjkontH91q3lqqTU0ExBKUBl1cUy4tm8c"  # Working Coze API key
COZE_API_BASE_URL = "https://api.coze.com"

# Default Bot/Agent IDs
DEFAULT_COZE_BOT_ID = "7511993619423985674"
DEFAULT_COZE_AGENT_ID = "default_agent_id"

# Timeout settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2

# Logging configuration
LOG_LEVEL = "INFO"

# Deployment Notes:
# 1. API keys are already configured with working values
# 2. Update DEFAULT_COZE_BOT_ID with your bot ID if needed
# 3. Adjust timeout settings based on your deployment environment 