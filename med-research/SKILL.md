---
name: med-research
description: High-fidelity medical research and AI consensus engine. v10.2 implements publisher-aware fallback, 5-tier download ladder, PDF integrity validation, and Markdown table safety rules.
---

# Medical Research Skill v10.2 (JCR Rigor & 1:1 Evidence Mastery)

## 1. 核心研究能力 (Core Capabilities)
1.  **JCR/IF 強制驗證**: 所有選入矩陣的文獻必須具備 JCR 分區 (Q1/Q2) 與實體 Impact Factor (IF)。嚴禁使用無 IF 的 ESCI 或 Pre-print 文獻，除非使用者明確要求。
2.  **1:1 數據誠信協議**: 每一行報告必須通過「DOI -> 標題 -> 技術細節」的實體校驗。嚴禁數據交叉污染或幻覺。
3.  **單篇深度剖析協議**: 若使用者要求「單篇」報告，Agent 必須展現極致的技術深度，涵蓋算法、物理建模與臨床對標。

## 2. 決策矩陣標準與硬約束 (Standard Matrix v10.0)
為了維持「95分以上的完美狀態」，報告必須嚴格遵守 **10 欄位** 標準。嚴禁擅自修改欄位名稱或順序。

### 統一欄位規範 (Unified Columns):
1.  **# / DOI / JCR (IF)**: 編號、實體連結與期刊權威指標。
2.  **論文標題 (1:1 對標)**: 必須與出版商索引完全一致。
3.  **核心算法/架構**: 具體算法名稱（如 CNN, Random Forest）。
4.  **數據規模/工程細節**: 樣本數、影像解析度、DICOM 深度等。
5.  **臨床挑戰 (Why)**: 該研究解決了什麼臨床痛點。
6.  **技術巧思/細節 (How)**: 算法的核心巧思（如 CLAHE, Feature Pyramid）。
7.  **實驗結果 (SOTA)**: 具體數據（Acc, F1, Precision）。
8.  **數據流 Logic**: 從輸入到輸出的邏輯鏈結。
9.  **瓶頸/開發難度**: 實作中可能遇到的技術坑位。
10. **專案對標 / 研究利基**: 目標臨床落地方案與未來發表點。

## 3. 出版商感知與下載梯隊 (Download Ladder v10.2)
當執行文獻獲取時，必須遵循以下「五層下載階梯」：

1.  **Tier 1: Unpaywall API** - 優先以 DOI 查詢合法的 Open Access PDF URL。
2.  **Tier 2: EuropePMC** - 以 DOI 反查 PMCID，再以 `https://europepmc.org/articles/{PMCID}?pdf=render` 下載。
3.  **Tier 3: Semantic Scholar** - 以 DOI 查詢 `openAccessPdf` 欄位，取得 OA PDF URL。
4.  **Tier 4: arXiv Preprint** - 以論文標題進行模糊搜尋，若標題詞彙重疊 ≥30% 即接受，下載 PDF。
5.  **Tier 5: CrossRef / medRxiv / bioRxiv** - 以標題查詢 posted-content，尋找 Preprint PDF 連結。

### 下載後強制驗證 (PDF Integrity Check):
- **每次下載後**，必須讀取檔案前 5 bytes，確認為 `%PDF-` magic bytes。
- 若驗證失敗（即下載到 HTML 偽裝檔案），**強制刪除**該檔案並進入下一 Tier。
- **最小有效大小**: 5,000 bytes。小於此值視為無效。

### HTML 偽裝防禦 (Fake PDF Defense):
若所有 Tier 均失敗，但曾成功取得 HTML 全文（如 Ovid SPA 頁面），可使用 Python `reportlab` + `html.parser` 進行本地端文本萃取，重新封裝為合法 PDF。執行後同樣需通過 magic bytes 驗證。

## 4. 報告 Markdown 格式強制規範 (Markdown Safety Rules v10.2)

### 4.1 欄內多連結的分隔符規則 (CRITICAL)
- 在同一個 Markdown 表格欄位內，若需並列多個連結（如 PDF + Web），**強制使用 `\|` (反斜線加管道符)** 作為欄內分隔符。
- **嚴禁使用未跳脫的 `|`**，否則 Markdown 解析器會將其誤認為新欄位分隔符，導致整行表格結構右移崩潰。

```
✅ 正確: [PDF](../papers/foo.pdf) \| [Web](https://doi.org/...)
❌ 錯誤: [PDF](../papers/foo.pdf) | [Web](https://doi.org/...)
```

### 4.2 URL 空白字元跳脫規則 (CRITICAL)
- 在 `[文字](URL)` 的 URL 部分，若檔名或路徑含有空白字元，**強制替換為 `%20`**。
- 原始空白會導致 Markdown 解析器截斷連結，造成連結破圖與表格渲染錯誤。

```
✅ 正確: [PDF](../papers/Deep%20Learning%20Model.pdf)
❌ 錯誤: [PDF](../papers/Deep Learning Model.pdf)
```

### 4.3 欄位內禁止使用行內括號備註
- 不在表格欄位內使用 `*(備註文字)*` 格式添加補充說明。
- 含有分號 `;`、冒號 `:` 或括號的備註文字，容易在部分渲染器中觸發格式錯誤。
- **正確做法**：備註資訊應寫入報告的「深度技術剖析」章節，而非嵌入表格欄位。

### 4.4 檔名句號結尾防護
- 當論文標題末尾有句號（如 `...exposure.`），以標題為檔名時，**必須去除末尾句號**，再接上副檔名 `.pdf`。
- 防止 `title..pdf`（雙句號）導致的副檔名辨識問題。

```python
# 正確的檔名清理邏輯
safe_title = title.rstrip('.').replace(':', '').replace('/', '-')
filename = safe_title[:120] + '.pdf'
```

## 5. Preprint 標注規則
- 若最終使用的是 Preprint 版本，必須在第 10 欄位的連結後標記來源，格式為：
  `[PDF (PREPRINT)](../papers/xxx.pdf) \| [Web (arXiv)](https://arxiv.org/...)`
- 同時在「數據規模/工程細節」欄位末尾標注 `[Source: Preprint/arXiv]`。
