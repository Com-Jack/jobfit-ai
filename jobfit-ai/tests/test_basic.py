"""基础测试"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEFAULT_INTERVIEW_COUNT, MAX_INPUT_LENGTH


def test_config_defaults():
    """测试配置默认值"""
    assert DEFAULT_INTERVIEW_COUNT == 5
    assert MAX_INPUT_LENGTH == 10000


def test_read_sample_files():
    """测试示例数据文件存在且可读"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    resume_path = os.path.join(data_dir, "sample_resume.txt")
    jd_path = os.path.join(data_dir, "sample_jd.txt")

    assert os.path.exists(resume_path), "示例简历文件不存在"
    assert os.path.exists(jd_path), "示例JD文件不存在"

    with open(resume_path, "r", encoding="utf-8") as f:
        resume = f.read()
    assert len(resume) > 0, "示例简历为空"
    assert "张三" in resume, "示例简历内容异常"

    with open(jd_path, "r", encoding="utf-8") as f:
        jd = f.read()
    assert len(jd) > 0, "示例JD为空"
    assert "AI" in jd, "示例JD内容异常"


def test_report_generation():
    """测试报告生成"""
    from utils.report import generate_report

    report = generate_report("测试报告", {"章节1": "内容1", "章节2": "内容2"})
    assert "# 测试报告" in report
    assert "## 章节1" in report
    assert "内容1" in report


if __name__ == "__main__":
    test_config_defaults()
    test_read_sample_files()
    test_report_generation()
    print("所有测试通过！")
