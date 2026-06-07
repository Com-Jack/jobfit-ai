"""API配置与常量"""

import os
from dotenv import load_dotenv

load_dotenv()

# 大模型API配置
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

# 默认参数
DEFAULT_INTERVIEW_COUNT = 5
MAX_INPUT_LENGTH = 10000
