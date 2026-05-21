import asyncio
from playwright.async_api import async_playwright
import os

async def download_pdf(url, filename, folder):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"正在導航至: {url}")
        try:
            # 監聽下載事件
            async with page.expect_download() as download_info:
                await page.goto(url, wait_until="networkidle")
            
            download = await download_info.value
            path = os.path.join(folder, filename)
            await download.save_as(path)
            print(f"成功下載: {filename} 至 {folder}")
        except Exception as e:
            print(f"下載 {filename} 失敗: {e}")
        
        await browser.close()

async def main():
    folder = "Med Deep Research/papers"
    os.makedirs(folder, exist_ok=True)
    
    # 定義下載清單
    tasks = [
        ("https://healthinformaticsjournal.com/index.php/fhi/article/download/1284/1184", "Kim_2024_Apron_Defects.pdf"),
        ("https://www.mdpi.com/1424-8220/25/9/2650/pdf", "PatchCTG_2025_FHR.pdf")
    ]
    
    for url, filename in tasks:
        await download_pdf(url, filename, folder)

if __name__ == "__main__":
    asyncio.run(main())
