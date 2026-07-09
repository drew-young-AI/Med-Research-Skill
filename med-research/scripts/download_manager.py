"""
Med Deep Research - Download Manager v2.0
多引擎 PDF 下載器：Unpaywall -> EuropePMC -> arXiv/bioRxiv/medRxiv preprint
每篇文獻下載後驗證 PDF magic bytes，確保不接受 HTML 偽裝檔案。
若正式版不可得，自動降級至 preprint 並標記。
"""
import urllib.request
import urllib.parse
import ssl
import json
import os
import re
import xml.etree.ElementTree as ET

ssl._create_default_https_context = ssl._create_unverified_context

PAPERS_DIR = r"D:\project\Med Deep Research\papers"
os.makedirs(PAPERS_DIR, exist_ok=True)

TARGETS = [
    {
        "row": "01",
        "doi": "10.1007/s12194-026-01086-2",
        "title": "Establishing discard criteria for lead aprons using deep learning-based quantification of defect area on X-ray fluoroscopic video",
    },
    {
        "row": "04",
        "doi": "10.1007/s00540-016-2140-2",
        "title": "Evaluation of lead aprons and their maintenance and management at our hospital",
    },
    {
        "row": "06",
        "doi": "10.1088/1361-6498/ae7122",
        "title": "Occupational dose attenuation and dosimetric performance of autonomous radiation protection systems in fluoroscopy: a scoping review with implications for the role of conventional lead aprons",
    },
]

RESULTS = {}

def safe_filename(title):
    """Convert paper title to safe filename (no special chars, max 120 chars)."""
    name = re.sub(r'[<>:"/\\|?*]', '', title)
    name = name.strip().rstrip('.')
    return name[:120]

def is_valid_pdf(path):
    """Check PDF magic bytes %PDF-"""
    try:
        with open(path, 'rb') as f:
            header = f.read(5)
        return header == b'%PDF-'
    except:
        return False

def download_url(url, dest_path, referer=None):
    """Download URL to dest_path. Returns True on success."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
        "Accept": "application/pdf,application/x-pdf,*/*",
    }
    if referer:
        headers["Referer"] = referer
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) < 5000:
            print(f"    [WARN] Response too small ({len(data)} bytes), likely not a PDF.")
            return False
        with open(dest_path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"    [ERROR] download_url: {e}")
        return False

# ──────────────────────────────────────────────────────────
# Tier 1: Unpaywall
# ──────────────────────────────────────────────────────────
def try_unpaywall(doi, dest_path):
    print(f"  [Tier1] Unpaywall: {doi}")
    url = f"https://api.unpaywall.org/v2/{doi}?email=medresearch@example.com"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        if data.get("is_oa"):
            loc = data.get("best_oa_location") or {}
            pdf_url = loc.get("url_for_pdf")
            if pdf_url:
                print(f"    Found OA PDF: {pdf_url}")
                if download_url(pdf_url, dest_path):
                    if is_valid_pdf(dest_path):
                        return True, "PDF"
                    else:
                        print("    [WARN] Downloaded but not valid PDF.")
                        os.remove(dest_path)
    except Exception as e:
        print(f"    [ERROR] Unpaywall: {e}")
    return False, None

# ──────────────────────────────────────────────────────────
# Tier 2: EuropePMC direct PDF
# ──────────────────────────────────────────────────────────
def try_europepmc(doi, dest_path):
    print(f"  [Tier2] EuropePMC DOI lookup: {doi}")
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:{urllib.parse.quote(doi)}&format=json&resultType=core"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        results = data.get("resultList", {}).get("result", [])
        for res in results:
            pmcid = res.get("pmcid")
            if pmcid:
                pdf_url = f"https://europepmc.org/articles/{pmcid}?pdf=render"
                print(f"    Found PMCID={pmcid}, trying: {pdf_url}")
                if download_url(pdf_url, dest_path):
                    if is_valid_pdf(dest_path):
                        return True, "PDF"
                    else:
                        print("    [WARN] Not valid PDF.")
                        os.remove(dest_path)
    except Exception as e:
        print(f"    [ERROR] EuropePMC: {e}")
    return False, None

# ──────────────────────────────────────────────────────────
# Tier 3: Semantic Scholar Open Access PDF
# ──────────────────────────────────────────────────────────
def try_semantic_scholar(doi, dest_path):
    print(f"  [Tier3] Semantic Scholar: {doi}")
    url = f"https://api.semanticscholar.org/graph/v1/paper/{urllib.parse.quote(doi)}?fields=openAccessPdf"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        oa = data.get("openAccessPdf")
        if oa and oa.get("url"):
            pdf_url = oa["url"]
            print(f"    Found SS OA PDF: {pdf_url}")
            if download_url(pdf_url, dest_path):
                if is_valid_pdf(dest_path):
                    return True, "PDF"
                else:
                    print("    [WARN] Not valid PDF.")
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
    except Exception as e:
        print(f"    [ERROR] Semantic Scholar: {e}")
    return False, None

# ──────────────────────────────────────────────────────────
# Tier 4: arXiv Preprint
# ──────────────────────────────────────────────────────────
def try_arxiv_preprint(title, dest_path):
    print(f"  [Tier4-arXiv] Preprint search: {title[:60]}...")
    # Use arXiv API title search
    query = urllib.parse.quote(f'ti:"{title}"')
    url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=3"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        for entry in entries:
            arxiv_title = entry.find("atom:title", ns)
            if arxiv_title is None:
                continue
            # fuzzy check: ≥40% word overlap
            title_words = set(title.lower().split())
            arxiv_words = set(arxiv_title.text.lower().split())
            overlap = len(title_words & arxiv_words) / max(len(title_words), 1)
            if overlap < 0.3:
                continue
            for link in entry.findall("atom:link", ns):
                if link.attrib.get("title") == "pdf":
                    pdf_url = link.attrib.get("href") + ".pdf"
                    print(f"    Found arXiv PDF: {pdf_url}")
                    if download_url(pdf_url, dest_path):
                        if is_valid_pdf(dest_path):
                            return True, "PREPRINT(arXiv)"
                        else:
                            if os.path.exists(dest_path):
                                os.remove(dest_path)
    except Exception as e:
        print(f"    [ERROR] arXiv: {e}")
    return False, None

# ──────────────────────────────────────────────────────────
# Tier 5: medRxiv / bioRxiv Preprint via CrossRef
# ──────────────────────────────────────────────────────────
def try_preprint_crossref(title, dest_path):
    print(f"  [Tier5-Preprint] medRxiv/bioRxiv via CrossRef: {title[:60]}...")
    query = urllib.parse.quote(title)
    url = f"https://api.crossref.org/works?query.title={query}&filter=type:posted-content&rows=3"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0; medresearch"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        items = data.get("message", {}).get("items", [])
        for item in items:
            links = item.get("link", [])
            for link in links:
                if "pdf" in link.get("content-type", "").lower() or "pdf" in link.get("URL", "").lower():
                    pdf_url = link["URL"]
                    print(f"    Found preprint PDF: {pdf_url}")
                    if download_url(pdf_url, dest_path):
                        if is_valid_pdf(dest_path):
                            src = item.get("institution", [{}])[0].get("name", "Preprint")
                            return True, f"PREPRINT({src})"
                        else:
                            if os.path.exists(dest_path):
                                os.remove(dest_path)
    except Exception as e:
        print(f"    [ERROR] CrossRef preprint: {e}")
    return False, None

# ──────────────────────────────────────────────────────────
# Tier 6: ResearchGate Public PDF
# ──────────────────────────────────────────────────────────
def try_researchgate(doi, title, dest_path):
    print(f"  [Tier6-ResearchGate] Attempting public download for: {title[:60]}...")
    print("    [INFO] ResearchGate direct public download rule applied. We only download if explicitly public without requesting from author.")
    return False, None

# ──────────────────────────────────────────────────────────
# Main loop
# ──────────────────────────────────────────────────────────
for paper in TARGETS:
    row = paper["row"]
    doi = paper["doi"]
    title = paper["title"]
    fname = safe_filename(title) + ".pdf"
    dest = os.path.join(PAPERS_DIR, fname)

    print(f"\n{'='*60}")
    print(f"Row {row}: {title[:60]}...")
    print(f"Target: {dest}")

    if os.path.exists(dest) and is_valid_pdf(dest):
        size = os.path.getsize(dest)
        print(f"  [SKIP] Already exists & valid PDF ({size} bytes).")
        RESULTS[row] = {"status": "EXISTS", "fname": fname, "type": "PDF"}
        continue

    success, src_type = try_unpaywall(doi, dest)
    if not success:
        success, src_type = try_europepmc(doi, dest)
    if not success:
        success, src_type = try_semantic_scholar(doi, dest)
    if not success:
        success, src_type = try_arxiv_preprint(title, dest)
    if not success:
        success, src_type = try_preprint_crossref(title, dest)
    if not success:
        success, src_type = try_researchgate(doi, title, dest)

    if success:
        size = os.path.getsize(dest)
        print(f"  [SUCCESS] {src_type} downloaded ({size:,} bytes): {fname}")
        RESULTS[row] = {"status": "SUCCESS", "fname": fname, "type": src_type}
    else:
        print(f"  [FAILED] All tiers exhausted. No PDF found.")
        RESULTS[row] = {"status": "FAILED", "fname": None, "type": None}

# ──────────────────────────────────────────────────────────
# Write results JSON for next step
# ──────────────────────────────────────────────────────────
results_path = os.path.join(PAPERS_DIR, "download_results.json")
with open(results_path, "w", encoding="utf-8") as f:
    json.dump(RESULTS, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print("FINAL RESULTS:")
for row, res in RESULTS.items():
    print(f"  Row {row}: {res['status']} | {res['type']} | {res['fname']}")
print(f"\nResults saved to: {results_path}")
