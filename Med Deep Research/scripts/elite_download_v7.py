import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import os
import random

async def human_mimic_download(url, filename, folder):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # 偶爾使用 GUI 模式可提高通過率
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)
        
        print(f"[*] 精英下載 v7.0 啟動: {url}")
        try:
            await page.goto(url, wait_until="networkidle")
            
            # 模擬人類行為：閱讀、滾動
            await page.mouse.wheel(0, 800)
            await asyncio.sleep(random.uniform(3, 7))
            
            async with page.expect_download(timeout=120000) as download_info:
                # 尋找下載按鈕
                pdf_btn = page.locator("a:has-text('PDF'), a[href$='.pdf'], .pdf-download-button").first
                await pdf_btn.click()
            
            download = await download_info.value
            save_path = os.path.join(folder, filename)
            await download.save_as(save_path)
            print(f"[+] 成功！檔案已固化: {save_path}")
            return True

        except Exception as e:
            print(f"[-] 下載失敗: {e}")
            return False
        finally:
            await browser.close()

if __name__ == "__main__":
    folder = "Med Deep Research/papers"
    os.makedirs(folder, exist_ok=True)
    asyncio.run(human_mimic_download("https://www.mdpi.com/1424-8220/25/9/2650", "2025_PatchCTG_Full_Text.pdf", folder))
