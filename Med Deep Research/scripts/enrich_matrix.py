import json
import os
import requests

class EnrichedGARP:
    def __init__(self, raw_data_path):
        self.raw_data_path = raw_data_path
        self.output_path = os.path.join("Med Deep Research", "enriched_matrix.json")

    def load_data(self):
        with open(self.raw_data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def enrich_data(self, data):
        """
        此處模擬 Agent 的推理過程。在實際運行中，Agent 會讀取 Abstract 
        並填入相關說明與資料定義。
        """
        enriched = []
        for item in data:
            # 這裡由 Agent 的推理邏輯填入內容
            item["Relevance_Note"] = "Analyzing..." # 關聯度與是否引用
            item["Data_Definition"] = "Defining..." # 問題定義與資料類型
            enriched.append(item)
        return enriched

    def save_enriched(self, data):
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    raw_path = "research_candidates.json"
    if os.path.exists(raw_path):
        processor = EnrichedGARP(raw_path)
        raw_data = processor.load_data()
        enriched_data = processor.enrich_data(raw_data)
        processor.save_enriched(enriched_data)
        print(f"Enriched data saved to {processor.output_path}")
