import requests, re, json
from concurrent.futures import ThreadPoolExecutor

# 多源抓取模块
def fetch_source(source):
    try:
        resp = requests.get(source['url'], timeout=10)
        if source['type'] == 'api':
            return parse_api(resp.json())
        elif source['type'] == 'm3u':
            return parse_m3u(resp.text)
    except:
        return []

# 数据清洗模块
def parse_m3u(content):
    return re.findall(r'^https?://\S+\.m3u8?$', content, re.MULTILINE)

def parse_api(data):
    return [item['url'] for item in data['streams'] if item['is_public']]

# 有效性验证模块
def check_stream(url):
    try:
        r = requests.head(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        return url if r.status_code == 200 else None
    except:
        return None

# 主流程
if __name__ == "__main__":
    with open('../sources/sources.json') as f:
        sources = json.load(f)
    
    # 多线程采集
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_source, sources))
    
    # 合并去重
    all_urls = list(set([url for sublist in results for url in sublist]))
    
    # 有效性验证
    with ThreadPoolExecutor(max_workers=10) as executor:
        valid_urls = list(filter(None, executor.map(check_stream, all_urls)))
    
    # 生成结果
    with open('../public/live_sources.txt', 'w') as f:
        f.write("\n".join(valid_urls))
