"""所有Prompt模板"""

# ========== 匹配分析 ==========
MATCH_SYSTEM = """你是一位资深猎头和职业规划师，擅长分析简历与岗位的匹配程度。
请用中文回答，输出必须是严格的JSON格式，不要包含任何其他文字。"""

MATCH_USER = """请分析以下简历与岗位的匹配程度：

【简历内容】
{resume}

【岗位要求】
{job}

请按以下JSON格式输出：
{{
  "score": <匹配度评分1-100的整数>,
  "matched_skills": ["匹配的技能1", "匹配的技能2"],
  "missing_skills": ["缺失的技能1", "缺失的技能2"],
  "matched_experience": ["匹配的经历1"],
  "missing_experience": ["缺失的经历1"],
  "strengths": ["优势1", "优势2"],
  "weaknesses": ["不足1", "不足2"],
  "suggestions": ["改进建议1", "改进建议2", "改进建议3"]
}}"""

# ========== 简历优化 ==========
OPTIMIZE_SYSTEM = """你是一位资深简历优化顾问，擅长根据目标岗位定制简历。
请用中文回答，输出必须是严格的JSON格式，不要包含任何其他文字。"""

OPTIMIZE_USER = """请根据目标岗位，给出简历优化建议：

【简历内容】
{resume}

【目标岗位】
{job}

请按以下JSON格式输出：
{{
  "overall_assessment": "简历整体评价（2-3句话）",
  "keyword_suggestions": [
    {{"keyword": "建议添加的关键词", "reason": "原因", "where": "建议放在简历哪个位置"}}
  ],
  "experience_optimizations": [
    {{"original": "原文描述", "suggested": "优化后描述", "reason": "优化原因"}}
  ],
  "structure_suggestions": ["结构建议1", "结构建议2"],
  "action_items": ["具体行动1", "具体行动2", "具体行动3"]
}}"""

# ========== 面试题生成 ==========
INTERVIEW_SYSTEM = """你是一位资深面试官，擅长根据岗位要求设计有深度的面试题。
请用中文回答，输出必须是严格的JSON格式，不要包含任何其他文字。"""

INTERVIEW_USER = """请根据以下岗位要求，生成{count}道面试题：

【岗位要求】
{job}

请按以下JSON格式输出：
{{
  "questions": [
    {{
      "id": 1,
      "category": "技术/行为/项目/场景",
      "question": "面试题内容",
      "intent": "考察点",
      "reference_answer": "参考答案要点",
      "evaluation_criteria": ["评分标准1", "评分标准2", "评分标准3"]
    }}
  ]
}}"""

# ========== 模拟面试评估 ==========
MOCK_EVAL_SYSTEM = """你是一位资深面试官，正在评估候选人的面试回答。
请用中文回答，输出必须是严格的JSON格式，不要包含任何其他文字。"""

MOCK_EVAL_USER = """请评估以下面试回答：

【面试问题】
{question}

【岗位要求】
{job}

【候选人回答】
{answer}

请按以下JSON格式输出：
{{
  "score": <评分1-10的整数>,
  "strengths": ["回答亮点1", "回答亮点2"],
  "weaknesses": ["回答不足1", "回答不足2"],
  "improved_answer": "改进后的参考回答",
  "tips": ["改进建议1", "改进建议2"]
}}"""

# ========== 简历解析 ==========
RESUME_PARSE_SYSTEM = """你是一位资深HR和简历分析专家，擅长从简历中提取结构化信息。
请用中文回答，输出必须是严格的JSON格式，不要包含任何其他文字。"""

RESUME_PARSE_USER = """请从以下简历中提取结构化信息：

【简历内容】
{resume}

请按以下JSON格式输出：
{{
  "name": "姓名",
  "target_positions": ["意向岗位1", "意向岗位2"],
  "target_cities": ["期望城市1", "期望城市2"],
  "expected_salary": "期望薪资（如25K-35K，未提及则填未指定）",
  "skills": ["技能1", "技能2", "技能3"],
  "skill_categories": {{
    "编程语言": ["Python", "SQL"],
    "框架": ["FastAPI"],
    "数据库": ["PostgreSQL"],
    "工具": ["Docker"],
    "其他": ["微服务架构"]
  }},
  "experience_years": <工作年限整数>,
  "projects": [
    {{"name": "项目名称", "description": "项目描述和关键成果"}}
  ],
  "education": "最高学历（学校+专业+学位）",
  "work_experiences": [
    {{"company": "公司名", "position": "职位", "duration": "时间段", "highlights": ["亮点1"]}}
  ]
}}"""

# ========== 岗位推荐 ==========
JOB_RECOMMEND_SYSTEM = """你是一位资深猎头，擅长根据求职者的技能栈和项目经验推荐合适的岗位，并分析适配度。
请用中文回答，输出必须是严格的JSON格式，不要包含任何其他文字。"""

JOB_RECOMMEND_USER = """请根据以下求职者信息推荐合适的岗位，并分析适配度：

【求职者信息】
姓名：{name}
意向岗位：{target_positions}
期望城市：{target_cities}
期望薪资：{expected_salary}
技能列表：{skills}
技能分类：{skill_categories}
工作年限：{experience_years}年
项目经历：
{projects}
学历：{education}

{search_results_section}

请按以下JSON格式输出：
{{
  "recommendations": [
    {{
      "rank": 1,
      "job_title": "推荐岗位名称",
      "company_type": "推荐公司类型（如头部互联网/创业公司/外企）",
      "salary_range": "推荐薪资范围",
      "city": "推荐城市",
      "fit_score": <适配度1-100整数>,
      "matched_skills": ["匹配的技能1", "匹配的技能2"],
      "missing_skills": ["缺失的技能1"],
      "matched_projects": ["相关的项目经历1"],
      "why_recommended": "推荐理由（2-3句话）",
      "jd_summary": "该岗位典型JD摘要（3-5条核心要求）",
      "optimization_suggestions": ["简历优化建议1", "简历优化建议2"]
    }}
  ],
  "overall_suggestions": [
    "整体求职策略建议1",
    "整体求职策略建议2",
    "整体求职策略建议3"
  ]
}}

如果上方有搜索结果，请优先基于搜索到的实际岗位进行推荐和分析，适配度要结合实际岗位要求评估。
如果没有搜索结果，请根据求职者的技能栈和项目经验，推荐最匹配的5个岗位方向。
"""

SEARCH_RESULTS_SECTION = """【搜索到的岗位（来自Boss直聘/猎聘/智联招聘）】
{search_results}"""

NO_SEARCH_RESULTS = "（暂无平台搜索结果，请根据求职者信息推荐岗位）"""
