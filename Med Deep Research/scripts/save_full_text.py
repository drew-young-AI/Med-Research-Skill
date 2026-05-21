import asyncio
from playwright.async_api import async_playwright
import os

async def save_full_text(url, filename, folder):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0")
        page = await context.new_page()
        try:
            print(f"正在擷取全文: {url}")
            await page.goto(url, wait_until="networkidle")
            content = await page.content()
            with open(os.path.join(folder, f"{filename}.html"), "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ 全文 HTML 已存檔: {filename}")
        except Exception as e:
            print(f"❌ 擷取失敗 {filename}: {e}")
        await browser.close()

async def main():
    folder = "Med Deep Research/papers"
    # 針對 Springer 或 ResearchGate 等難以下載 PDF 的頁面，儲存全文 HTML
    tasks = [
        ("https://link.springer.com/article/10.1007/s13755-025-00383-1", "2025_CTGFusionNet_fusion_of_deep_learning_models_for_predicting_fetal_distress_Mohan"),
        ("https://www.researchgate.net/publication/381144431_Prediction_Model_for_Defects_in_Lead_and_Lead-free_Aprons", "2024_Prediction_Model_for_Defects_in_Lead_and_Lead-free_Aprons_Kellens")
    ]
    for url, name in tasks:
        await save_full_text(url, name, folder)

if __name__ == "__main__":
    asyncio.run(main())
