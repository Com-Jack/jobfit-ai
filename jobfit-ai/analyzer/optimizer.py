"""简历优化建议"""

import json
from utils.llm import chat
from analyzer.prompts import OPTIMIZE_SYSTEM, OPTIMIZE_USER


def optimize_resume(resume: str, job: str) -> dict:
    """根据目标岗位给出简历优化建议

    Args:
        resume: 简历文本
        job: 岗位JD文本

    Returns:
        优化建议字典
    """
    prompt = OPTIMIZE_USER.format(resume=resume, job=job)
    response = chat(OPTIMIZE_SYSTEM, prompt, temperature=0.5)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(response[start:end])
        else:
            result = {
                "overall_assessment": "解析失败，请重试",
                "keyword_suggestions": [],
                "experience_optimizations": [],
                "structure_suggestions": [],
                "action_items": [],
                "raw_response": response,
            }

    return result
