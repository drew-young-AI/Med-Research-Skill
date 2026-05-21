import os
import sys

def aggregate_knowledge(papers_dir):
    """
    模擬 NotebookLM 的 Source 整合邏輯。
    遍歷 /papers 資料夾，將 PDF 轉存的文本、HTML 與 Summary 整合為一個大型 Context。
    """
    knowledge_base = ""
    print(f"[*] 正在掃描知識庫: {papers_dir}")
    
    files = [f for f in os.listdir(papers_dir) if f.endswith(('.txt', '.html', '.md'))]
    for filename in files:
        path = os.path.join(papers_dir, filename)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            knowledge_base += f"\n\n=== SOURCE: {filename} ===\n{content[:5000]}\n" # 限制每篇長度避免爆 Context
            
    return knowledge_base

if __name__ == "__main__":
    kb = aggregate_knowledge("Med Deep Research/papers")
    print(f"[+] 知識基座已生成，總字數: {len(kb)}")
    # 此輸出可被 Agent 直接讀取作為 RAG 基礎
