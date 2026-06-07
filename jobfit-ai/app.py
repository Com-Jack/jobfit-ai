"""JobFit AI - Streamlit Web界面 - 全局数据互通版"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from analyzer.matcher import analyze_match
from analyzer.optimizer import optimize_resume
from analyzer.interviewer import generate_interview_questions, evaluate_answer
from analyzer.resume_parser import parse_resume
from analyzer.job_searcher import search_multi_keywords, generate_search_urls
from analyzer.job_recommender import recommend_jobs
from utils.report import generate_report

# 页面配置
st.set_page_config(
    page_title="JobFit AI",
    page_icon="🎯",
    layout="wide",
)

# ==================== 全局共享数据 ====================
# 所有页面共享的数据，避免重复上传
if "shared_resume" not in st.session_state:
    st.session_state.shared_resume = ""
if "shared_jd" not in st.session_state:
    st.session_state.shared_jd = ""
if "shared_parsed_resume" not in st.session_state:
    st.session_state.shared_parsed_resume = None
if "shared_recommendations" not in st.session_state:
    st.session_state.shared_recommendations = None
if "shared_match_result" not in st.session_state:
    st.session_state.shared_match_result = None
if "shared_optimize_result" not in st.session_state:
    st.session_state.shared_optimize_result = None
if "shared_interview_questions" not in st.session_state:
    st.session_state.shared_interview_questions = None
if "shared_search_results" not in st.session_state:
    st.session_state.shared_search_results = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "智能推荐"
if "interview_q_index" not in st.session_state:
    st.session_state.interview_q_index = 0
if "interview_scores" not in st.session_state:
    st.session_state.interview_scores = []
if "selected_job_title" not in st.session_state:
    st.session_state.selected_job_title = ""
if "selected_job_jd" not in st.session_state:
    st.session_state.selected_job_jd = ""


def extract_text_from_file(uploaded_file) -> str:
    """从上传文件中提取文本，支持txt/md/pdf/docx"""
    if uploaded_file is None:
        return None
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".pdf"):
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            text_parts = [page.extract_text() for page in reader.pages if page.extract_text()]
            content = "\n".join(text_parts)
            if not content.strip():
                st.warning("PDF未提取到文本，可能是扫描件，建议复制内容粘贴")
                return None
            return content
        except Exception as e:
            st.error(f"PDF解析失败：{e}")
            return None
    if file_name.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(uploaded_file)
            content = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            if not content.strip():
                st.warning("Word文件未提取到文本内容")
                return None
            return content
        except Exception as e:
            st.error(f"Word解析失败：{e}")
            return None
    try:
        return uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        try:
            uploaded_file.seek(0)
            return uploaded_file.read().decode("gbk")
        except Exception:
            st.error("文件编码无法识别")
            return None


def make_upload_callback(target_key):
    """文件上传回调"""
    def callback():
        uploader_key = f"_upload_{target_key}"
        uploaded_file = st.session_state.get(uploader_key)
        if uploaded_file is not None:
            content = extract_text_from_file(uploaded_file)
            if content:
                st.session_state[target_key] = content
    return callback


def render_file_uploader(label, target_key, file_types=None):
    """渲染文件上传组件"""
    if file_types is None:
        file_types = ["txt", "md", "pdf", "docx"]
    uploader_key = f"_upload_{target_key}"
    st.file_uploader(label, type=file_types, key=uploader_key,
                     on_change=make_upload_callback(target_key))


def navigate_to(page_name):
    """跳转到指定页面"""
    st.session_state.current_page = page_name


def show_data_badge():
    """显示当前共享数据状态"""
    badges = []
    if st.session_state.shared_resume:
        badges.append("简历已加载")
    if st.session_state.shared_jd:
        badges.append("JD已加载")
    if st.session_state.shared_parsed_resume:
        badges.append("简历已解析")
    if st.session_state.shared_recommendations:
        badges.append("推荐已生成")
    if badges:
        st.markdown(" | ".join(f"`{b}`" for b in badges))


# ==================== 侧边栏导航 ====================
with st.sidebar:
    st.header("JobFit AI")
    from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
    if LLM_API_KEY:
        st.success("API Key 已配置")
        st.info(f"模型：{LLM_MODEL}")
    else:
        st.error("API Key 未配置")
        st.markdown("参考 `.env.example`")

    st.divider()

    page_options = [
        "智能推荐",
        "岗位搜索",
        "匹配分析",
        "简历优化",
        "面试题生成",
        "模拟面试",
    ]
    current = st.radio(
        "功能导航",
        page_options,
        index=page_options.index(st.session_state.current_page) if st.session_state.current_page in page_options else 0,
        key="_page_nav",
    )
    st.session_state.current_page = current

    st.divider()
    st.markdown("**共享数据状态**")
    if st.session_state.shared_resume:
        preview = st.session_state.shared_resume[:30].replace("\n", " ")
        st.markdown(f"简历：`{preview}...`")
    else:
        st.markdown("简历：`未加载`")
    if st.session_state.shared_jd:
        preview = st.session_state.shared_jd[:30].replace("\n", " ")
        st.markdown(f"JD：`{preview}...`")
    else:
        st.markdown("JD：`未加载`")

    st.divider()
    if st.button("清除所有数据", key="clear_all"):
        for key in ["shared_resume", "shared_jd", "shared_parsed_resume",
                     "shared_recommendations", "shared_match_result",
                     "shared_optimize_result", "shared_interview_questions",
                     "shared_search_results", "selected_job_title", "selected_job_jd"]:
            st.session_state[key] = "" if key in ["shared_resume", "shared_jd", "selected_job_title", "selected_job_jd"] else None
        st.session_state.interview_q_index = 0
        st.session_state.interview_scores = []
        st.rerun()

# ==================== 主内容区 ====================
st.title("JobFit AI - 简历岗位智能匹配与面试分析器")
show_data_badge()

# ==================== 页面1: 智能推荐 ====================
if current == "智能推荐":
    st.header("智能推荐：解析简历→搜索岗位→推荐分析→模拟面试")
    st.markdown("输入简历，AI自动提取意向岗位和技能，搜索求职平台，推荐最匹配的岗位并分析适配度。")

    render_file_uploader("上传简历文件（支持拖拽，TXT/MD/PDF/Word）", target_key="shared_resume")
    resume_text = st.text_area(
        "简历内容",
        value=st.session_state.shared_resume,
        height=300,
        placeholder="粘贴简历内容（请包含求职意向：意向岗位、期望城市、期望薪资）...\n也可上传文件自动填入",
        key="shared_resume",
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("加载示例简历", key="load_sample"):
            with open("data/sample_resume.txt", "r", encoding="utf-8") as f:
                st.session_state.shared_resume = f.read()
            st.rerun()

    with col_btn2:
        if st.button("开始智能推荐", type="primary", key="rec_btn"):
            if not resume_text:
                st.warning("请输入简历内容")
            elif not LLM_API_KEY:
                st.error("API Key 未配置")
            else:
                with st.spinner("Step 1/3: 正在解析简历..."):
                    parsed = parse_resume(resume_text)
                    st.session_state.shared_parsed_resume = parsed

                positions = parsed.get("target_positions", [])
                cities = parsed.get("target_cities", [])

                if not positions:
                    st.warning("简历中未找到意向岗位，请确保包含「求职意向」部分")
                else:
                    with st.spinner("Step 2/3: 正在搜索求职平台..."):
                        search_results = search_multi_keywords(positions, cities if cities else ["北京"])
                        st.session_state.shared_search_results = search_results

                    with st.spinner("Step 3/3: 正在AI推荐岗位并分析适配度..."):
                        rec_result = recommend_jobs(parsed, search_results)
                        st.session_state.shared_recommendations = rec_result

    # 展示解析结果
    if st.session_state.shared_parsed_resume:
        parsed = st.session_state.shared_parsed_resume
        with st.expander("简历解析结果", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**姓名：**{parsed.get('name', '未知')}")
                st.markdown(f"**意向岗位：**{'、'.join(parsed.get('target_positions', []))}")
                st.markdown(f"**期望城市：**{'、'.join(parsed.get('target_cities', []))}")
                st.markdown(f"**期望薪资：**{parsed.get('expected_salary', '未指定')}")
            with col_b:
                st.markdown(f"**工作年限：**{parsed.get('experience_years', 0)}年")
                st.markdown(f"**学历：**{parsed.get('education', '未指定')}")
                skills = parsed.get("skills", [])
                if skills:
                    st.markdown(f"**技能：**{'、'.join(skills[:15])}")

    # 展示推荐结果
    if st.session_state.shared_recommendations:
        rec_data = st.session_state.shared_recommendations

        search_urls = rec_data.get("search_urls", [])
        if search_urls:
            with st.expander("求职平台搜索链接"):
                for u in search_urls:
                    st.markdown(f"- [{u['platform']}]({u['url']})")

        recommendations = rec_data.get("recommendations", [])
        if recommendations:
            st.markdown("### 推荐岗位")

            for rec in recommendations:
                score = rec.get("fit_score", 0)
                score_color = "green" if score >= 70 else "orange" if score >= 50 else "red"

                with st.expander(
                    f"#{rec.get('rank', '?')} {rec.get('job_title', '')} - "
                    f"适配度 :{score_color}[**{score}**] - "
                    f"{rec.get('salary_range', '')} - {rec.get('city', '')}",
                    expanded=True,
                ):
                    col_info, col_match = st.columns(2)
                    with col_info:
                        st.markdown(f"**公司类型：**{rec.get('company_type', '')}")
                        st.markdown(f"**薪资范围：**{rec.get('salary_range', '')}")
                        st.markdown(f"**推荐城市：**{rec.get('city', '')}")
                        st.markdown(f"**推荐理由：**{rec.get('why_recommended', '')}")
                    with col_match:
                        matched = rec.get("matched_skills", [])
                        if matched:
                            st.markdown("**匹配技能：**")
                            for s in matched:
                                st.markdown(f"- :green[{s}]")
                        missing = rec.get("missing_skills", [])
                        if missing:
                            st.markdown("**缺失技能：**")
                            for s in missing:
                                st.markdown(f"- :red[{s}]")

                    jd_items = rec.get("jd_summary", [])
                    if jd_items:
                        st.markdown("**典型JD核心要求：**")
                        for item in jd_items:
                            st.markdown(f"- {item}")

                    opt_suggestions = rec.get("optimization_suggestions", [])
                    if opt_suggestions:
                        st.markdown("**简历优化建议：**")
                        for s in opt_suggestions:
                            st.markdown(f"- {s}")

                    # 操作按钮行
                    jd_text = "; ".join(jd_items)
                    col_act1, col_act2, col_act3 = st.columns(3)

                    with col_act1:
                        if st.button(f"匹配分析", key=f"match_go_{rec.get('rank', 0)}"):
                            st.session_state.shared_jd = jd_text
                            st.session_state.shared_match_result = None
                            navigate_to("匹配分析")
                            st.rerun()

                    with col_act2:
                        if st.button(f"简历优化", key=f"opt_go_{rec.get('rank', 0)}"):
                            st.session_state.shared_jd = jd_text
                            st.session_state.shared_optimize_result = None
                            navigate_to("简历优化")
                            st.rerun()

                    with col_act3:
                        if st.button(f"模拟面试", key=f"mock_go_{rec.get('rank', 0)}"):
                            st.session_state.shared_jd = jd_text
                            st.session_state.selected_job_title = rec.get("job_title", "")
                            st.session_state.selected_job_jd = jd_text
                            st.session_state.shared_interview_questions = None
                            st.session_state.interview_q_index = 0
                            st.session_state.interview_scores = []
                            navigate_to("模拟面试")
                            st.rerun()

        overall = rec_data.get("overall_suggestions", [])
        if overall:
            st.markdown("### 整体求职策略建议")
            for i, s in enumerate(overall, 1):
                st.markdown(f"{i}. {s}")

# ==================== 页面2: 岗位搜索 ====================
elif current == "岗位搜索":
    st.header("岗位搜索")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        search_keyword = st.text_input("搜索关键词", placeholder="如：Python开发工程师", key="search_keyword")
    with col_s2:
        search_city = st.selectbox("城市", [
            "北京", "上海", "广州", "深圳", "杭州", "成都",
            "南京", "武汉", "西安", "重庆", "苏州", "天津",
        ], key="search_city")

    if st.button("搜索岗位", type="primary", key="search_btn"):
        if not search_keyword:
            st.warning("请输入搜索关键词")
        else:
            with st.spinner("正在搜索求职平台..."):
                result = search_multi_keywords([search_keyword], [search_city])
                st.session_state.shared_search_results = result

            jobs = result.get("jobs", [])
            urls = result.get("search_urls", [])

            if jobs:
                st.success(f"搜索到 {len(jobs)} 个岗位")
                for i, job in enumerate(jobs, 1):
                    st.markdown(
                        f"**{i}. {job.get('title', '')}** | "
                        f"{job.get('company', '')} | "
                        f"{job.get('salary', '')} | "
                        f"{job.get('location', '')} | "
                        f"*来源: {job.get('platform', '')}*"
                    )
                    if job.get("tags"):
                        st.caption(job["tags"])
            else:
                st.warning("未能从平台抓取到岗位数据，请通过以下链接手动搜索：")

            if urls:
                st.markdown("### 求职平台搜索链接")
                for u in urls:
                    st.markdown(f"- [{u['platform']}]({u['url']})")

# ==================== 页面3: 匹配分析 ====================
elif current == "匹配分析":
    st.header("简历-岗位匹配分析")

    col1, col2 = st.columns(2)
    with col1:
        render_file_uploader("上传简历文件（TXT/MD/PDF/Word）", target_key="shared_resume")
        resume_input = st.text_area(
            "简历内容",
            value=st.session_state.shared_resume,
            height=300,
            placeholder="粘贴简历内容或上传文件...\n从「智能推荐」跳转时自动填入",
            key="shared_resume",
        )
        if st.button("加载示例简历", key="load_match_resume"):
            with open("data/sample_resume.txt", "r", encoding="utf-8") as f:
                st.session_state.shared_resume = f.read()
            st.rerun()

    with col2:
        render_file_uploader("上传岗位JD文件（TXT/MD/PDF/Word）", target_key="shared_jd")
        job_input = st.text_area(
            "岗位JD",
            value=st.session_state.shared_jd,
            height=300,
            placeholder="粘贴岗位JD或上传文件...\n从「智能推荐」跳转时自动填入",
            key="shared_jd",
        )
        if st.button("加载示例JD", key="load_match_jd"):
            with open("data/sample_jd.txt", "r", encoding="utf-8") as f:
                st.session_state.shared_jd = f.read()
            st.rerun()

    if st.button("开始匹配分析", type="primary", key="match_btn"):
        if not resume_input or not job_input:
            st.warning("请输入简历和岗位JD内容")
        elif not LLM_API_KEY:
            st.error("API Key 未配置")
        else:
            with st.spinner("AI正在分析匹配度..."):
                result = analyze_match(resume_input, job_input)
                st.session_state.shared_match_result = result

    # 展示匹配结果
    if st.session_state.shared_match_result:
        result = st.session_state.shared_match_result
        score = result.get("score", 0)
        score_color = "green" if score >= 80 else "orange" if score >= 60 else "red"
        st.markdown(f"### 匹配度评分：:{score_color}[**{score}**] / 100")

        col_a, col_b = st.columns(2)
        with col_a:
            matched = result.get("matched_skills", [])
            if matched:
                st.markdown("#### 匹配的技能")
                for skill in matched:
                    st.markdown(f"- :green[{skill}]")
            strengths = result.get("strengths", [])
            if strengths:
                st.markdown("#### 优势")
                for s in strengths:
                    st.markdown(f"- {s}")
        with col_b:
            missing = result.get("missing_skills", [])
            if missing:
                st.markdown("#### 缺失的技能")
                for skill in missing:
                    st.markdown(f"- :red[{skill}]")
            weaknesses = result.get("weaknesses", [])
            if weaknesses:
                st.markdown("#### 不足")
                for w in weaknesses:
                    st.markdown(f"- {w}")

        suggestions = result.get("suggestions", [])
        if suggestions:
            st.markdown("#### 改进建议")
            for i, s in enumerate(suggestions, 1):
                st.markdown(f"{i}. {s}")

        # 跳转按钮
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            if st.button("前往简历优化", key="match_to_opt"):
                st.session_state.shared_optimize_result = None
                navigate_to("简历优化")
                st.rerun()
        with col_j2:
            if st.button("前往模拟面试", key="match_to_mock"):
                st.session_state.shared_interview_questions = None
                st.session_state.interview_q_index = 0
                st.session_state.interview_scores = []
                navigate_to("模拟面试")
                st.rerun()

# ==================== 页面4: 简历优化 ====================
elif current == "简历优化":
    st.header("简历优化建议")

    col1, col2 = st.columns(2)
    with col1:
        render_file_uploader("上传简历文件（TXT/MD/PDF/Word）", target_key="shared_resume")
        opt_resume = st.text_area(
            "简历内容",
            value=st.session_state.shared_resume,
            height=300,
            placeholder="粘贴简历内容或上传文件...\n从其他页面跳转时自动填入",
            key="shared_resume",
        )
        if st.button("加载示例简历", key="load_opt_resume"):
            with open("data/sample_resume.txt", "r", encoding="utf-8") as f:
                st.session_state.shared_resume = f.read()
            st.rerun()
    with col2:
        render_file_uploader("上传岗位JD文件（TXT/MD/PDF/Word）", target_key="shared_jd")
        opt_job = st.text_area(
            "目标岗位JD",
            value=st.session_state.shared_jd,
            height=300,
            placeholder="粘贴岗位JD或上传文件...\n从其他页面跳转时自动填入",
            key="shared_jd",
        )
        if st.button("加载示例JD", key="load_opt_jd"):
            with open("data/sample_jd.txt", "r", encoding="utf-8") as f:
                st.session_state.shared_jd = f.read()
            st.rerun()

    if st.button("生成优化建议", type="primary", key="opt_btn"):
        if not opt_resume or not opt_job:
            st.warning("请输入简历和岗位JD内容")
        elif not LLM_API_KEY:
            st.error("API Key 未配置")
        else:
            with st.spinner("AI正在生成优化建议..."):
                result = optimize_resume(opt_resume, opt_job)
                st.session_state.shared_optimize_result = result

    if st.session_state.shared_optimize_result:
        result = st.session_state.shared_optimize_result
        st.markdown("### 整体评价")
        st.info(result.get("overall_assessment", ""))

        keywords = result.get("keyword_suggestions", [])
        if keywords:
            st.markdown("### 关键词建议")
            for kw in keywords:
                st.markdown(f"- **{kw.get('keyword', '')}**：{kw.get('reason', '')}（建议放在{kw.get('where', '')}）")

        exps = result.get("experience_optimizations", [])
        if exps:
            st.markdown("### 经历描述优化")
            for exp in exps:
                st.markdown(f"**原文：**{exp.get('original', '')}")
                st.markdown(f"**建议：**{exp.get('suggested', '')}")
                st.markdown(f"**原因：**{exp.get('reason', '')}")
                st.divider()

        actions = result.get("action_items", [])
        if actions:
            st.markdown("### 行动清单")
            for i, a in enumerate(actions, 1):
                st.markdown(f"{i}. {a}")

        # 跳转按钮
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            if st.button("前往匹配分析", key="opt_to_match"):
                st.session_state.shared_match_result = None
                navigate_to("匹配分析")
                st.rerun()
        with col_j2:
            if st.button("前往模拟面试", key="opt_to_mock"):
                st.session_state.shared_interview_questions = None
                st.session_state.interview_q_index = 0
                st.session_state.interview_scores = []
                navigate_to("模拟面试")
                st.rerun()

# ==================== 页面5: 面试题生成 ====================
elif current == "面试题生成":
    st.header("面试题生成")

    render_file_uploader("上传岗位JD文件（TXT/MD/PDF/Word）", target_key="shared_jd")
    interview_job = st.text_area(
        "岗位JD",
        value=st.session_state.shared_jd,
        height=300,
        placeholder="粘贴岗位JD或上传文件...\n从其他页面跳转时自动填入",
        key="shared_jd",
    )

    question_count = st.slider("生成题目数量", min_value=1, max_value=10, value=5, key="q_count")

    if st.button("生成面试题", type="primary", key="interview_btn"):
        if not interview_job:
            st.warning("请输入岗位JD内容")
        elif not LLM_API_KEY:
            st.error("API Key 未配置")
        else:
            with st.spinner(f"AI正在生成 {question_count} 道面试题..."):
                result = generate_interview_questions(interview_job, question_count)
                st.session_state.shared_interview_questions = result.get("questions", [])

    if st.session_state.shared_interview_questions:
        questions = st.session_state.shared_interview_questions
        for q in questions:
            with st.expander(f"面试题 #{q.get('id', '?')} - {q.get('category', '')}", expanded=True):
                st.markdown(f"**问题：**{q.get('question', '')}")
                st.markdown(f"**考察点：**{q.get('intent', '')}")
                st.markdown(f"**参考答案：**{q.get('reference_answer', '')}")
                criteria = q.get("evaluation_criteria", [])
                if criteria:
                    st.markdown("**评分标准：**")
                    for c in criteria:
                        st.markdown(f"- {c}")

        if st.button("前往模拟面试练习这些题目", type="primary", key="interview_to_mock"):
            st.session_state.interview_q_index = 0
            st.session_state.interview_scores = []
            navigate_to("模拟面试")
            st.rerun()

# ==================== 页面6: 模拟面试 ====================
elif current == "模拟面试":
    st.header("模拟面试")

    # 确定JD来源
    if st.session_state.selected_job_title:
        st.info(f"推荐岗位：**{st.session_state.selected_job_title}**")
        mock_job = st.session_state.selected_job_jd or st.session_state.shared_jd
    else:
        mock_job = st.session_state.shared_jd

    render_file_uploader("上传岗位JD文件（TXT/MD/PDF/Word）", target_key="shared_jd")
    mock_job_input = st.text_area(
        "岗位JD",
        value=mock_job,
        height=200,
        placeholder="粘贴岗位JD或上传文件...\n从「智能推荐」跳转时自动填入",
        key="shared_jd",
    )

    mock_count = st.slider("面试题目数量", min_value=1, max_value=5, value=3, key="mock_count")

    if st.button("开始模拟面试", type="primary", key="mock_start"):
        if not mock_job_input:
            st.warning("请输入岗位JD内容")
        elif not LLM_API_KEY:
            st.error("API Key 未配置")
        else:
            with st.spinner("AI正在准备面试题..."):
                result = generate_interview_questions(mock_job_input, mock_count)
                st.session_state.shared_interview_questions = result.get("questions", [])
                st.session_state.interview_q_index = 0
                st.session_state.interview_scores = []

    # 面试过程
    if st.session_state.shared_interview_questions:
        questions = st.session_state.shared_interview_questions
        idx = st.session_state.interview_q_index

        if idx < len(questions):
            q = questions[idx]
            st.markdown(f"### 面试题 #{q.get('id', '?')}（{q.get('category', '')}）")
            st.markdown(f"**{q.get('question', '')}**")
            st.caption(f"考察点：{q.get('intent', '')}")

            answer = st.text_area("你的回答", height=200, key=f"answer_{idx}")

            if st.button("提交回答", key=f"submit_{idx}"):
                if not answer.strip():
                    st.warning("请输入你的回答")
                else:
                    with st.spinner("AI正在评估你的回答..."):
                        eval_result = evaluate_answer(q.get("question", ""), answer, mock_job_input)

                    score = eval_result.get("score", 0)
                    st.markdown(f"### 回答评分：**{score}** / 10")

                    for s in eval_result.get("strengths", []):
                        st.markdown(f"- :green[{s}]")
                    for w in eval_result.get("weaknesses", []):
                        st.markdown(f"- :red[{w}]")

                    improved = eval_result.get("improved_answer", "")
                    if improved:
                        st.markdown("**改进后的参考回答：**")
                        st.info(improved)

                    for t in eval_result.get("tips", []):
                        st.markdown(f"- {t}")

                    st.session_state.interview_scores.append(score)
                    st.session_state.interview_q_index = idx + 1
                    st.rerun()
        else:
            scores = st.session_state.interview_scores
            if scores:
                avg = sum(scores) / len(scores)
                st.markdown("### 模拟面试总结")
                st.markdown(f"共回答 **{len(scores)}** 题，平均得分 **{avg:.1f}** / 10")
                for i, s in enumerate(scores):
                    st.markdown(f"- 题目{i+1}：{s} / 10")

            col_end1, col_end2 = st.columns(2)
            with col_end1:
                if st.button("前往简历优化", key="mock_to_opt"):
                    st.session_state.shared_optimize_result = None
                    navigate_to("简历优化")
                    st.rerun()
            with col_end2:
                if st.button("重新开始面试", key="mock_restart"):
                    st.session_state.shared_interview_questions = None
                    st.session_state.interview_q_index = 0
                    st.session_state.interview_scores = []
                    st.session_state.selected_job_title = ""
                    st.session_state.selected_job_jd = ""
                    st.rerun()
