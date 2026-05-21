import asyncio
from playwright.async_api import async_playwright
import os
import sys

async def elite_download(url, filename, folder):
    """
    精英級下載引擎 v2：強化按鈕偵測與 Session 保持。
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            accept_downloads=True
        )
        page = await context.new_page()
        print(f"[*] 執行高保真下載: {url}")
        
        try:
            # 先建立 Session
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # 監聽下載
            async with page.expect_download(timeout=120000) as download_info:
                # 策略 A: 尋找實體 PDF 下載按鈕
                pdf_btn = page.locator("a:has-text('Download PDF'), a.UD_Listings_ArticlePDF, a[href$='/pdf'], button:has-text('PDF')").first
                if await pdf_btn.is_visible():
                    print("[*] 偵測到下載按鈕，執行模擬點擊...")
                    await pdf_btn.click()
                else:
                    # 策略 B: 強制重定向至 PDF 串流
                    print("[!] 未見按鈕，嘗試導航至 PDF 串流網址...")
                    target = url if url.endswith("/pdf") else f"{url}/pdf"
                    await page.goto(target, wait_until="load")
            
            download = await download_info.value
            save_path = os.path.join(folder, filename)
            await download.save_as(save_path)
            print(f"[+] 成功獲取實體檔案: {filename} ({os.path.getsize(save_path)} bytes)")
            return True
        except Exception as e:
            print(f"[-] 下載失敗: {e}")
            return False
        finally:
            await browser.close()

if __name__ == "__main__":
    folder = "Med Deep Research/papers"
    os.makedirs(folder, exist_ok=True)
    asyncio.run(elite_download("https://www.mdpi.com/1424-8220/25/9/2650", "2025_PatchCTG_Full_Text.pdf", folder))
