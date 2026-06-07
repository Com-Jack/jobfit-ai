"""生成项目报告Word文档"""

from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime
import os

doc = Document()

# ==================== 全局样式设置 ====================
style = doc.styles['Normal']
font = style.font
font.name = '宋体'
font.size = Pt(12)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# 页面边距
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)


def set_cell_shading(cell, color):
    """设置单元格底色"""
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    shading.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shading)


def add_heading_styled(text, level=1):
    """添加带样式的标题"""
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = '黑体'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        if level == 1:
            run.font.size = Pt(18)
            run.font.color.rgb = RGBColor(0, 51, 102)
        elif level == 2:
            run.font.size = Pt(15)
            run.font.color.rgb = RGBColor(0, 70, 130)
        elif level == 3:
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(0, 90, 156)
    return h


def add_para(text, bold=False, indent=False, font_size=12, alignment=None):
    """添加段落"""
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    if alignment:
        p.alignment = alignment
    run = p.add_run(text)
    run.font.name = '宋体'
    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(font_size)
    run.bold = bold
    return p


def add_table(headers, rows, col_widths=None):
    """添加表格"""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # 表头
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.name = '宋体'
                run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                run.font.size = Pt(10)
        set_cell_shading(cell, 'D9E2F3')

    # 数据行
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(val)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.name = '宋体'
                    run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                    run.font.size = Pt(10)

    if col_widths:
        for i, width in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(width)

    return table


# ==================== 封面页 ====================
for _ in range(6):
    doc.add_paragraph()

add_para('JobFit AI', bold=True, font_size=28, alignment=WD_ALIGN_PARAGRAPH.CENTER)
add_para('简历岗位智能匹配与面试分析器', bold=True, font_size=20, alignment=WD_ALIGN_PARAGRAPH.CENTER)
doc.add_paragraph()
add_para('项 目 报 告', bold=True, font_size=22, alignment=WD_ALIGN_PARAGRAPH.CENTER)

for _ in range(3):
    doc.add_paragraph()

info_items = [
    ('项目名称', 'JobFit AI - 简历岗位智能匹配与面试分析器'),
    ('项目版本', 'V1.0.0'),
    ('报告日期', datetime.date.today().strftime('%Y年%m月%d日')),
    ('项目类型', 'AI应用开发项目'),
    ('技术方向', '大语言模型应用 / 智能求职助手'),
]
for label, value in info_items:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run1 = p.add_run(f'{label}：')
    run1.bold = True
    run1.font.name = '宋体'
    run1.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run1.font.size = Pt(14)
    run2 = p.add_run(value)
    run2.font.name = '宋体'
    run2.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run2.font.size = Pt(14)

doc.add_page_break()

# ==================== 目录页 ====================
add_heading_styled('目  录', level=1)
toc_items = [
    '一、项目概述',
    '    1.1 项目背景',
    '    1.2 项目目标',
    '    1.3 项目范围',
    '二、需求分析',
    '    2.1 用户痛点分析',
    '    2.2 功能需求',
    '    2.3 非功能需求',
    '三、系统设计',
    '    3.1 系统架构设计',
    '    3.2 模块设计',
    '    3.3 数据流设计',
    '    3.4 接口设计',
    '四、技术方案',
    '    4.1 技术选型',
    '    4.2 大模型API集成方案',
    '    4.3 Prompt工程方案',
    '    4.4 文件解析方案',
    '五、功能实现',
    '    5.1 智能推荐功能',
    '    5.2 岗位搜索功能',
    '    5.3 匹配分析功能',
    '    5.4 简历优化功能',
    '    5.5 面试题生成功能',
    '    5.6 模拟面试功能',
    '六、测试验证',
    '    6.1 测试环境',
    '    6.2 功能测试',
    '    6.3 接口测试',
    '七、项目总结',
    '    7.1 项目成果',
    '    7.2 技术亮点',
    '    7.3 不足与展望',
]
for item in toc_items:
    add_para(item, font_size=12)

doc.add_page_break()

# ==================== 一、项目概述 ====================
add_heading_styled('一、项目概述', level=1)

add_heading_styled('1.1 项目背景', level=2)
add_para('随着人工智能技术的快速发展，大语言模型（LLM）在自然语言处理领域展现出强大的能力，为传统行业的智能化升级提供了新的技术路径。在人力资源和求职招聘领域，求职者面临着信息过载、岗位匹配效率低、面试准备不足等痛点。传统的求职方式依赖人工筛选岗位、手动比对岗位要求与自身条件，效率低下且容易遗漏关键信息。', indent=True)
add_para('与此同时，Boss直聘、猎聘、智联招聘等主流求职平台虽然提供了丰富的岗位信息，但缺乏智能化的简历-岗位匹配分析工具，求职者难以快速定位最适合自己的岗位，也难以针对性地优化简历和准备面试。', indent=True)
add_para('基于上述背景，本项目提出JobFit AI——简历岗位智能匹配与面试分析器，利用大语言模型的自然语言理解和生成能力，实现从简历解析、岗位搜索、匹配分析、简历优化到模拟面试的全流程智能化求职辅助。', indent=True)

add_heading_styled('1.2 项目目标', level=2)
add_para('本项目的核心目标是构建一个基于大语言模型API的一站式求职助手系统，具体目标如下：', indent=True)
goals = [
    ('智能解析', '利用LLM从非结构化简历文本中提取结构化信息，包括意向岗位、期望城市、期望薪资、技能栈、项目经历等关键要素'),
    ('精准推荐', '结合简历技能栈和项目经验，自动搜索求职平台岗位，AI推荐最匹配的岗位并分析适配度'),
    ('深度分析', '对简历与目标岗位进行多维度匹配分析，量化评估适配度，识别优势与不足'),
    ('优化指导', '针对目标岗位给出具体的简历优化建议，包括关键词、经历描述、结构调整等'),
    ('面试辅助', '根据岗位要求生成针对性面试题，支持交互式模拟面试与AI点评'),
]
for title, desc in goals:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    run1 = p.add_run(f'（{goals.index((title, desc)) + 1}）{title}：')
    run1.bold = True
    run1.font.name = '宋体'
    run1.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run1.font.size = Pt(12)
    run2 = p.add_run(desc)
    run2.font.name = '宋体'
    run2.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run2.font.size = Pt(12)

add_heading_styled('1.3 项目范围', level=2)
add_table(
    ['维度', '说明'],
    [
        ['目标用户', '求职者（应届生、社招人员、转行人员）'],
        ['支持平台', 'Boss直聘、猎聘、智联招聘'],
        ['支持格式', 'TXT、MD、PDF、DOCX'],
        ['运行模式', 'CLI命令行模式 + Streamlit Web界面模式'],
        ['模型支持', 'DeepSeek、阿里云通义千问、OpenAI等兼容接口'],
        ['语言支持', '中文为主，兼容英文简历'],
    ],
    col_widths=[4, 12]
)

doc.add_page_break()

# ==================== 二、需求分析 ====================
add_heading_styled('二、需求分析', level=1)

add_heading_styled('2.1 用户痛点分析', level=2)
add_table(
    ['序号', '痛点', '描述', '影响程度'],
    [
        ['1', '岗位信息分散', '需要在多个求职平台分别搜索，信息整合困难', '高'],
        ['2', '匹配判断主观', '无法客观评估简历与岗位的适配度，容易错失机会', '高'],
        ['3', '简历优化盲目', '不清楚目标岗位看重哪些关键词和技能，优化缺乏方向', '高'],
        ['4', '面试准备不足', '缺乏针对性的面试题练习，无法提前发现知识盲区', '中'],
        ['5', '反馈周期长', '投递简历后等待回复时间长，无法快速迭代优化', '中'],
    ],
    col_widths=[1.5, 3, 7, 2.5]
)

add_heading_styled('2.2 功能需求', level=2)
add_table(
    ['功能模块', '功能编号', '功能名称', '功能描述', '优先级'],
    [
        ['智能推荐', 'FR-01', '简历智能解析', 'AI自动提取意向岗位、城市、薪资、技能分类、项目经历', 'P0'],
        ['智能推荐', 'FR-02', '求职平台搜索', '自动搜索Boss直聘/猎聘/智联招聘，生成搜索链接', 'P0'],
        ['智能推荐', 'FR-03', '岗位智能推荐', '基于技能栈+项目经验推荐5个匹配岗位，含适配度评分', 'P0'],
        ['匹配分析', 'FR-04', '适配度评分', '量化评估简历与岗位JD的匹配程度（1-100分）', 'P0'],
        ['匹配分析', 'FR-05', '技能匹配分析', '识别匹配技能和缺失技能，分析优势与不足', 'P0'],
        ['简历优化', 'FR-06', '关键词建议', '针对目标岗位建议应添加的关键词及放置位置', 'P1'],
        ['简历优化', 'FR-07', '经历描述优化', '优化项目经历和工作经历的描述方式', 'P1'],
        ['面试题生成', 'FR-08', '针对性出题', '根据JD生成技术/行为/项目/场景类面试题', 'P1'],
        ['模拟面试', 'FR-09', '交互式面试', 'AI出题→用户回答→AI点评，含评分和改进建议', 'P0'],
        ['数据互通', 'FR-10', '全局数据共享', '6个功能页面数据互通，一键跳转无需重新上传', 'P1'],
        ['文件解析', 'FR-11', '多格式支持', '支持TXT/MD/PDF/DOCX文件上传和解析', 'P1'],
    ],
    col_widths=[2.2, 1.5, 2.5, 6, 1.3]
)

add_heading_styled('2.3 非功能需求', level=2)
add_table(
    ['需求编号', '需求名称', '描述', '指标'],
    [
        ['NFR-01', '响应时间', '单次API调用响应时间', '≤30秒'],
        ['NFR-02', '可用性', '系统在API可用时的可用率', '≥99%'],
        ['NFR-03', '兼容性', '支持主流操作系统', 'Windows/macOS/Linux'],
        ['NFR-04', '安全性', 'API Key不暴露到代码仓库', '.gitignore排除.env'],
        ['NFR-05', '可扩展性', '支持切换不同大模型API', '配置化切换，无需改代码'],
        ['NFR-06', '易用性', 'Web界面操作直观', '文件拖拽上传，一键分析'],
    ],
    col_widths=[2, 2.5, 5, 4]
)

doc.add_page_break()

# ==================== 三、系统设计 ====================
add_heading_styled('三、系统设计', level=1)

add_heading_styled('3.1 系统架构设计', level=2)
add_para('本系统采用分层架构设计，分为表现层、业务逻辑层、数据访问层三个层次，各层之间通过明确的接口进行通信，实现了高内聚低耦合的设计目标。', indent=True)

add_para('系统架构图如下：', indent=True)
# 用表格模拟架构图
arch_table = doc.add_table(rows=5, cols=1)
arch_table.style = 'Table Grid'
arch_table.alignment = WD_TABLE_ALIGNMENT.CENTER

layers = [
    ('表现层（Presentation Layer）', 'CLI命令行界面（click + rich） | Streamlit Web界面'),
    ('业务逻辑层（Business Logic Layer）', '简历解析 | 岗位搜索 | 岗位推荐 | 匹配分析 | 简历优化 | 面试评估'),
    ('数据访问层（Data Access Layer）', 'LLM API封装（OpenAI兼容接口） | 求职平台爬虫 | 文件解析器'),
    ('基础设施层（Infrastructure Layer）', '配置管理（config.py + .env） | 报告生成 | 日志记录'),
    ('外部服务（External Services）', '大模型API（DeepSeek/通义千问/OpenAI） | Boss直聘/猎聘/智联招聘'),
]
for i, (title, content) in enumerate(layers):
    cell = arch_table.rows[i].cells[0]
    p1 = cell.paragraphs[0]
    run1 = p1.add_run(title)
    run1.bold = True
    run1.font.name = '宋体'
    run1.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run1.font.size = Pt(10)
    p2 = cell.add_paragraph()
    run2 = p2.add_run(content)
    run2.font.name = '宋体'
    run2.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run2.font.size = Pt(9)
    colors = ['E2EFDA', 'D6E4F0', 'FCE4D6', 'E4DFEC', 'FFF2CC']
    set_cell_shading(cell, colors[i])

add_heading_styled('3.2 模块设计', level=2)
add_table(
    ['模块名称', '文件路径', '职责描述', '核心方法'],
    [
        ['简历解析', 'analyzer/resume_parser.py', '从简历文本提取结构化信息', 'parse_resume()'],
        ['岗位搜索', 'analyzer/job_searcher.py', '搜索求职平台岗位', 'search_multi_keywords()'],
        ['岗位推荐', 'analyzer/job_recommender.py', 'AI推荐匹配岗位', 'recommend_jobs()'],
        ['匹配分析', 'analyzer/matcher.py', '简历-岗位适配度分析', 'analyze_match()'],
        ['简历优化', 'analyzer/optimizer.py', '简历优化建议生成', 'optimize_resume()'],
        ['面试评估', 'analyzer/interviewer.py', '面试题生成与回答评估', 'generate_interview_questions()\nevaluate_answer()'],
        ['Prompt模板', 'analyzer/prompts.py', '所有LLM Prompt模板', '-'],
        ['LLM封装', 'utils/llm.py', '大模型API调用封装', 'chat()\nchat_stream()'],
        ['报告生成', 'utils/report.py', 'Markdown报告生成与导出', 'generate_report()\nsave_report()'],
        ['配置管理', 'config.py', 'API配置与常量', '-'],
        ['CLI入口', 'main.py', '命令行交互入口', 'match/optimize/interview/\nmock/search/recommend'],
        ['Web界面', 'app.py', 'Streamlit可视化界面', '6个功能页面'],
    ],
    col_widths=[2, 3.5, 4, 3.5]
)

add_heading_styled('3.3 数据流设计', level=2)
add_para('系统核心数据流如下：', indent=True)
add_para('（1）智能推荐流程：简历文本 → 简历解析（LLM） → 结构化信息 → 岗位搜索（爬虫） → 搜索结果 → 岗位推荐（LLM） → 推荐列表 + 适配度评分 + 优化建议', indent=True)
add_para('（2）匹配分析流程：简历文本 + 岗位JD → 匹配分析（LLM） → 适配度评分 + 匹配技能 + 缺失技能 + 改进建议', indent=True)
add_para('（3）简历优化流程：简历文本 + 岗位JD → 优化分析（LLM） → 关键词建议 + 经历优化 + 行动清单', indent=True)
add_para('（4）模拟面试流程：岗位JD → 面试题生成（LLM） → 面试题列表 → 用户作答 → 回答评估（LLM） → 评分 + 点评 + 改进建议', indent=True)
add_para('（5）全局数据流：用户上传简历/JD → 共享Session State → 各功能页面直接读取 → 一键跳转无需重新上传', indent=True)

add_heading_styled('3.4 接口设计', level=2)
add_para('系统对外提供CLI和Web两种交互接口，内部通过统一的LLM API封装层与大模型通信。', indent=True)

add_table(
    ['接口类型', '接口名称', '输入参数', '输出结果'],
    [
        ['CLI', 'match', '简历文件路径、JD文件路径', '匹配度评分、匹配/缺失技能、建议'],
        ['CLI', 'optimize', '简历文件路径、JD文件路径', '关键词建议、经历优化、行动清单'],
        ['CLI', 'interview', 'JD文件路径、题目数量', '面试题列表+参考答案+评分标准'],
        ['CLI', 'mock', 'JD文件路径、题目数量', '交互式面试流程+评分总结'],
        ['CLI', 'search', '简历文件路径', '搜索链接+岗位列表'],
        ['CLI', 'recommend', '简历文件路径、岗位序号', '解析+搜索+推荐+面试全流程'],
        ['Web', '智能推荐页', '简历文本/文件', '解析结果+推荐岗位+适配度'],
        ['Web', '匹配分析页', '简历+JD', '匹配评分+详细分析'],
        ['Web', '模拟面试页', 'JD', '交互式面试+评分'],
    ],
    col_widths=[1.5, 2.5, 4.5, 5]
)

doc.add_page_break()

# ==================== 四、技术方案 ====================
add_heading_styled('四、技术方案', level=1)

add_heading_styled('4.1 技术选型', level=2)
add_table(
    ['技术领域', '技术选型', '选型理由'],
    [
        ['编程语言', 'Python 3.10+', '生态丰富，AI/ML领域主流语言，开发效率高'],
        ['LLM接口', 'OpenAI兼容API', '统一接口标准，支持DeepSeek/通义千问/OpenAI等多家模型'],
        ['CLI框架', 'Click + Rich', 'Click提供命令组管理，Rich提供终端美化输出'],
        ['Web框架', 'Streamlit', '快速构建数据应用，无需前端开发，适合AI应用原型'],
        ['HTTP请求', 'Requests', 'Python最流行的HTTP库，简洁易用'],
        ['HTML解析', 'BeautifulSoup4', '轻量级HTML解析库，适合爬取求职平台页面'],
        ['PDF解析', 'PyPDF2', '纯Python实现，无系统依赖，跨平台兼容'],
        ['Word解析', 'python-docx', '官方推荐的Word文档处理库'],
        ['环境管理', 'python-dotenv', '标准化的环境变量管理，保护API Key安全'],
    ],
    col_widths=[2.5, 3.5, 8]
)

add_heading_styled('4.2 大模型API集成方案', level=2)
add_para('本系统采用OpenAI兼容接口标准，通过统一的封装层（utils/llm.py）实现对多家大模型API的透明调用。核心设计如下：', indent=True)

add_para('（1）配置化切换：通过.env文件配置LLM_API_KEY、LLM_BASE_URL、LLM_MODEL三个参数，无需修改代码即可切换模型提供商。', indent=True)
add_para('（2）统一封装：chat()函数封装了完整的API调用流程，包括客户端初始化、消息构造、异常处理。', indent=True)
add_para('（3）流式支持：chat_stream()函数提供流式输出能力，为后续的实时生成场景预留接口。', indent=True)
add_para('（4）JSON解析容错：所有LLM返回结果均经过JSON解析容错处理，自动提取JSON片段，确保结构化输出。', indent=True)

add_heading_styled('4.3 Prompt工程方案', level=2)
add_para('本系统采用System Prompt + User Prompt的双层Prompt架构，针对不同功能场景设计了6套专业Prompt模板，存储在analyzer/prompts.py中。', indent=True)

add_table(
    ['Prompt名称', '应用场景', '温度参数', '输出格式', '设计要点'],
    [
        ['MATCH', '匹配分析', '0.3', 'JSON', '角色设定为资深猎头，输出评分+匹配/缺失技能+建议'],
        ['OPTIMIZE', '简历优化', '0.5', 'JSON', '角色设定为简历优化顾问，输出关键词+经历优化+行动清单'],
        ['INTERVIEW', '面试题生成', '0.7', 'JSON', '角色设定为资深面试官，输出多类型题目+参考答案+评分标准'],
        ['MOCK_EVAL', '面试评估', '0.3', 'JSON', '评估回答质量，输出评分+亮点+不足+改进建议'],
        ['RESUME_PARSE', '简历解析', '0.2', 'JSON', '提取结构化信息，输出意向/技能/项目/学历等字段'],
        ['JOB_RECOMMEND', '岗位推荐', '0.5', 'JSON', '角色设定为资深猎头，输出推荐岗位+适配度+优化建议'],
    ],
    col_widths=[2.2, 2, 1.5, 1.5, 6.5]
)

add_heading_styled('4.4 文件解析方案', level=2)
add_para('系统支持TXT、MD、PDF、DOCX四种文件格式的简历和JD文件解析，具体方案如下：', indent=True)

add_table(
    ['文件格式', '解析库', '解析策略', '异常处理'],
    [
        ['TXT/MD', '内置decode', '优先UTF-8解码，失败回退GBK', '编码识别失败时提示用户'],
        ['PDF', 'PyPDF2', '逐页提取文本，合并输出', '扫描件PDF提示用户手动粘贴'],
        ['DOCX', 'python-docx', '遍历段落提取文本，过滤空行', '空文档提示用户检查文件内容'],
    ],
    col_widths=[2, 2.5, 5, 4]
)

add_para('在Streamlit Web界面中，文件上传采用on_change回调机制，上传文件后自动将解析内容填入对应的text_area组件，避免Streamlit的session_state修改冲突。', indent=True)

doc.add_page_break()

# ==================== 五、功能实现 ====================
add_heading_styled('五、功能实现', level=1)

add_heading_styled('5.1 智能推荐功能', level=2)
add_para('智能推荐是本系统的核心功能，实现了从简历输入到岗位推荐的完整闭环。执行流程如下：', indent=True)
add_para('Step 1 - 简历解析：调用LLM对简历文本进行结构化信息提取，输出姓名、意向岗位、期望城市、期望薪资、技能分类、项目经历等字段。', indent=True)
add_para('Step 2 - 岗位搜索：根据解析出的意向岗位和城市，构造Boss直聘/猎聘/智联招聘的搜索URL，并尝试抓取Boss直聘的岗位列表数据。', indent=True)
add_para('Step 3 - AI推荐：将简历结构化信息和搜索结果作为上下文，调用LLM推荐5个最匹配的岗位，每个岗位包含适配度评分、匹配/缺失技能、推荐理由、典型JD摘要和简历优化建议。', indent=True)
add_para('Step 4 - 功能跳转：推荐结果中每个岗位提供"匹配分析"、"简历优化"、"模拟面试"三个跳转按钮，点击后自动将简历和JD数据传递到目标页面，无需重新上传。', indent=True)

add_heading_styled('5.2 岗位搜索功能', level=2)
add_para('岗位搜索模块实现了对三大主流求职平台的搜索能力：', indent=True)
add_para('（1）URL构造：根据关键词和城市编码，生成Boss直聘、猎聘、智联招聘的搜索URL。', indent=True)
add_para('（2）数据抓取：尝试通过HTTP请求+BeautifulSoup解析Boss直聘的岗位列表页面，提取岗位名称、薪资、公司、标签等信息。', indent=True)
add_para('（3）降级策略：当抓取失败时（平台反爬机制），自动降级为提供搜索链接，用户可手动访问。', indent=True)
add_para('（4）多关键词搜索：支持多意向岗位×多城市的组合搜索，结果自动去重。', indent=True)

add_heading_styled('5.3 匹配分析功能', level=2)
add_para('匹配分析模块对简历与目标岗位JD进行多维度深度分析：', indent=True)
add_para('（1）量化评分：输出1-100分的适配度评分，评分标准综合考虑技能匹配度、经验匹配度、学历匹配度等因素。', indent=True)
add_para('（2）技能分析：分别列出匹配的技能和缺失的技能，帮助求职者快速定位差距。', indent=True)
add_para('（3）优劣势分析：从整体角度分析求职者的优势和不足，提供改进建议。', indent=True)
add_para('（4）报告导出：支持将分析结果导出为Markdown格式报告，便于保存和分享。', indent=True)

add_heading_styled('5.4 简历优化功能', level=2)
add_para('简历优化模块从三个维度提供针对性的优化建议：', indent=True)
add_para('（1）关键词优化：分析目标岗位JD中的高频关键词，建议在简历中添加的关键词及放置位置（如技能栏、项目描述、自我评价等）。', indent=True)
add_para('（2）经历描述优化：对简历中的项目经历和工作经历描述进行逐条优化，提供原文→建议→原因的完整对比。', indent=True)
add_para('（3）行动清单：生成可执行的行动项列表，帮助求职者按优先级逐步优化简历。', indent=True)

add_heading_styled('5.5 面试题生成功能', level=2)
add_para('面试题生成模块根据岗位JD自动生成多类型面试题：', indent=True)
add_para('（1）题目类型：涵盖技术题、行为题、项目题、场景题四大类型，全面考察候选人能力。', indent=True)
add_para('（2）参考答案：每道题配备详细的参考答案要点，帮助求职者了解优秀回答的标准。', indent=True)
add_para('（3）评分标准：提供3-5条评分标准，明确面试官的考察维度和评分依据。', indent=True)
add_para('（4）数量可控：支持1-10道题目的自定义生成，满足不同准备深度的需求。', indent=True)

add_heading_styled('5.6 模拟面试功能', level=2)
add_para('模拟面试模块实现了完整的交互式面试体验：', indent=True)
add_para('（1）出题阶段：根据岗位JD生成面试题，逐题展示给用户。', indent=True)
add_para('（2）作答阶段：用户在文本框中输入回答，提交后进入评估环节。', indent=True)
add_para('（3）评估阶段：LLM对用户回答进行多维度评估，输出1-10分评分、回答亮点、回答不足、改进后的参考回答和改进建议。', indent=True)
add_para('（4）总结阶段：所有题目回答完毕后，输出平均得分和各题得分汇总。', indent=True)
add_para('（5）数据互通：从智能推荐页面选择岗位后，JD数据自动传递到模拟面试页面，实现无缝跳转。', indent=True)

doc.add_page_break()

# ==================== 六、测试验证 ====================
add_heading_styled('六、测试验证', level=1)

add_heading_styled('6.1 测试环境', level=2)
add_table(
    ['项目', '配置'],
    [
        ['操作系统', 'Windows 11'],
        ['Python版本', '3.10+'],
        ['大模型', '阿里云通义千问 qwen-plus'],
        ['API接口', 'https://dashscope.aliyuncs.com/compatible-mode/v1'],
        ['测试框架', 'pytest'],
        ['Web框架', 'Streamlit 1.30+'],
    ],
    col_widths=[3, 11]
)

add_heading_styled('6.2 功能测试', level=2)
add_table(
    ['测试编号', '测试功能', '测试输入', '预期输出', '实际结果', '是否通过'],
    [
        ['TC-01', '简历解析', '示例简历文本', '提取姓名、意向岗位、城市、薪资、技能', '正确提取所有字段', '通过'],
        ['TC-02', '岗位搜索', '关键词"Python开发"+城市"北京"', '生成3个平台搜索URL', '生成3个URL', '通过'],
        ['TC-03', '匹配分析', '示例简历+示例JD', '评分1-100+匹配/缺失技能', '评分72分，分析准确', '通过'],
        ['TC-04', '简历优化', '示例简历+示例JD', '关键词建议+经历优化', '输出结构化优化建议', '通过'],
        ['TC-05', '面试题生成', '示例JD，3道题', '3道面试题+参考答案', '3道高质量面试题', '通过'],
        ['TC-06', '模拟面试', '示例JD，3道题', '交互式面试+评分', '完整面试流程', '通过'],
        ['TC-07', '文件上传(TXT)', 'sample_resume.txt', '自动填入文本框', '正确解析填入', '通过'],
        ['TC-08', '文件上传(DOCX)', '简历.docx', '自动填入文本框', '正确解析填入', '通过'],
        ['TC-09', '页面跳转', '推荐页点击"模拟面试"', 'JD自动传递到面试页', '数据正确传递', '通过'],
        ['TC-10', '报告导出', '匹配分析+导出参数', '生成Markdown报告', '报告格式正确', '通过'],
    ],
    col_widths=[1.3, 2, 2.5, 3, 2.5, 1.2]
)

add_heading_styled('6.3 接口测试', level=2)
add_para('对LLM API调用接口进行了以下验证：', indent=True)
add_para('（1）简历解析接口：输入示例简历，验证返回JSON结构完整性和字段准确性。', indent=True)
add_para('（2）匹配分析接口：输入简历+JD，验证评分合理性和分析内容专业性。', indent=True)
add_para('（3）面试题生成接口：输入JD，验证题目类型多样性和参考答案质量。', indent=True)
add_para('（4）面试评估接口：输入问题+回答+JD，验证评分一致性和改进建议实用性。', indent=True)
add_para('（5）岗位推荐接口：输入结构化简历+搜索结果，验证推荐岗位相关性和适配度评分准确性。', indent=True)

doc.add_page_break()

# ==================== 七、项目总结 ====================
add_heading_styled('七、项目总结', level=1)

add_heading_styled('7.1 项目成果', level=2)
add_para('本项目成功实现了JobFit AI——简历岗位智能匹配与面试分析器，完成了以下核心成果：', indent=True)

add_table(
    ['成果项', '说明'],
    [
        ['功能完整性', '实现6大核心功能：智能推荐、岗位搜索、匹配分析、简历优化、面试题生成、模拟面试'],
        ['双模式运行', '支持CLI命令行和Streamlit Web两种运行模式，满足不同使用场景'],
        ['多格式支持', '支持TXT/MD/PDF/DOCX四种文件格式上传和解析'],
        ['数据互通', '6个功能页面数据全局共享，支持一键跳转，无需重复上传'],
        ['多模型兼容', '支持DeepSeek/通义千问/OpenAI等兼容接口，一行配置切换'],
        ['求职平台集成', '集成Boss直聘/猎聘/智联招聘三大平台搜索能力'],
        ['代码质量', '21个源文件，2368行代码，模块化设计，结构清晰'],
        ['文档完善', 'README文档、.env配置模板、示例数据齐全，clone即可运行'],
    ],
    col_widths=[3, 11]
)

add_heading_styled('7.2 技术亮点', level=2)
add_para('（1）Prompt工程：针对6个不同场景设计了专业的Prompt模板，通过角色设定、输出格式约束、温度参数调优等手段，确保LLM输出的结构化和准确性。', indent=True)
add_para('（2）JSON解析容错：所有LLM返回结果均经过JSON解析容错处理，自动提取JSON片段，有效解决了LLM输出格式不稳定的问题。', indent=True)
add_para('（3）全局数据互通：通过Streamlit Session State实现6个功能页面的数据共享，用户在任一页面输入的数据自动同步到其他页面，大幅提升使用体验。', indent=True)
add_para('（4）文件上传回调机制：采用on_change回调方式处理文件上传，避免了Streamlit中widget key冲突的问题，实现了上传文件后自动填入文本框的功能。', indent=True)
add_para('（5）降级策略：岗位搜索模块在爬取失败时自动降级为提供搜索链接，确保功能可用性不受外部平台反爬机制影响。', indent=True)

add_heading_styled('7.3 不足与展望', level=2)
add_para('（1）岗位搜索局限性：受限于求职平台的反爬机制，目前仅能稳定抓取Boss直聘的部分岗位数据，猎聘和智联招聘暂无法直接抓取。未来可考虑接入官方API或使用Selenium等自动化工具。', indent=True)
add_para('（2）简历格式支持：目前PDF解析依赖PyPDF2，对扫描件PDF无法提取文本。未来可集成OCR能力（如PaddleOCR）提升PDF解析覆盖率。', indent=True)
add_para('（3）面试评估维度：当前模拟面试仅支持文本输入，无法评估语言表达、肢体语言等软技能。未来可集成语音识别和视频分析能力。', indent=True)
add_para('（4）用户数据持久化：当前系统不保存用户历史数据，每次使用需重新输入。未来可增加用户账户系统和数据持久化功能。', indent=True)
add_para('（5）多语言支持：当前系统以中文为主，对英文简历和JD的支持有限。未来可增加自动语言检测和多语言Prompt模板。', indent=True)

doc.add_paragraph()
doc.add_paragraph()

# 签名区域
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
run = p.add_run(f'报告日期：{datetime.date.today().strftime("%Y年%m月%d日")}')
run.font.name = '宋体'
run.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
run.font.size = Pt(12)

# ==================== 保存文档 ====================
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'JobFit_AI_项目报告.docx')
doc.save(output_path)
print(f'项目报告已生成：{output_path}')
