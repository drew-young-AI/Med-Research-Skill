import asyncio
from playwright.async_api import async_playwright
import os

async def archive_paper(url, filename_base, folder):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"正在嘗試存檔: {url}")
        try:
            # 1. 嘗試下載 PDF
            try:
                async with page.expect_download(timeout=15000) as download_info:
                    # 針對某些網址直接導航就會觸發下載
                    await page.goto(url, wait_until="load")
                
                download = await download_info.value
                pdf_path = os.path.join(folder, f"{filename_base}.pdf")
                await download.save_as(pdf_path)
                
                # 檢查檔案大小是否合理 (> 50KB)
                if os.path.getsize(pdf_path) > 50000:
                    print(f"✅ PDF 下載成功: {pdf_path}")
                    await browser.close()
                    return
                else:
                    print(f"⚠️ PDF 檔案過小 ({os.path.getsize(pdf_path)} bytes)，可能為無效頁面，啟動網頁存檔...")
            except Exception:
                print("❌ 無法直接下載 PDF，啟動網頁文本存檔...")

            # 2. 網頁文本存檔 (Fallback)
            await page.goto(url, wait_until="networkidle")
            # 擷取主要內容 (嘗試尋找常見的文章容器)
            content = await page.evaluate("() => document.body.innerText")
            html_content = await page.content()
            
            txt_path = os.path.join(folder, f"{filename_base}_Archive.txt")
            html_path = os.path.join(folder, f"{filename_base}_Archive.html")
            
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(content)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            print(f"✅ 網頁內容已成功存檔至: {txt_path} 與 .html")

        except Exception as e:
            print(f"🛑 存檔 {filename_base} 徹底失敗: {e}")
        
        await browser.close()

async def main():
    folder = "Med Deep Research/papers"
    os.makedirs(folder, exist_ok=True)
    
    # 定義任務清單 (優先使用文章檢視頁，而非直接 PDF 連結，以便執行 Fallback)
    tasks = [
        ("https://healthinformaticsjournal.com/index.php/fhi/article/view/1284", "Kim_2024_Apron_Defects"),
        ("https://www.mdpi.com/1424-8220/25/9/2650", "PatchCTG_2025_FHR")
    ]
    
    for url, filename in tasks:
        await archive_paper(url, filename, folder)

if __name__ == "__main__":
    asyncio.run(main())
