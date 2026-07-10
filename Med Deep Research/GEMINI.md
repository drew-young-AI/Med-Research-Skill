# Med Deep Research - Specific Mandates (v12.0 Master)

## 通用自主研究協議 (General Autonomous Research Protocol - GARP)

### A. 本地知識基座架構 (Project Knowledge Base - PKB)
- **實體檔案優先**：所有 `Reference Source` 必須優先連結至 `/papers` 中存在的實體 PDF 檔案。
- **RAG 架構**：Agent 必須能呼叫 `knowledge_aggregator.py` 獲取所有本地文獻的聯集 Context 進行跨文獻對話。

### C. 決策矩陣標準與硬約束 (Standard Matrix v12.0)
- **8 欄位標準**：強制執行 **8 欄位** 標準，表格中**嚴禁**包含任何 `專案對標 (CYCH)` 欄位。
- **欄位定義**：
  1. # / DOI / JCR (IF) (年份)
  2. 論文標題 (1:1 對標)
  3. 核心算法 / 物理邏輯
  4. 工程參數 / 標定值
  5. 技術巧思 (How)
  6. 實驗結果 (SOTA)
  7. 數據流 Logic
  8. 參考文獻 (PDF / Web)
- **內容密度**：技術巧思與算法邏輯必須具體描述，嚴禁縮減為簡述。

### I. 深度技術節錄規範
- **客觀分析**：解析必須包含「物理維度」、「預測/AI維度」與「落地實作步驟」。
- **代碼/數據流導向**：必須描述算法的具體數據流（如：CNN-Transformer 多尺度特徵融合、PVR 灰階比對）。

---

## 4. 學習與改進指南 (Lessons Learned & Anti-Regression Rules)

### 4.1 表格解析與重構防偏斜
- **修復管線對齊**：重構 Markdown 表格行時，嚴禁在首尾管線 `|` 前後產生多餘空格，或多出雙重 `|`。必須對分割後的 parts 數組進行 strip 處理，並以 `| ` 與 ` |` 包裹。

### 4.2 PDF 雙軌下載優先序
- **優先 Unpaywall**：下載文獻時，應優先查詢 Unpaywall API 獲取合法 Open Access 直連 PDF 下載連結，以避免 Sci-Hub 403 阻擋。
- **Sci-Hub 降級**：當 Unpaywall 無 OA 連結時，方降級到 Sci-Hub 鏡像站嘗試抓取。

### 4.3 零情緒寫作規範 (Zero Emotional Bias)
- **嚴禁自誇**：報告中嚴禁出現任何自我讚揚或描述產出品質的詞彙（如「95分以上的完美狀態」、「無懈可擊」、「品質突破」、「修復」）。
- **嚴禁情緒字眼**：全篇僅能使用中立、客觀、邏輯通順的學術與技術語言。
- **自測通過**：每次產生或更新報告後，必須在本地執行 `verify_integrity.py` 驗證其編碼相容性、排版與數據一致性，自測通過後方能交付。
