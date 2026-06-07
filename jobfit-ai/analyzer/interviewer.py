"""面试题生成与模拟面试"""

import json
from utils.llm import chat
from analyzer.prompts import INTERVIEW_SYSTEM, INTERVIEW_USER, MOCK_EVAL_SYSTEM, MOCK_EVAL_USER


def generate_interview_questions(job: str, count: int = 5) -> dict:
    """根据岗位要求生成面试题

    Args:
        job: 岗位JD文本
        count: 生成题目数量

    Returns:
        面试题字典
    """
    prompt = INTERVIEW_USER.format(job=job, count=count)
    response = chat(INTERVIEW_SYSTEM, prompt, temperature=0.7)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(response[start:end])
        else:
            result = {
                "questions": [],
                "raw_response": response,
            }

    return result


def evaluate_answer(question: str, answer: str, job: str) -> dict:
    """评估模拟面试回答

    Args:
        question: 面试问题
        answer: 候选人回答
        job: 岗位JD文本

    Returns:
        评估结果字典
    """
    prompt = MOCK_EVAL_USER.format(question=question, answer=answer, job=job)
    response = chat(MOCK_EVAL_SYSTEM, prompt, temperature=0.3)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(response[start:end])
        else:
            result = {
                "score": 0,
                "strengths": [],
                "weaknesses": [],
                "improved_answer": "解析失败",
                "tips": ["评估结果解析失败，请重试"],
                "raw_response": response,
            }

    return result
