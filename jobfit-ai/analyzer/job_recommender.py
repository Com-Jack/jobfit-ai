"""岗位推荐 - 基于简历技能栈+项目经验匹配推荐岗位，分析适配度"""

import json
from utils.llm import chat
from analyzer.prompts import (
    JOB_RECOMMEND_SYSTEM, JOB_RECOMMEND_USER,
    SEARCH_RESULTS_SECTION, NO_SEARCH_RESULTS,
)


def recommend_jobs(parsed_resume: dict, search_results: dict = None) -> dict:
    """基于简历信息推荐岗位并分析适配度

    策略：
    1. 如果有搜索结果，基于搜索到的岗位进行适配度分析
    2. 如果没有搜索结果，让AI根据简历技能栈和项目经验生成推荐岗位

    Args:
        parsed_resume: 解析后的简历结构化信息
        search_results: 搜索结果（可选）

    Returns:
        推荐岗位列表 + 适配度分析
    """
    # 构建搜索结果上下文
    search_context = ""
    if search_results and search_results.get("jobs"):
        jobs_text = []
        for i, job in enumerate(search_results["jobs"][:15], 1):
            jobs_text.append(
                f"{i}. {job.get('title', '')} | {job.get('company', '')} | "
                f"{job.get('salary', '')} | {job.get('location', '')} | "
                f"标签: {job.get('tags', '')} | 来源: {job.get('platform', '')}"
            )
        search_context = SEARCH_RESULTS_SECTION.format(
            search_results="\n".join(jobs_text)
        )
    else:
        search_context = NO_SEARCH_RESULTS

    prompt = JOB_RECOMMEND_USER.format(
        name=parsed_resume.get("name", "未知"),
        target_positions="、".join(parsed_resume.get("target_positions", [])),
        target_cities="、".join(parsed_resume.get("target_cities", [])),
        expected_salary=parsed_resume.get("expected_salary", "未指定"),
        skills="、".join(parsed_resume.get("skills", [])),
        skill_categories=json.dumps(
            parsed_resume.get("skill_categories", {}),
            ensure_ascii=False
        ),
        experience_years=parsed_resume.get("experience_years", 0),
        projects="\n".join(
            f"- {p.get('name', '')}: {p.get('description', '')}"
            for p in parsed_resume.get("projects", [])
        ),
        education=parsed_resume.get("education", ""),
        search_results_section=search_context,
    )

    response = chat(JOB_RECOMMEND_SYSTEM, prompt, temperature=0.5)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(response[start:end])
        else:
            result = {
                "recommendations": [],
                "overall_suggestions": [],
                "raw_response": response,
            }

    # 补充搜索URL到推荐结果中
    if search_results and search_results.get("search_urls"):
        result["search_urls"] = [
            {"platform": u["platform"], "url": u["url"]}
            for u in search_results["search_urls"]
        ]

    return result
