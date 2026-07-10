import asyncio
import os

from playwright.async_api import async_playwright

try:
    from playwright_stealth import stealth_async
except ImportError:
    stealth_async = None


class UniversalDownloader:
    """
    Universal downloader with multiple fallback strategies.
    """

    def __init__(self, folder="Med Deep Research/papers", headless=True):
        self.folder = folder
        self.headless = headless
        os.makedirs(self.folder, exist_ok=True)
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        )

    async def _verify_content(self, file_path):
        """Verify that the downloaded file looks like a PDF or HTML document."""
        if not os.path.exists(file_path):
            return False

        size = os.path.getsize(file_path)
        if size < 5000:
            return False

        with open(file_path, "rb") as f:
            header = f.read(16).lower()
            if header.startswith(b"%pdf"):
                return "PDF"
            if b"<html" in header or b"<!doc" in header:
                return "HTML"

        return "UNKNOWN"

    async def download(self, url, filename):
        """Execute a download task with multiple fallback strategies."""
        save_path = os.path.join(self.folder, filename)
        result = {"success": False, "type": None, "path": save_path, "msg": ""}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent=self.user_agent,
                accept_downloads=True,
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()

            if stealth_async is not None:
                await stealth_async(page)

            try:
                print(f"[*] Task: {filename} -> {url}")

                # Strategy 1: direct navigation and download monitoring.
                try:
                    async with page.expect_download(timeout=30000) as download_info:
                        response = await page.goto(url, wait_until="commit", timeout=20000)
                        if response and response.status == 403:
                            raise Exception("HTTP 403 Access Denied")

                    download = await download_info.value
                    await download.save_as(save_path)
                    if await self._verify_content(save_path) == "PDF":
                        result.update({"success": True, "type": "PDF", "msg": "Direct download success"})
                        return result
                except Exception as e:
                    print(f"[*] Strategy 1 failed: {str(e)[:80]}")

                # Strategy 2: click an explicit PDF link or button.
                try:
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    selectors = [
                        "a:has-text('Download PDF')",
                        "a:has-text('Full Text PDF')",
                        "a[href$='.pdf']",
                        "button:has-text('PDF')",
                        ".pdf-link",
                        ".download-link",
                    ]
                    for selector in selectors:
                        btn = page.locator(selector).first
                        if await btn.is_visible():
                            print(f"[*] Found selector {selector}, attempting click...")
                            async with page.expect_download(timeout=30000) as download_info:
                                await btn.click()
                            download = await download_info.value
                            await download.save_as(save_path)
                            if await self._verify_content(save_path) == "PDF":
                                result.update(
                                    {
                                        "success": True,
                                        "type": "PDF",
                                        "msg": f"Button click success ({selector})",
                                    }
                                )
                                return result
                except Exception as e:
                    print(f"[*] Strategy 2 failed: {str(e)[:80]}")

                # Strategy 3: print to PDF as a final PDF fallback.
                try:
                    print("[*] Strategy 3: Print to PDF...")
                    await page.pdf(path=save_path, format="A4", print_background=True)
                    if await self._verify_content(save_path) == "PDF":
                        result.update({"success": True, "type": "PRINT", "msg": "Print to PDF success"})
                        return result
                except Exception as e:
                    print(f"[*] Strategy 3 failed: {str(e)[:80]}")

                # Strategy 4: store the HTML as a final fallback.
                try:
                    print("[*] Strategy 4: HTML archive...")
                    content = await page.content()
                    html_path = save_path.replace(".pdf", ".html")
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    result.update({"success": True, "type": "HTML", "path": html_path, "msg": "HTML fallback success"})
                except Exception as e:
                    result["msg"] = f"All strategies failed: {str(e)}"

            except Exception as e:
                result["msg"] = f"Critical failure: {str(e)}"
            finally:
                await browser.close()

        return result


async def main():
    downloader = UniversalDownloader()
    res = await downloader.download(
        "https://www.researchgate.net/publication/381144431_Prediction_Model_for_Defects_in_Lead_and_Lead-free_Aprons",
        "Kellens_2024_Test.pdf",
    )
    print(f"Result: {res}")


if __name__ == "__main__":
    asyncio.run(main())
