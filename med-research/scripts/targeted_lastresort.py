"""
Targeted Last-Resort Download for Row 01, 03, 04
Uses journal-specific direct PDF endpoints that the generic tiers missed.
"""
import os
import ssl
import json
import urllib.request

ssl._create_default_https_context = ssl._create_unverified_context

PAPERS_DIR = r"D:\project\Med Deep Research\papers"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

def is_valid_pdf(path):
    try:
        with open(path, 'rb') as f:
            return f.read(5) == b'%PDF-'
    except:
        return False

def content_check(path, title):
    try:
        import pypdf
        reader = pypdf.PdfReader(path)
        text = ''
        for i in range(min(2, len(reader.pages))):
            text += (reader.pages[i].extract_text() or '')
        text_lower = text.lower().replace('-', ' ')
        title_words = set(title.lower().replace('-', ' ').split())
        sig = [w for w in title_words if len(w) > 3]
        if not sig:
            return True, "NO_SIG"
        matched = sum(1 for w in sig if w in text_lower)
        ratio = matched / len(sig)
        return ratio >= 0.3, f"{ratio:.0%} ({matched}/{len(sig)})"
    except Exception as e:
        return False, str(e)

def download(url, dest, referer=None):
    h = dict(HEADERS)
    if referer:
        h["Referer"] = referer
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) < 5000:
            print(f"    [WARN] Too small: {len(data)} bytes")
            return False
        with open(dest, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"    [ERR] {e}")
        return False

def try_url(url, dest, title, label, referer=None):
    print(f"  [{label}] {url}")
    if download(url, dest, referer):
        if not is_valid_pdf(dest):
            print(f"    [FAIL] Not a PDF")
            try: os.remove(dest)
            except: pass
            return False
        ok, msg = content_check(dest, title)
        if ok:
            print(f"    [SUCCESS] Content validated: {msg} | {os.path.getsize(dest):,} bytes")
            return True
        else:
            print(f"    [FAIL] Content: {msg}")
            try: os.remove(dest)
            except: pass
    return False

results = {}

# ─────────────────────────────────────────────────────────────
# ROW 03: IJRI (Indian Journal of Radiology and Imaging) - OA
# DOI: 10.4103/ijri.IJRI_374_17, PMID: 30319195
# IJRI is published by Wolters Kluwer India, fully Open Access
# ─────────────────────────────────────────────────────────────
print("=" * 70)
print("ROW 03: A simple quality control tool for assessing integrity of lead equivalent aprons")
title_03 = "A simple quality control tool for assessing integrity of lead equivalent aprons"
fname_03 = f"{title_03}.pdf"
dest_03 = os.path.join(PAPERS_DIR, fname_03)

urls_03 = [
    # IJRI direct downloadpdf endpoint (Wolters Kluwer India OA)
    ("https://www.ijri.org/downloadpdf.asp?issn=0971-3026;year=2018;volume=28;issue=3;spage=347;epage=355;aulast=Jafari", "IJRI-direct"),
    # PMC NCBI direct PDF
    ("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6166353/pdf/IJRI-28-347.pdf", "PMC-direct"),
    # PMC FTP-style
    ("https://pmc.ncbi.nlm.nih.gov/articles/PMC6166353/pdf/IJRI-28-347.pdf", "PMC-new"),
    # Alternate PMC PDF render
    ("https://europepmc.org/articles/PMC6166353?pdf=render", "EPMC-render"),
]

success_03 = False
for url, label in urls_03:
    if try_url(url, dest_03, title_03, label, referer="https://www.ijri.org/"):
        success_03 = True
        results["03"] = {"status": "SUCCESS", "fname": fname_03, "source": label}
        break

if not success_03:
    results["03"] = {"status": "FAILED"}
    print("  [FAILED] Row 03")

# ─────────────────────────────────────────────────────────────
# ROW 04: Journal of Anesthesia (Springer) - PMC4799263
# DOI: 10.1007/s00540-016-2140-2, PMID: 26842670
# This is an OA article (CC BY 4.0) per PMC
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("ROW 04: Evaluation of lead aprons and their maintenance and management at our hospital")
title_04 = "Evaluation of lead aprons and their maintenance and management at our hospital"
fname_04 = f"{title_04}.pdf"
dest_04 = os.path.join(PAPERS_DIR, fname_04)

urls_04 = [
    # PMC NCBI direct PDF (Journal of Anesthesia format)
    ("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4799263/pdf/540_2016_Article_2140.pdf", "PMC-direct"),
    ("https://pmc.ncbi.nlm.nih.gov/articles/PMC4799263/pdf/540_2016_Article_2140.pdf", "PMC-new"),
    # Springer OA PDF (sometimes the /content/pdf path works for OA articles)
    ("https://link.springer.com/content/pdf/10.1007/s00540-016-2140-2", "Springer-PDF"),
    # EuropePMC with correct render
    ("https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC4799263&blobtype=pdf", "EPMC-backend"),
]

success_04 = False
for url, label in urls_04:
    if try_url(url, dest_04, title_04, label, referer="https://www.ncbi.nlm.nih.gov/"):
        success_04 = True
        results["04"] = {"status": "SUCCESS", "fname": fname_04, "source": label}
        break

if not success_04:
    results["04"] = {"status": "FAILED"}
    print("  [FAILED] Row 04")

# ─────────────────────────────────────────────────────────────
# ROW 01: Radiological Physics and Technology (Springer 2026)
# DOI: 10.1007/s12194-026-01086-2
# Very new (2026), likely paywalled. Try SharedIt / RDCu link.
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("ROW 01: Establishing discard criteria for lead aprons (Springer 2026)")
title_01 = "Establishing discard criteria for lead aprons using deep learning-based quantification of defect area on X-ray fluoroscopic video"
fname_01 = f"{title_01}.pdf"
dest_01 = os.path.join(PAPERS_DIR, fname_01)

urls_01 = [
    # Springer SharedIt (sometimes open for new articles)
    ("https://rdcu.be/d3abc", "SharedIt-guess"),
    # Springer direct content PDF
    ("https://link.springer.com/content/pdf/10.1007/s12194-026-01086-2.pdf", "Springer-PDF"),
    # Try J-STAGE (Radiological Physics and Technology is a Japanese journal published via Springer)
    ("https://www.jstage.jst.go.jp/article/rpt/advpub/0/advpub_2026-01086/_pdf/-char/en", "J-STAGE-advpub"),
    # ResearchGate public (will likely 403, but try)
    ("https://www.researchgate.net/profile/publication/392843781/fulltext/downloads", "RG-public"),
]

success_01 = False
for url, label in urls_01:
    if try_url(url, dest_01, title_01, label):
        success_01 = True
        results["01"] = {"status": "SUCCESS", "fname": fname_01, "source": label}
        break

if not success_01:
    results["01"] = {"status": "FAILED"}
    print("  [FAILED] Row 01")

# ─────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("TARGETED DOWNLOAD RESULTS:")
for row, res in sorted(results.items()):
    print(f"  Row {row}: {res.get('status')} | {res.get('source', 'N/A')} | {res.get('fname', 'N/A')}")

with open(os.path.join(PAPERS_DIR, "targeted_v3_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
