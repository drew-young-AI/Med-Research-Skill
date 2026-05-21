import asyncio
from playwright.async_api import async_playwright
import os
import sys

async def robust_download(url, filename, folder):
    """
    使用 Playwright 模擬真實瀏覽器進行下載，繞過純 CLI 工具(如 curl)會遇到的 Session 與 JS 限制。
    """
    async with async_playwright() as p:
        # 啟動真實的 Chromium 瀏覽器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            accept_downloads=True
        )
        page = await context.new_page()
        
        print(f"[*] 啟動智慧下載引擎...")
        print(f"[*] 正在導航至目標連結: {url}")
        
        try:
            # 針對特定期刊網站的行為：監聽下載事件
            async with page.expect_download(timeout=60000) as download_info:
                # 導航
                response = await page.goto(url, wait_until="load")
                
                # 如果頁面本身不是下載流，嘗試尋找頁面中的 'PDF' 或 'Download' 按鈕並點擊
                if "application/pdf" not in (response.headers.get("content-type") or ""):
                    print("[!] 頁面非直接下載流，嘗試尋找下載按鈕...")
                    # 尋找包含 PDF 字樣的連結或按鈕
                    pdf_link = page.locator("a:has-text('PDF'), a[href$='.pdf']").first
                    if await pdf_link.count() > 0:
                        await pdf_link.click()
                    else:
                        # 某些網站可能在 iframe 中或需要二次導航
                        print("[!] 未找到顯式按鈕，等待頁面自動跳轉...")

            download = await download_info.value
            save_path = os.path.join(folder, filename)
            await download.save_as(save_path)
            
            file_size = os.path.getsize(save_path)
            if file_size > 10000: # 確保大於 10KB
                print(f"[+] 成功！檔案已存至: {save_path} (大小: {file_size} bytes)")
                return True
            else:
                print(f"[-] 警告：下載的檔案過小 ({file_size} bytes)，可能下載到了錯誤頁面。")
                return False

        except Exception as e:
            print(f"[-] 下載失敗: {str(e)}")
            return False
        finally:
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python download_skill.py <URL> <FILENAME>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    target_name = sys.argv[2]
    target_folder = "Med Deep Research/papers"
    
    os.makedirs(target_folder, exist_ok=True)
    asyncio.run(robust_download(target_url, target_name, target_folder))
