import os
import requests
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class ResearchDiscovery:
    def __init__(self):
        self.arxiv_api_url = "http://export.arxiv.org/api/query"

    def search_arxiv(self, query, max_results=10):
        """透過 arXiv 搜尋學術論文 (無需 API Key)"""
        logger.info(f"正在搜尋 arXiv: {query}")
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results
        }
        
        try:
            response = requests.get(self.arxiv_api_url, params=params, timeout=30)
            response.raise_for_status()
            
            # 解析 XML
            root = ET.fromstring(response.text)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            results = []
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text.strip()
                summary = entry.find('atom:summary', ns).text.strip()
                published = entry.find('atom:published', ns).text
                pdf_url = ""
                for link in entry.findall('atom:link', ns):
                    if link.attrib.get('title') == 'pdf' or link.attrib.get('type') == 'application/pdf':
                        pdf_url = link.attrib.get('href')
                
                results.append({
                    "title": title,
                    "abstract": summary,
                    "year": published[:4],
                    "url": pdf_url,
                    "source": "arXiv"
                })
            return results
        except Exception as e:
            logger.error(f"arXiv 搜尋出錯: {e}")
            return []

    def save_results(self, results, filename):
        path = os.path.join("Med Deep Research", filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"搜尋結果已儲存至 {path}")

if __name__ == "__main__":
    discovery = ResearchDiscovery()
    topic = "lead protective clothing X-ray medical radiation protection"
    
    results = discovery.search_arxiv(topic, max_results=10)
    if results:
        discovery.save_results(results, "discovery_arxiv_lead_apron.json")
        print(f"\n成功從 arXiv 找到 {len(results)} 篇相關論文！")
        for i, paper in enumerate(results):
            print(f"[{i+1}] {paper.get('title')} ({paper.get('year')})")
    else:
        print("未找到相關文獻。")
