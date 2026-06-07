# JobFit AI - 简历岗位智能匹配与面试分析器

基于大模型API的一站式求职助手：智能解析简历→搜索求职平台→推荐匹配岗位→分析适配度→优化简历→AI模拟面试。

## 功能列表

1. **智能推荐**：输入简历，AI自动提取意向岗位/城市/薪资/技能栈，搜索Boss直聘/猎聘/智联招聘，推荐最匹配岗位并分析适配度
2. **岗位搜索**：根据关键词+城市搜索多个求职平台，生成搜索链接
3. **匹配分析**：输入简历+岗位JD，AI分析匹配度评分、匹配/缺失技能、优势不足、改进建议
4. **简历优化**：针对目标岗位，AI给出关键词建议、经历描述优化、行动清单
5. **面试题生成**：根据岗位JD自动生成针对性面试题+参考答案+评分标准
6. **模拟面试**：交互式模拟面试，AI出题→你答→AI点评，给出评分和改进建议

## 环境要求

- Python 3.10+
- 大模型API Key（支持 DeepSeek / OpenAI / 阿里云通义千问 等兼容接口）

## 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/jobfit-ai.git
cd jobfit-ai

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置API Key
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key 和配置
```

`.env` 配置示例：

```env
# DeepSeek
LLM_API_KEY=your-deepseek-api-key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# 或 阿里云通义千问
LLM_API_KEY=your-dashscope-api-key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus

# 或 OpenAI
LLM_API_KEY=your-openai-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

## 运行示例

### CLI 模式

```bash
# 智能推荐（核心功能：解析简历→搜索岗位→推荐分析→模拟面试）
python main.py recommend -r data/sample_resume.txt

# 指定推荐岗位序号直接进入模拟面试
python main.py recommend -r data/sample_resume.txt -i 1

# 搜索求职平台岗位
python main.py search -r data/sample_resume.txt

# 匹配分析
python main.py match -r data/sample_resume.txt -j data/sample_jd.txt

# 匹配分析 + 导出报告
python main.py match -r data/sample_resume.txt -j data/sample_jd.txt -o report.md

# 简历优化
python main.py optimize -r data/sample_resume.txt -j data/sample_jd.txt

# 生成5道面试题
python main.py interview -j data/sample_jd.txt --count 5

# 交互式模拟面试（3题）
python main.py mock -j data/sample_jd.txt --count 3
```

### Web 模式（Streamlit）

```bash
streamlit run app.py
```

浏览器打开后即可使用可视化界面，包含6个功能标签页。

## 项目结构

```
jobfit-ai/
├── main.py                 # CLI入口（click命令组）
├── app.py                  # Streamlit Web界面（6个标签页）
├── config.py               # API配置与常量
├── requirements.txt        # Python依赖
├── .env.example            # 环境变量模板
├── .gitignore
├── analyzer/
│   ├── resume_parser.py    # 简历智能解析（提取意向/技能/项目）
│   ├── job_searcher.py     # 求职平台搜索（Boss直聘/猎聘/智联）
│   ├── job_recommender.py  # 岗位推荐与适配度分析
│   ├── matcher.py          # 匹配分析核心逻辑
│   ├── optimizer.py        # 简历优化建议
│   ├── interviewer.py      # 面试题生成+模拟面试评估
│   └── prompts.py          # 所有Prompt模板
├── utils/
│   ├── llm.py              # 大模型API调用封装
│   └── report.py           # 报告生成与导出
├── data/
│   ├── sample_resume.txt   # 示例简历（含求职意向）
│   └── sample_jd.txt       # 示例岗位JD
└── tests/
    └── test_basic.py       # 基础测试
```

## 主要功能 + 实现方式

| 功能 | 实现方式 |
|------|----------|
| 简历解析 | LLM提取结构化信息：意向岗位、城市、薪资、技能分类、项目经历、工作年限 |
| 岗位搜索 | 构造Boss直聘/猎聘/智联招聘搜索URL，尝试抓取岗位列表，提供平台搜索链接 |
| 岗位推荐 | 结合搜索结果+简历技能栈，LLM推荐5个匹配岗位，含适配度评分和优化建议 |
| 匹配分析 | 简历+JD作为上下文，LLM输出结构化JSON（评分/匹配项/缺失项/建议） |
| 简历优化 | Prompt引导LLM从关键词、经历描述、结构三个维度给出优化建议 |
| 面试题生成 | 根据JD生成不同类型（技术/行为/项目/场景）面试题，含参考答案和评分标准 |
| 模拟面试 | 先生成面试题，用户逐题作答，LLM评估回答质量并给出改进建议 |
| API封装 | 统一封装OpenAI兼容接口，支持DeepSeek/通义千问/OpenAI等，一行配置切换 |

## 常见问题

**Q: 报错"未设置 LLM_API_KEY"**
A: 请在项目根目录创建 `.env` 文件并填入API Key，参考 `.env.example`。

**Q: 支持哪些大模型API？**
A: 支持所有兼容OpenAI接口的API，包括 DeepSeek、阿里云通义千问、OpenAI、智谱AI等。只需修改 `.env` 中的 `LLM_BASE_URL` 和 `LLM_MODEL`。

**Q: 岗位搜索抓取不到数据？**
A: 求职平台有反爬机制，可能无法直接抓取。此时系统会：1）提供各平台搜索链接供手动查看；2）AI仍会根据简历技能栈推荐匹配岗位。

**Q: 分析结果不准确怎么办？**
A: 可以尝试：1）提供更详细的简历和JD；2）切换更强大的模型（如 qwen-max、deepseek-reasoner）；3）修改 `analyzer/prompts.py` 中的Prompt模板。
