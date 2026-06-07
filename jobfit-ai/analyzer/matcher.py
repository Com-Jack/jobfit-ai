"""匹配分析核心逻辑"""

import json
from utils.llm import chat
from analyzer.prompts import MATCH_SYSTEM, MATCH_USER


def analyze_match(resume: str, job: str) -> dict:
    """分析简历与岗位的匹配度

    Args:
        resume: 简历文本
        job: 岗位JD文本

    Returns:
        匹配分析结果字典
    """
    prompt = MATCH_USER.format(resume=resume, job=job)
    response = chat(MATCH_SYSTEM, prompt, temperature=0.3)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        # 尝试提取JSON部分
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(response[start:end])
        else:
            result = {
                "score": 0,
                "matched_skills": [],
                "missing_skills": [],
                "matched_experience": [],
                "missing_experience": [],
                "strengths": [],
                "weaknesses": [],
                "suggestions": ["分析结果解析失败，请重试"],
                "raw_response": response,
            }

    return result
