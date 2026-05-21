import requests
import json
import os
import re

class GARPOrchestrator:
    def __init__(self):
        self.s2_api_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    def fetch_candidates(self, query, limit=15):
        """獲取學術文獻候選名單"""
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,authors,year,abstract,citationCount,externalIds,url,isOpenAccess"
        }
        try:
            response = requests.get(self.s2_api_url, params=params, timeout=20)
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as e:
            return []

    def generate_matrix_row(self, paper):
        """生成單行矩陣內容 (初稿，後續由 Agent 豐富化)"""
        title = paper.get("title", "N/A")
        year = paper.get("year", "N/A")
        citations = paper.get("citationCount", 0)
        url = paper.get("url", "#")
        
        # 簡單提取關鍵字 (後續由 Agent 透過 LLM 處理摘要)
        abstract = paper.get("abstract", "")
        methodology = "Scanning..." 
        
        return {
            "Title": f"[{title}]({url})",
            "Year": year,
            "Citations": citations,
            "Methodology": methodology,
            "Gap": "Analyzing...",
            "Raw_Abstract": abstract
        }

if __name__ == "__main__":
    # 範例調度
    orchestrator = GARPOrchestrator()
    # 這裡可以用任何 Topic 測試
    topic = "lead-free radiation shielding composites"
    candidates = orchestrator.fetch_candidates(topic)
    
    matrix_data = [orchestrator.generate_matrix_row(p) for p in candidates]
    
    with open("research_candidates.json", "w", encoding="utf-8") as f:
        json.dump(matrix_data, f, ensure_ascii=False, indent=2)
