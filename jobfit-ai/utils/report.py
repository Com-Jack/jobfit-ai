"""报告生成与导出"""

from datetime import datetime


def generate_report(title: str, sections: dict) -> str:
    """生成Markdown格式报告

    Args:
        title: 报告标题
        sections: {章节名: 章节内容} 字典
    """
    lines = [f"# {title}", ""]
    lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    for section_name, content in sections.items():
        lines.append(f"## {section_name}")
        lines.append("")
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


def save_report(report: str, filepath: str) -> None:
    """保存报告到文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
