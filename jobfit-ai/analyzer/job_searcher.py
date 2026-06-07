"""岗位搜索 - 搜索Boss直聘/猎聘/智联招聘等求职平台"""

import re
import json
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup


# 平台搜索URL模板
PLATFORM_URLS = {
    "boss直聘": "https://www.zhipin.com/web/geek/job?query={keyword}&city={city_code}",
    "猎聘": "https://www.liepin.com/zhaopin/?key={keyword}&city={city_code}",
    "智联招聘": "https://sou.zhaopin.com/?jl={city_code}&kw={keyword}",
}

# 城市编码映射
CITY_CODES = {
    "北京": "101010100",
    "上海": "101020100",
    "广州": "101280100",
    "深圳": "101280600",
    "杭州": "101210100",
    "成都": "101270100",
    "南京": "101190100",
    "武汉": "101200100",
    "西安": "101110100",
    "重庆": "101040100",
    "苏州": "101190400",
    "天津": "101030100",
    "长沙": "101250100",
    "郑州": "101180100",
    "东莞": "101281600",
    "沈阳": "101070100",
    "青岛": "101120200",
    "合肥": "101220100",
    "佛山": "101280800",
    "昆明": "101290100",
}

# Boss直聘城市编码
BOSS_CITY_CODES = {
    "北京": "101010100",
    "上海": "101020100",
    "广州": "101280100",
    "深圳": "101280600",
    "杭州": "101210100",
    "成都": "101270100",
    "南京": "101190100",
    "武汉": "101200100",
    "西安": "101110100",
    "重庆": "101040100",
    "苏州": "101190400",
    "天津": "101030100",
    "长沙": "101250100",
    "郑州": "101180100",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def get_city_code(city: str, platform: str = "boss") -> str:
    """获取城市编码"""
    if platform == "boss":
        return BOSS_CITY_CODES.get(city, "101010100")
    return CITY_CODES.get(city, "101010100")


def generate_search_urls(keyword: str, city: str) -> list:
    """生成各平台的搜索URL列表

    Args:
        keyword: 搜索关键词（岗位名称）
        city: 城市名称

    Returns:
        [{"platform": "平台名", "url": "搜索URL", "keyword": keyword, "city": city}]
    """
    encoded_keyword = quote(keyword)
    results = []

    for platform, url_template in PLATFORM_URLS.items():
        city_code = get_city_code(city, "boss" if "boss" in platform else "default")
        url = url_template.format(keyword=encoded_keyword, city_code=city_code)
        results.append({
            "platform": platform,
            "url": url,
            "keyword": keyword,
            "city": city,
        })

    return results


def search_boss(keyword: str, city: str) -> list:
    """搜索Boss直聘岗位（尝试抓取，失败则返回空列表）

    Args:
        keyword: 搜索关键词
        city: 城市

    Returns:
        岗位列表
    """
    jobs = []
    try:
        city_code = get_city_code(city, "boss")
        url = f"https://www.zhipin.com/web/geek/job?query={quote(keyword)}&city={city_code}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            job_cards = soup.find_all("div", class_="job-card-wrapper")
            for card in job_cards[:10]:
                try:
                    title_el = card.find("span", class_="job-name")
                    salary_el = card.find("span", class_="salary")
                    company_el = card.find("h3", class_="company-name")
                    tag_el = card.find("div", class_="job-info")
                    location_el = card.find("span", class_="job-area")

                    title = title_el.get_text(strip=True) if title_el else ""
                    salary = salary_el.get_text(strip=True) if salary_el else "面议"
                    company = company_el.get_text(strip=True) if company_el else ""
                    tags = tag_el.get_text(strip=True) if tag_el else ""
                    location = location_el.get_text(strip=True) if location_el else city

                    if title:
                        jobs.append({
                            "title": title,
                            "salary": salary,
                            "company": company,
                            "tags": tags,
                            "location": location,
                            "platform": "Boss直聘",
                            "url": url,
                        })
                except Exception:
                    continue
    except Exception:
        pass

    return jobs


def search_jobs(keyword: str, city: str) -> dict:
    """搜索多个平台的岗位

    Args:
        keyword: 搜索关键词
        city: 城市

    Returns:
        {"search_urls": [...], "jobs": [...], "platform_status": {...}}
    """
    # 生成搜索URL
    search_urls = generate_search_urls(keyword, city)

    # 尝试抓取Boss直聘
    jobs = search_boss(keyword, city)

    platform_status = {}
    for item in search_urls:
        platform_status[item["platform"]] = {
            "url": item["url"],
            "scraped": item["platform"] == "Boss直聘" and len(jobs) > 0,
            "job_count": len([j for j in jobs if j["platform"] == item["platform"]]),
        }

    return {
        "search_urls": search_urls,
        "jobs": jobs,
        "platform_status": platform_status,
    }


def search_multi_keywords(keywords: list, cities: list) -> dict:
    """多关键词多城市搜索

    Args:
        keywords: 关键词列表
        cities: 城市列表

    Returns:
        汇总搜索结果
    """
    all_jobs = []
    all_urls = []
    seen_titles = set()

    for keyword in keywords:
        for city in cities:
            result = search_jobs(keyword, city)
            for job in result["jobs"]:
                job_key = f"{job['title']}_{job['company']}"
                if job_key not in seen_titles:
                    seen_titles.add(job_key)
                    all_jobs.append(job)
            all_urls.extend(result["search_urls"])

    # 去重URL
    seen_urls = set()
    unique_urls = []
    for u in all_urls:
        if u["url"] not in seen_urls:
            seen_urls.add(u["url"])
            unique_urls.append(u)

    return {
        "search_urls": unique_urls,
        "jobs": all_jobs,
        "total_found": len(all_jobs),
    }
