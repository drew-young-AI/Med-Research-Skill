# Med Deep Research - Specific Mandates (v6.6 Master)

## 通用自主研究協議 (General Autonomous Research Protocol - GARP)

### A. 本地知識基座架構 (Project Knowledge Base - PKB)
為了提供類似 **NotebookLM** 的深度分析體驗，系統必須建立「實體驅動型知識庫」：
- **存續義務**：所有 `Reference Source` 必須優先連結至 `/papers` 中的實體檔案。
- **RAG 準備**：Agent 必須能呼叫 `knowledge_aggregator.py` 獲取所有本地文獻的聯集 Context，進行跨文獻對話。

### C. 決策矩陣標準與硬約束 (Standard Matrix v6.6)
為了維持「95分以上的完美狀態」，Master 報告必須嚴格遵守：
- **欄位硬約束**：強制執行 **10 欄位** 標準（含 JCR 指標、相似度對比、高密度方法論等）。
- **內容密度**：`Methodology` 欄位內容必須包含架構與演算法巧思，嚴禁縮減為簡述。
- **Row 數規範**：精選 5 篇文獻。**第 5 篇固定為 [Overview] Paper** 以利領域導讀。
- **本地路徑優先**：`Reference Source` 連結必須優先指向 `/papers` 資料夾中的實體檔案。


### I. 深度技術節錄擴充規範 (Expanded Excerpts)
- **不可僅有簡述**：解析必須包含「臨床挑戰 (Why)」、「技術架構 (How)」與「專案對標 (Project Mapping)」。
- **代碼導向**：若文獻包含算法巧思，必須描述其數據流（如：Patching 邏輯、Attention Map 權重）。
