"""JobFit AI - 简历岗位智能匹配与面试分析器 CLI入口"""

import sys
import os

# 将项目根目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import DEFAULT_INTERVIEW_COUNT, MAX_INPUT_LENGTH
from analyzer.matcher import analyze_match
from analyzer.optimizer import optimize_resume
from analyzer.interviewer import generate_interview_questions, evaluate_answer
from analyzer.resume_parser import parse_resume
from analyzer.job_searcher import search_multi_keywords, generate_search_urls
from analyzer.job_recommender import recommend_jobs
from utils.report import generate_report, save_report

console = Console()


def read_file(filepath: str) -> str:
    """读取文件内容"""
    if not os.path.exists(filepath):
        console.print(f"[red]错误：文件不存在 {filepath}[/red]")
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if len(content) > MAX_INPUT_LENGTH:
        console.print(f"[yellow]警告：文件内容超过{MAX_INPUT_LENGTH}字符，已截断[/yellow]")
        content = content[:MAX_INPUT_LENGTH]
    return content


def print_match_result(result: dict):
    """美观打印匹配分析结果"""
    score = result.get("score", 0)

    # 评分颜色
    if score >= 80:
        score_color = "green"
    elif score >= 60:
        score_color = "yellow"
    else:
        score_color = "red"

    console.print(Panel(
        f"[{score_color}]{score}[/{score_color}] / 100",
        title="匹配度评分",
        expand=False,
    ))

    # 匹配技能
    matched = result.get("matched_skills", [])
    if matched:
        table = Table(title="匹配的技能")
        table.add_column("技能", style="green")
        for skill in matched:
            table.add_row(skill)
        console.print(table)

    # 缺失技能
    missing = result.get("missing_skills", [])
    if missing:
        table = Table(title="缺失的技能")
        table.add_column("技能", style="red")
        for skill in missing:
            table.add_row(skill)
        console.print(table)

    # 优势
    strengths = result.get("strengths", [])
    if strengths:
        console.print("\n[bold green]优势：[/bold green]")
        for s in strengths:
            console.print(f"  ✅ {s}")

    # 不足
    weaknesses = result.get("weaknesses", [])
    if weaknesses:
        console.print("\n[bold red]不足：[/bold red]")
        for w in weaknesses:
            console.print(f"  ❌ {w}")

    # 建议
    suggestions = result.get("suggestions", [])
    if suggestions:
        console.print("\n[bold cyan]改进建议：[/bold cyan]")
        for i, s in enumerate(suggestions, 1):
            console.print(f"  {i}. {s}")


def print_optimize_result(result: dict):
    """美观打印简历优化结果"""
    console.print(Panel(
        result.get("overall_assessment", ""),
        title="简历整体评价",
    ))

    # 关键词建议
    keywords = result.get("keyword_suggestions", [])
    if keywords:
        table = Table(title="关键词建议")
        table.add_column("关键词", style="cyan")
        table.add_column("原因")
        table.add_column("建议位置", style="yellow")
        for kw in keywords:
            table.add_row(kw.get("keyword", ""), kw.get("reason", ""), kw.get("where", ""))
        console.print(table)

    # 经历优化
    exps = result.get("experience_optimizations", [])
    if exps:
        console.print("\n[bold cyan]经历描述优化：[/bold cyan]")
        for exp in exps:
            console.print(f"  [red]原文：[/red]{exp.get('original', '')}")
            console.print(f"  [green]建议：[/green]{exp.get('suggested', '')}")
            console.print(f"  [yellow]原因：[/yellow]{exp.get('reason', '')}")
            console.print()

    # 行动项
    actions = result.get("action_items", [])
    if actions:
        console.print("[bold cyan]行动清单：[/bold cyan]")
        for i, a in enumerate(actions, 1):
            console.print(f"  {i}. {a}")


def print_interview_result(result: dict):
    """美观打印面试题结果"""
    questions = result.get("questions", [])
    if not questions:
        console.print("[yellow]未生成面试题[/yellow]")
        return

    for q in questions:
        console.print(Panel(
            f"[bold]{q.get('question', '')}[/bold]\n\n"
            f"[cyan]类型：[/cyan]{q.get('category', '')}\n"
            f"[cyan]考察点：[/cyan]{q.get('intent', '')}",
            title=f"面试题 #{q.get('id', '?')}",
        ))
        console.print(f"  [green]参考答案：[/green]{q.get('reference_answer', '')}")
        criteria = q.get("evaluation_criteria", [])
        if criteria:
            console.print("  [yellow]评分标准：[/yellow]")
            for c in criteria:
                console.print(f"    - {c}")
        console.print()


def print_eval_result(result: dict):
    """美观打印面试评估结果"""
    score = result.get("score", 0)
    score_color = "green" if score >= 7 else "yellow" if score >= 5 else "red"

    console.print(Panel(
        f"[{score_color}]{score}[/{score_color}] / 10",
        title="回答评分",
        expand=False,
    ))

    strengths = result.get("strengths", [])
    if strengths:
        console.print("[bold green]回答亮点：[/bold green]")
        for s in strengths:
            console.print(f"  ✅ {s}")

    weaknesses = result.get("weaknesses", [])
    if weaknesses:
        console.print("[bold red]回答不足：[/bold red]")
        for w in weaknesses:
            console.print(f"  ❌ {w}")

    improved = result.get("improved_answer", "")
    if improved:
        console.print(Panel(improved, title="改进后的参考回答"))

    tips = result.get("tips", [])
    if tips:
        console.print("[bold cyan]改进建议：[/bold cyan]")
        for t in tips:
            console.print(f"  💡 {t}")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """JobFit AI - 简历岗位智能匹配与面试分析器

    基于大模型API，帮助你分析简历与岗位匹配度、优化简历、准备面试。
    """
    pass


@cli.command()
@click.option("--resume", "-r", required=True, help="简历文件路径")
@click.option("--job", "-j", required=True, help="岗位JD文件路径")
@click.option("--output", "-o", default=None, help="导出报告路径（Markdown格式）")
def match(resume, job, output):
    """分析简历与岗位的匹配度"""
    resume_text = read_file(resume)
    job_text = read_file(job)

    console.print("[bold cyan]正在分析匹配度，调用AI分析中...[/bold cyan]")
    result = analyze_match(resume_text, job_text)

    print_match_result(result)

    if output:
        sections = {
            "匹配度评分": f"**{result.get('score', 0)} / 100**",
            "匹配的技能": "\n".join(f"- {s}" for s in result.get("matched_skills", [])),
            "缺失的技能": "\n".join(f"- {s}" for s in result.get("missing_skills", [])),
            "优势": "\n".join(f"- {s}" for s in result.get("strengths", [])),
            "不足": "\n".join(f"- {s}" for s in result.get("weaknesses", [])),
            "改进建议": "\n".join(f"{i}. {s}" for i, s in enumerate(result.get("suggestions", []), 1)),
        }
        report = generate_report("简历-岗位匹配分析报告", sections)
        save_report(report, output)
        console.print(f"\n[green]报告已保存至 {output}[/green]")


@cli.command()
@click.option("--resume", "-r", required=True, help="简历文件路径")
@click.option("--job", "-j", required=True, help="岗位JD文件路径")
@click.option("--output", "-o", default=None, help="导出报告路径（Markdown格式）")
def optimize(resume, job, output):
    """根据目标岗位优化简历"""
    resume_text = read_file(resume)
    job_text = read_file(job)

    console.print("[bold cyan]正在生成优化建议，调用AI分析中...[/bold cyan]")
    result = optimize_resume(resume_text, job_text)

    print_optimize_result(result)

    if output:
        sections = {
            "整体评价": result.get("overall_assessment", ""),
            "关键词建议": "\n".join(
                f"- **{kw.get('keyword', '')}**：{kw.get('reason', '')}（建议放在{kw.get('where', '')}）"
                for kw in result.get("keyword_suggestions", [])
            ),
            "行动清单": "\n".join(f"{i}. {a}" for i, a in enumerate(result.get("action_items", []), 1)),
        }
        report = generate_report("简历优化建议报告", sections)
        save_report(report, output)
        console.print(f"\n[green]报告已保存至 {output}[/green]")


@cli.command()
@click.option("--job", "-j", required=True, help="岗位JD文件路径")
@click.option("--count", "-n", default=DEFAULT_INTERVIEW_COUNT, help="生成题目数量")
@click.option("--output", "-o", default=None, help="导出报告路径（Markdown格式）")
def interview(job, count, output):
    """根据岗位要求生成面试题"""
    job_text = read_file(job)

    console.print(f"[bold cyan]正在生成 {count} 道面试题，调用AI生成中...[/bold cyan]")
    result = generate_interview_questions(job_text, count)

    print_interview_result(result)

    if output:
        questions_md = []
        for q in result.get("questions", []):
            questions_md.append(
                f"### 面试题 #{q.get('id', '?')}（{q.get('category', '')}）\n\n"
                f"**问题：**{q.get('question', '')}\n\n"
                f"**考察点：**{q.get('intent', '')}\n\n"
                f"**参考答案：**{q.get('reference_answer', '')}\n\n"
                f"**评分标准：**\n"
                + "\n".join(f"- {c}" for c in q.get("evaluation_criteria", []))
            )
        sections = {"面试题": "\n\n".join(questions_md)}
        report = generate_report("面试题集", sections)
        save_report(report, output)
        console.print(f"\n[green]报告已保存至 {output}[/green]")


@cli.command()
@click.option("--job", "-j", required=True, help="岗位JD文件路径")
@click.option("--count", "-n", default=3, help="模拟面试题目数量")
def mock(job, count):
    """交互式模拟面试：出题→你答→AI点评"""
    job_text = read_file(job)

    console.print(Panel(
        "[bold]模拟面试模式[/bold]\n\n"
        "AI将根据岗位要求出题，你输入回答后AI会给出点评。\n"
        "输入 [red]quit[/red] 可随时退出。",
        title="JobFit AI",
    ))

    # 先生成面试题
    console.print("[bold cyan]正在准备面试题，调用AI生成中...[/bold cyan]")
    result = generate_interview_questions(job_text, count)

    questions = result.get("questions", [])
    if not questions:
        console.print("[red]未能生成面试题，请检查API配置[/red]")
        return

    total_score = 0
    answered = 0

    for q in questions:
        console.print(Panel(
            f"[bold]{q.get('question', '')}[/bold]\n\n"
            f"[cyan]类型：[/cyan]{q.get('category', '')}  "
            f"[cyan]考察点：[/cyan]{q.get('intent', '')}",
            title=f"面试题 #{q.get('id', '?')}",
        ))

        answer = console.input("[bold green]请输入你的回答：[/bold green]")

        if answer.strip().lower() == "quit":
            console.print("[yellow]已退出模拟面试[/yellow]")
            break

        if not answer.strip():
            console.print("[yellow]跳过此题[/yellow]")
            continue

        console.print("[bold cyan]正在评估你的回答...[/bold cyan]")
        eval_result = evaluate_answer(q.get("question", ""), answer, job_text)

        print_eval_result(eval_result)
        total_score += eval_result.get("score", 0)
        answered += 1
        console.print()

    if answered > 0:
        avg_score = total_score / answered
        console.print(Panel(
            f"共回答 {answered} 题\n平均得分：[bold]{avg_score:.1f}[/bold] / 10",
            title="模拟面试总结",
        ))


@cli.command()
@click.option("--resume", "-r", required=True, help="简历文件路径")
@click.option("--output", "-o", default=None, help="导出报告路径（Markdown格式）")
def search(resume, output):
    """根据简历意向自动搜索求职平台岗位"""
    resume_text = read_file(resume)

    # 1. 解析简历
    console.print("[bold cyan]正在解析简历...[/bold cyan]")
    parsed = parse_resume(resume_text)

    positions = parsed.get("target_positions", [])
    cities = parsed.get("target_cities", [])

    if not positions:
        console.print("[yellow]简历中未找到意向岗位，请确保简历包含「求职意向」部分[/yellow]")
        return

    console.print(Panel(
        f"姓名：{parsed.get('name', '未知')}\n"
        f"意向岗位：{'、'.join(positions)}\n"
        f"期望城市：{'、'.join(cities) if cities else '未指定'}\n"
        f"期望薪资：{parsed.get('expected_salary', '未指定')}\n"
        f"技能：{'、'.join(parsed.get('skills', [])[:10])}",
        title="简历解析结果",
    ))

    # 2. 搜索岗位
    console.print("[bold cyan]正在搜索求职平台...[/bold cyan]")
    search_results = search_multi_keywords(positions, cities if cities else ["北京"])

    # 3. 展示搜索结果
    jobs = search_results.get("jobs", [])
    urls = search_results.get("search_urls", [])

    if jobs:
        table = Table(title=f"搜索到 {len(jobs)} 个岗位")
        table.add_column("序号", style="cyan", width=4)
        table.add_column("岗位名称", style="green")
        table.add_column("公司", style="white")
        table.add_column("薪资", style="yellow")
        table.add_column("地点")
        table.add_column("来源", style="cyan")
        for i, job in enumerate(jobs, 1):
            table.add_row(
                str(i),
                job.get("title", ""),
                job.get("company", ""),
                job.get("salary", ""),
                job.get("location", ""),
                job.get("platform", ""),
            )
        console.print(table)
    else:
        console.print("[yellow]未能从平台抓取到岗位数据（可能需要登录），请通过以下链接手动搜索：[/yellow]")

    # 4. 展示搜索链接
    if urls:
        console.print("\n[bold cyan]求职平台搜索链接：[/bold cyan]")
        for u in urls:
            console.print(f"  [{u['platform']}] {u['url']}")

    # 5. AI推荐
    console.print("\n[bold cyan]正在基于简历技能栈和项目经验进行AI岗位推荐...[/bold cyan]")
    rec_result = recommend_jobs(parsed, search_results)

    recommendations = rec_result.get("recommendations", [])
    if recommendations:
        for rec in recommendations:
            score = rec.get("fit_score", 0)
            score_color = "green" if score >= 70 else "yellow" if score >= 50 else "red"
            console.print(Panel(
                f"[bold]{rec.get('job_title', '')}[/bold]\n\n"
                f"[cyan]公司类型：[/cyan]{rec.get('company_type', '')}\n"
                f"[cyan]薪资范围：[/cyan]{rec.get('salary_range', '')}\n"
                f"[cyan]推荐城市：[/cyan]{rec.get('city', '')}\n"
                f"[cyan]适配度：[/cyan][{score_color}]{score}[/{score_color}]/100\n"
                f"[cyan]匹配技能：[/cyan]{', '.join(rec.get('matched_skills', []))}\n"
                f"[cyan]缺失技能：[/cyan]{', '.join(rec.get('missing_skills', []))}\n"
                f"[cyan]相关项目：[/cyan]{', '.join(rec.get('matched_projects', []))}\n\n"
                f"[white]推荐理由：[/white]{rec.get('why_recommended', '')}\n\n"
                f"[white]典型JD：[/white]{'; '.join(rec.get('jd_summary', [])[:3])}\n\n"
                f"[yellow]简历优化建议：[/yellow]",
                title=f"推荐 #{rec.get('rank', '?')}",
            ))
            for s in rec.get("optimization_suggestions", []):
                console.print(f"  - {s}")
            console.print()

    # 整体建议
    overall = rec_result.get("overall_suggestions", [])
    if overall:
        console.print("[bold cyan]整体求职策略建议：[/bold cyan]")
        for i, s in enumerate(overall, 1):
            console.print(f"  {i}. {s}")

    if output:
        sections = {
            "简历解析": f"姓名：{parsed.get('name', '')}\n意向岗位：{'、'.join(positions)}\n期望城市：{'、'.join(cities)}",
            "搜索链接": "\n".join(f"- [{u['platform']}]({u['url']})" for u in urls),
            "AI推荐岗位": "\n\n".join(
                f"### {rec.get('job_title', '')}（适配度{rec.get('fit_score', 0)}分）\n\n"
                f"- 公司类型：{rec.get('company_type', '')}\n"
                f"- 薪资：{rec.get('salary_range', '')}\n"
                f"- 推荐理由：{rec.get('why_recommended', '')}\n"
                f"- 匹配技能：{', '.join(rec.get('matched_skills', []))}\n"
                f"- 缺失技能：{', '.join(rec.get('missing_skills', []))}\n"
                f"- 优化建议：\n" + "\n".join(f"  - {s}" for s in rec.get("optimization_suggestions", []))
                for rec in recommendations
            ),
            "整体建议": "\n".join(f"{i}. {s}" for i, s in enumerate(overall, 1)),
        }
        report = generate_report("岗位搜索与推荐报告", sections)
        save_report(report, output)
        console.print(f"\n[green]报告已保存至 {output}[/green]")


@cli.command()
@click.option("--resume", "-r", required=True, help="简历文件路径")
@click.option("--job-index", "-i", default=0, help="选择推荐岗位的序号（从1开始，0表示交互选择）")
@click.option("--output", "-o", default=None, help="导出报告路径（Markdown格式）")
def recommend(resume, job_index, output):
    """一键推荐：解析简历→搜索岗位→推荐分析→模拟面试"""
    resume_text = read_file(resume)

    # 1. 解析简历
    console.print("[bold cyan]Step 1/4: 正在解析简历...[/bold cyan]")
    parsed = parse_resume(resume_text)

    positions = parsed.get("target_positions", [])
    cities = parsed.get("target_cities", [])

    console.print(Panel(
        f"姓名：{parsed.get('name', '未知')}\n"
        f"意向岗位：{'、'.join(positions)}\n"
        f"期望城市：{'、'.join(cities) if cities else '未指定'}\n"
        f"期望薪资：{parsed.get('expected_salary', '未指定')}\n"
        f"核心技能：{'、'.join(parsed.get('skills', [])[:8])}",
        title="简历解析结果",
    ))

    # 2. 搜索岗位
    console.print("[bold cyan]Step 2/4: 正在搜索求职平台...[/bold cyan]")
    search_results = search_multi_keywords(positions, cities if cities else ["北京"])

    # 3. AI推荐
    console.print("[bold cyan]Step 3/4: 正在AI推荐岗位并分析适配度...[/bold cyan]")
    rec_result = recommend_jobs(parsed, search_results)

    recommendations = rec_result.get("recommendations", [])
    if not recommendations:
        console.print("[red]未能生成推荐岗位[/red]")
        return

    # 展示推荐列表
    console.print("\n[bold green]推荐岗位列表：[/bold green]")
    for rec in recommendations:
        score = rec.get("fit_score", 0)
        score_color = "green" if score >= 70 else "yellow" if score >= 50 else "red"
        console.print(
            f"  [{rec.get('rank', '?')}] "
            f"[bold]{rec.get('job_title', '')}[/bold] | "
            f"{rec.get('company_type', '')} | "
            f"{rec.get('salary_range', '')} | "
            f"[{score_color}]{score}分[/{score_color}] | "
            f"{rec.get('city', '')}"
        )

    # 4. 选择岗位进行模拟面试
    if job_index == 0:
        choice = console.input("\n[bold green]请选择岗位序号进行模拟面试（输入数字，0跳过）：[/bold green]")
        try:
            job_index = int(choice)
        except ValueError:
            job_index = 0

    if 0 < job_index <= len(recommendations):
        selected = recommendations[job_index - 1]
        jd_text = "; ".join(selected.get("jd_summary", []))
        job_title = selected.get("job_title", "")

        console.print(f"\n[bold cyan]Step 4/4: 针对「{job_title}」进行模拟面试...[/bold cyan]")
        console.print(Panel(
            f"[bold]已选择：{job_title}[/bold]\n"
            f"适配度：{selected.get('fit_score', 0)}/100\n"
            f"匹配技能：{', '.join(selected.get('matched_skills', []))}\n"
            f"缺失技能：{', '.join(selected.get('missing_skills', []))}",
            title="模拟面试岗位",
        ))

        # 生成面试题
        console.print("[bold cyan]正在生成面试题...[/bold cyan]")
        interview_result = generate_interview_questions(jd_text, 3)
        questions = interview_result.get("questions", [])

        if not questions:
            console.print("[red]未能生成面试题[/red]")
            return

        total_score = 0
        answered = 0

        for q in questions:
            console.print(Panel(
                f"[bold]{q.get('question', '')}[/bold]\n\n"
                f"[cyan]类型：[/cyan]{q.get('category', '')}  "
                f"[cyan]考察点：[/cyan]{q.get('intent', '')}",
                title=f"面试题 #{q.get('id', '?')}",
            ))

            answer = console.input("[bold green]请输入你的回答：[/bold green]")

            if answer.strip().lower() == "quit":
                break

            if not answer.strip():
                continue

            console.print("[bold cyan]正在评估你的回答...[/bold cyan]")
            eval_result = evaluate_answer(q.get("question", ""), answer, jd_text)
            print_eval_result(eval_result)
            total_score += eval_result.get("score", 0)
            answered += 1

        if answered > 0:
            avg_score = total_score / answered
            console.print(Panel(
                f"岗位：{job_title}\n"
                f"共回答 {answered} 题\n"
                f"平均得分：[bold]{avg_score:.1f}[/bold] / 10",
                title="模拟面试总结",
            ))

        # 简历优化建议
        opt_suggestions = selected.get("optimization_suggestions", [])
        if opt_suggestions:
            console.print(f"\n[bold cyan]针对「{job_title}」的简历优化建议：[/bold cyan]")
            for i, s in enumerate(opt_suggestions, 1):
                console.print(f"  {i}. {s}")

    if output:
        sections = {
            "简历解析": f"姓名：{parsed.get('name', '')}\n意向岗位：{'、'.join(positions)}\n技能：{'、'.join(parsed.get('skills', [])[:10])}",
            "推荐岗位": "\n\n".join(
                f"### {rec.get('job_title', '')}（适配度{rec.get('fit_score', 0)}分）\n\n"
                f"- 推荐理由：{rec.get('why_recommended', '')}\n"
                f"- 匹配技能：{', '.join(rec.get('matched_skills', []))}\n"
                f"- 缺失技能：{', '.join(rec.get('missing_skills', []))}\n"
                f"- 优化建议：\n" + "\n".join(f"  - {s}" for s in rec.get("optimization_suggestions", []))
                for rec in recommendations
            ),
            "整体建议": "\n".join(f"{i}. {s}" for i, s in enumerate(rec_result.get("overall_suggestions", []), 1)),
        }
        report = generate_report("岗位推荐与面试分析报告", sections)
        save_report(report, output)
        console.print(f"\n[green]报告已保存至 {output}[/green]")


if __name__ == "__main__":
    cli()
