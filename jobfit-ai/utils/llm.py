"""大模型API调用封装"""

from openai import OpenAI
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL


def get_client() -> OpenAI:
    """获取OpenAI兼容客户端"""
    if not LLM_API_KEY:
        raise ValueError(
            "未设置 LLM_API_KEY。\n"
            "请在 .env 文件中配置，或设置环境变量。\n"
            "参考 .env.example 获取配置模板。"
        )
    return OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)


def chat(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    """调用大模型进行对话"""
    client = get_client()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content


def chat_stream(system_prompt: str, user_prompt: str, temperature: float = 0.7):
    """流式调用大模型"""
    client = get_client()
    stream = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
