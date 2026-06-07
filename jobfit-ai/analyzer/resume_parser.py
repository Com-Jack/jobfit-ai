"""简历智能解析 - 提取意向岗位、城市、薪资、技能栈、项目经验"""

import json
from utils.llm import chat
from analyzer.prompts import RESUME_PARSE_SYSTEM, RESUME_PARSE_USER


def parse_resume(resume: str) -> dict:
    """解析简历，提取结构化信息

    Args:
        resume: 简历文本

    Returns:
        结构化简历信息字典
    """
    prompt = RESUME_PARSE_USER.format(resume=resume)
    response = chat(RESUME_PARSE_SYSTEM, prompt, temperature=0.2)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(response[start:end])
        else:
            result = {
                "name": "未知",
                "target_positions": [],
                "target_cities": [],
                "expected_salary": "",
                "skills": [],
                "skill_categories": {},
                "experience_years": 0,
                "projects": [],
                "education": "",
                "raw_response": response,
            }

    return result
