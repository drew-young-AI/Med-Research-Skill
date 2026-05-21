import google.generativeai as genai
import json
import os
import logging
from dotenv import load_dotenv

# 載入 .env
load_dotenv(os.path.join("etc", ".env"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class ResearchAnalyst:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("未在 .env 中找到 GEMINI_API_KEY！")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_abstracts(self, papers, topic):
        """分析摘要並篩選高價值文獻"""
        if not self.model:
            return "錯誤：缺少 API Key，無法進行 AI 分析。"

        logger.info(f"正在分析 {len(papers)} 篇文獻的價值...")
        
        # 建立分析 Prompt
        paper_summaries = ""
        for i, p in enumerate(papers):
            paper_summaries += f"--- Paper {i+1} ---\nTitle: {p.get('title')}\nAbstract: {p.get('abstract')}\n\n"

        prompt = f"""
你是一位專業的醫學 AI 研究助理。請針對以下研究題目分析文獻：
題目：{topic}

文獻列表：
{paper_summaries}

任務：
1. 根據題目相關性，從 1-10 分評分每篇文獻。
2. 總結這組文獻中的核心技術趨勢 (SOTA)。
3. 指出目前文獻中尚未解決的缺口 (Research Gaps)。
4. 篩選出最值得深度閱讀的 3 篇文獻。

請以繁體中文回答，並輸出 JSON 格式以便後續處理。
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"分析失敗: {e}")
            return str(e)

if __name__ == "__main__":
    analyst = ResearchAnalyst()
    # 這裡預期讀取之前產出的 JSON
    results_path = os.path.join("Med Deep Research", "initial_search_lead_apron.json")
    if os.path.exists(results_path):
        with open(results_path, "r", encoding="utf-8") as f:
            papers = json.load(f)
        
        analysis = analyst.analyze_abstracts(papers, "鉛防護衣在醫學與X光機的應用")
        print("\n=== AI 文獻分析結果 ===")
        print(analysis)
    else:
        print("請先運行 discovery.py 獲取文獻數據。")
