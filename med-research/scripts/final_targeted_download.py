"""
Final Targeted Download - Row 01, 03, 04
Uses confirmed CrossRef PDF endpoints + preprint fallbacks.
"""
import os, ssl, json, urllib.request, urllib.parse, time

ssl._create_default_https_context = ssl._create_unverified_context
PAPERS_DIR = r"D:\project\Med Deep Research\papers"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/pdf,text/html,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
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
        print(f"    -> Redirected to: {final_url}" if final_url != url else "")
        if len(data) < 5000:
            print(f"    [WARN] Too small: {len(data)} bytes")
            return False
        with open(dest, 'wb') as f:
            f.write(data)
        if not is_valid_pdf(dest):
            print(f"    [FAIL] Not a PDF (magic bytes)")
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

results = {}

# ═══════════════════════════════════════════════════════════════════════════
# ROW 03: IJRI - PMID=30050253, PMCID=PMC6038217
# CrossRef confirmed: thieme-connect.de
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("ROW 03: A simple quality control tool (IJRI, CC BY-NC-ND 4.0)")
title_03 = "A simple quality control tool for assessing integrity of lead equivalent aprons"
fname_03 = f"{title_03}.pdf"
dest_03 = os.path.join(PAPERS_DIR, fname_03)

urls_03 = [
    # CrossRef confirmed endpoint
    ("http://www.thieme-connect.de/products/ejournals/pdf/10.4103/ijri.IJRI_374_17.pdf",
     "Thieme-CrossRef", {"Referer": "https://www.thieme-connect.de/"}),
    # PMC6038217 direct PDF with correct PMCID
    ("https://pmc.ncbi.nlm.nih.gov/articles/PMC6038217/pdf/",
     "PMC-6038217-index", {}),
    # Try common IJRI PDF naming
    ("https://www.ijri.org/article.asp?issn=0971-3026;year=2018;volume=28;issue=3;spage=347;epage=355;aulast=Jafari",
     "IJRI-article", {}),
    # EuropePMC correct ID
    ("https://europepmc.org/articles/PMC6038217?pdf=render",
     "EPMC-6038217", {}),
    # Thieme Connect via HTTPS
    ("https://www.thieme-connect.com/products/ejournals/pdf/10.4103/ijri.IJRI_374_17.pdf",
     "Thieme-HTTPS", {"Referer": "https://www.thieme-connect.com/"}),
    # Wolters Kluwer India OA
    ("https://www.lww.com/doi/10.4103/ijri.IJRI_374_17",
     "LWW-India", {}),
]

success_03 = False
for url, label, extra in urls_03:
    if try_url(url, dest_03, title_03, label, extra):
        success_03 = True
        results["03"] = {"status": "SUCCESS", "fname": fname_03, "source": label}
        break
    time.sleep(0.5)

if not success_03:
    results["03"] = {"status": "FAILED"}
    print("  [FAILED] Row 03")

# ═══════════════════════════════════════════════════════════════════════════
# ROW 04: Journal of Anesthesia (Springer) - NOT in PMC (confirmed)
# CrossRef link: link.springer.com/content/pdf/10.1007/s00540-016-2140-2.pdf
# -> returns 3038 bytes (redirect/login page)
# Strategy: Try Sci-Hub mirror (academic necessity), or preprint servers
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("ROW 04: Evaluation of lead aprons (Springer, NOT in PMC)")
title_04 = "Evaluation of lead aprons and their maintenance and management at our hospital"
fname_04 = f"{title_04}.pdf"
dest_04 = os.path.join(PAPERS_DIR, fname_04)

urls_04 = [
    # Try Springer SharedIt (free read link via DOI)
    ("https://rdcu.be/einmL", "SharedIt-1", {}),
    # Springer content with direct resolve (try https redirect)
    ("https://link.springer.com/article/10.1007/s00540-016-2140-2",
     "Springer-article-page", {}),
    # Search PubMed for preprint or free version
    # eprint via semanticscholar direct
    ("https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/s00540-016-2140-2?fields=openAccessPdf,externalIds",
     "SS-API-check", {}),
]

success_04 = False
# First check Semantic Scholar for any OA link
ss_url = "https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/s00540-016-2140-2?fields=openAccessPdf,externalIds,tldr"
try:
    req = urllib.request.Request(ss_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        ss_data = json.loads(resp.read().decode())
    oa = ss_data.get("openAccessPdf") or {}
    eids = ss_data.get("externalIds") or {}
    oa_url = oa.get("url")
    print(f"  SS: OA={oa_url}, externalIds={eids}")
    if oa_url:
        if try_url(oa_url, dest_04, title_04, "SS-OA"):
            success_04 = True
            results["04"] = {"status": "SUCCESS", "fname": fname_04, "source": "SS-OA"}
except Exception as e:
    print(f"  SS API ERR: {e}")

if not success_04:
    results["04"] = {"status": "FAILED"}
    print("  [FAILED] Row 04 - Confirmed paywalled, NOT in PMC, no OA version found")

# ═══════════════════════════════════════════════════════════════════════════
# ROW 01: Springer 2026 - Try preprint / bioRxiv / ResearchGate public
# DOI: 10.1007/s12194-026-01086-2
# Radiological Physics and Technology is published by the Japanese Society of Radiological Technology
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("ROW 01: Establishing discard criteria (Springer 2026)")
title_01 = "Establishing discard criteria for lead aprons using deep learning-based quantification of defect area on X-ray fluoroscopic video"
fname_01 = "Establishing discard criteria for lead aprons using deep learning.pdf"
dest_01 = os.path.join(PAPERS_DIR, fname_01)

success_01 = False

# Check Semantic Scholar for OA
ss_url_01 = "https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/s12194-026-01086-2?fields=openAccessPdf,externalIds"
try:
    req = urllib.request.Request(ss_url_01, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        ss_data = json.loads(resp.read().decode())
    oa = ss_data.get("openAccessPdf") or {}
    oa_url = oa.get("url")
    print(f"  SS: OA URL={oa_url}, externalIds={ss_data.get('externalIds')}")
    if oa_url and "doi.org" not in oa_url:
        if try_url(oa_url, dest_01, title_01, "SS-OA"):
            success_01 = True
            results["01"] = {"status": "SUCCESS", "fname": fname_01, "source": "SS-OA"}
except Exception as e:
    print(f"  SS API ERR: {e}")

# Try J-STAGE search (JSRT publishes in Radiological Physics and Technology)
if not success_01:
    jstage_urls = [
        ("https://www.jstage.jst.go.jp/article/rpt/-1/0/rpt_2026-01086/_pdf/-char/en", "J-STAGE-v1"),
        ("https://www.jstage.jst.go.jp/article/rpht/advpub/0/advpub_s12194-026-01086-2/_pdf/-char/en", "J-STAGE-v2"),
        ("https://www.jstage.jst.go.jp/search/-char/en?globalId=10.1007/s12194-026-01086-2&viewMode=", "J-STAGE-search"),
    ]
    for url, label in jstage_urls:
        if try_url(url, dest_01, title_01, label):
            success_01 = True
            results["01"] = {"status": "SUCCESS", "fname": fname_01, "source": label}
            break
        time.sleep(0.5)

if not success_01:
    results["01"] = {"status": "FAILED"}
    print("  [FAILED] Row 01 - Springer 2026, likely still behind paywall")

# ═══════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("FINAL TARGETED DOWNLOAD RESULTS:")
for row, res in sorted(results.items()):
    print(f"  Row {row}: {res.get('status')} | {res.get('source','N/A')} | {res.get('fname','N/A')}")
