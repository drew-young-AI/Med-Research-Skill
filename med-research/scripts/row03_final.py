"""
Row 03 Final: Try PMC4962047 (different PMCID found in efetch)
Row 01: Try PubMed abstract page to find any free link
"""
import os, ssl, json, urllib.request, time
ssl._create_default_https_context = ssl._create_unverified_context

PAPERS_DIR = r"D:\project\Med Deep Research\papers"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/pdf,text/html,*/*;q=0.8",
}

def is_valid_pdf(path):
    try:
        with open(path, 'rb') as f:
            return f.read(5) == b'%PDF-'
    except: return False

def content_check(path, title):
    try:
        import pypdf
        reader = pypdf.PdfReader(path)
        text = ''.join((reader.pages[i].extract_text() or '') for i in range(min(2, len(reader.pages))))
        text_lower = text.lower().replace('-', ' ')
        for pw in ['purchase', 'subscribe', 'access to this article', 'log in']:
            if pw in text_lower:
                return False, f"PAYWALL:{pw}"
        sig = [w for w in title.lower().replace('-',' ').split() if len(w) > 3]
        if not sig: return True, "OK"
        matched = sum(1 for w in sig if w in text_lower)
        ratio = matched / len(sig)
        return ratio >= 0.3, f"{ratio:.0%} ({matched}/{len(sig)})"
    except Exception as e:
        return False, str(e)

def try_url(url, dest, title, label, extra_headers=None):
    h = dict(HEADERS)
    if extra_headers:
        h.update(extra_headers)
    print(f"  [{label}] {url}")
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            final_url = resp.geturl()
        if final_url != url:
            print(f"    -> {final_url}")
        if len(data) < 5000:
            print(f"    [WARN] Too small: {len(data)} bytes")
            return False
        with open(dest, 'wb') as f:
            f.write(data)
        if not is_valid_pdf(dest):
            print(f"    [FAIL] Not a PDF")
            try: os.remove(dest)
            except: pass
            return False
        ok, msg = content_check(dest, title)
        if ok:
            print(f"    [SUCCESS] {msg} | {os.path.getsize(dest):,} bytes")
            return True
        else:
            print(f"    [FAIL] Content: {msg}")
            try: os.remove(dest)
            except: pass
            return False
    except Exception as e:
        print(f"    [ERR] {e}")
        return False

# ── Row 03: Try PMC4962047 (second PMC found in efetch) ──────────────────
print("=" * 70)
print("ROW 03: PMC4962047 attempt")
title_03 = "A simple quality control tool for assessing integrity of lead equivalent aprons"
fname_03 = f"{title_03}.pdf"
dest_03 = os.path.join(PAPERS_DIR, fname_03)

success_03 = False
for pmcid in ["PMC4962047"]:
    for url, label in [
        (f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/pdf/", f"PMC-{pmcid}-index"),
        (f"https://europepmc.org/articles/{pmcid}?pdf=render", f"EPMC-{pmcid}"),
        (f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/", f"NCBI-{pmcid}"),
    ]:
        if try_url(url, dest_03, title_03, label):
            success_03 = True
            break
        time.sleep(0.5)
    if success_03:
        break

# Try exact PMC PDF URL patterns for IJRI journal
if not success_03:
    ijri_urls = [
        ("https://pmc.ncbi.nlm.nih.gov/articles/PMC6038217/pdf/IJRI-28-347.pdf", "PMC-IJRI-28-347"),
        ("https://pmc.ncbi.nlm.nih.gov/articles/PMC6038217/pdf/IJRI-28-3-347.pdf", "PMC-IJRI-v2"),
    ]
    for url, label in ijri_urls:
        if try_url(url, dest_03, title_03, label):
            success_03 = True
            break
        time.sleep(0.5)

print(f"Row 03 result: {'SUCCESS' if success_03 else 'FAILED'}")

# ── Row 01: Try J-STAGE API to get correct article handle ────────────────
print("\n" + "=" * 70)
print("ROW 01: J-STAGE API search for correct article path")
title_01 = "Establishing discard criteria for lead aprons using deep learning-based quantification of defect area on X-ray fluoroscopic video"
fname_01 = "Establishing discard criteria for lead aprons using deep learning.pdf"
dest_01 = os.path.join(PAPERS_DIR, fname_01)

# J-STAGE API search by title keywords
jstage_api = "https://api.jstage.jst.go.jp/searchapi/do?service=3&query=lead+apron+discard+criteria+deep+learning&lang=en&count=5"
try:
    req = urllib.request.Request(jstage_api, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        xml = resp.read().decode(errors="ignore")
    print(f"J-STAGE API response (first 1000 chars):\n{xml[:1000]}")
except Exception as e:
    print(f"J-STAGE API ERR: {e}")

# Also try Springer SharedIt via doi.org resolution chain
print("\nTrying Springer/doi.org resolution for Row 01:")
doi_url = "https://doi.org/10.1007/s12194-026-01086-2"
try:
    req = urllib.request.Request(doi_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        final = resp.geturl()
    print(f"  DOI resolves to: {final}")
except Exception as e:
    print(f"  ERR: {e}")
