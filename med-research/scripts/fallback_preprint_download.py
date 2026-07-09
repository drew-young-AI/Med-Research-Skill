import os
import json
import urllib.request
import urllib.parse
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

PAPERS_DIR = r'D:\project\Med Deep Research\papers'
RESULTS_PATH = os.path.join(PAPERS_DIR, 'targeted_results.json')

# Load existing results to get missing rows and DOIs
with open(RESULTS_PATH, 'r', encoding='utf-8') as f:
    results = json.load(f)

# Helper download function (reuse from targeted_download)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def is_valid_pdf(path):
    try:
        with open(path, 'rb') as f:
            return f.read(5) == b'%PDF-'
    except Exception:
        return False

def download(url, dest):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) < 5000:
            print(f"    [WARN] Too small ({len(data)} bytes) from {url}")
            return False
        with open(dest, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"    [ERR] {e} ({url})")
        return False

# Mapping from row to DOI (hard‑coded from master matrix for now)
ROW_DOI = {
    "01": "10.1007/s12194-026-01086-2",
    "06": "10.1088/1361-6498/ae7122",
}

# Title extraction for naming PDFs
ROW_TITLE = {
    "01": "Establishing discard criteria for lead aprons using deep learning-based quantification of defect area on X-ray fluoroscopic video",
    "06": "Occupational dose attenuation and dosimetric performance of autonomous radiation protection systems in fluoroscopy",
}

for row, info in results.items():
    if info.get('status') != 'SUCCESS':
        doi = ROW_DOI.get(row)
        title = ROW_TITLE.get(row)
        if not doi:
            continue
        fname = f"{title}.pdf"
        dest = os.path.join(PAPERS_DIR, fname)
        # 1. Try Semantic Scholar OA PDF (openAccessPdf)
        ss_url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf"
        try:
            req = urllib.request.Request(ss_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                ss_data = json.loads(resp.read().decode())
            oa = ss_data.get('openAccessPdf')
            if oa and oa.get('url'):
                print(f"[ROW {row}] Trying SS OA PDF: {oa['url']}")
                if download(oa['url'], dest) and is_valid_pdf(dest):
                    results[row] = {"status": "SUCCESS", "fname": fname, "type": "PDF", "source": "SemanticScholar"}
                    continue
        except Exception as e:
            print(f"[ROW {row}] SS error: {e}")
        # 2. Try Unpaywall (via https://api.unpaywall.org/v2/DOI?email=you@example.com) – no email required for fallback, use demo.
        unpay_url = f"https://api.unpaywall.org/v2/{doi}?email=demo@example.com"
        try:
            req = urllib.request.Request(unpay_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                up_data = json.loads(resp.read().decode())
            best_url = up_data.get('best_oa_location', {}).get('url')
            if best_url:
                print(f"[ROW {row}] Trying Unpaywall OA: {best_url}")
                if download(best_url, dest) and is_valid_pdf(dest):
                    results[row] = {"status": "SUCCESS", "fname": fname, "type": "PDF", "source": "Unpaywall"}
                    continue
        except Exception as e:
            print(f"[ROW {row}] Unpaywall error: {e}")
        # 3. Fallback: try DOI resolver to see if it redirects to a preprint server
        doi_resolver = f"https://doi.org/{doi}"
        try:
            req = urllib.request.Request(doi_resolver, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                final_url = resp.geturl()
            if final_url != doi_resolver:
                print(f"[ROW {row}] DOI resolved to {final_url}")
                if download(final_url, dest) and is_valid_pdf(dest):
                    results[row] = {"status": "SUCCESS", "fname": fname, "type": "PDF", "source": "DOIResolver"}
                    continue
        except Exception as e:
            print(f"[ROW {row}] DOI resolver error: {e}")
        # If all attempts fail, keep FAILED
        results[row] = {"status": "FAILED", "fname": None, "type": None}

# Write back updated results
with open(RESULTS_PATH, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print('Fallback preprint download completed.')
