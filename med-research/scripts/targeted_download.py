"""
Med Deep Research - Targeted Download v2.1
針對三篇失敗文獻進行精準狙擊下載
"""
import urllib.request
import urllib.parse
import ssl
import os
import re
import json

ssl._create_default_https_context = ssl._create_unverified_context

PAPERS_DIR = r"D:\project\Med Deep Research\papers"
RESULTS = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def is_valid_pdf(path):
    try:
        with open(path, 'rb') as f:
            return f.read(5) == b'%PDF-'
    except:
        return False

def download(url, dest, extra_headers=None):
    headers = dict(HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    try:
        req = urllib.request.Request(url, headers=headers)
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

# ──────────────────────────────────────────────────────────
# ROW 04: PMID 26842670 → EuropePMC 直接 PDF 抓取
# ──────────────────────────────────────────────────────────
print("=" * 60)
print("Row 04: Evaluation of lead aprons (PMID: 26842670)")
fname_04 = "Evaluation of lead aprons and their maintenance and management at our hospital.pdf"
dest_04 = os.path.join(PAPERS_DIR, fname_04)

# Try 1: EuropePMC PDF render by PMID
urls_04 = [
    "https://europepmc.org/articles/PMC4799263?pdf=render",     # try common PMCID pattern
    "https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC4799263&blobtype=pdf",
    "https://pubmed.ncbi.nlm.nih.gov/26842670/",
    "https://link.springer.com/content/pdf/10.1007/s00540-016-2140-2.pdf",
]

success_04 = False
for url in urls_04:
    print(f"  Trying: {url}")
    if download(url, dest_04):
        if is_valid_pdf(dest_04):
            print(f"  [SUCCESS] Row 04 PDF valid! {os.path.getsize(dest_04):,} bytes")
            RESULTS["04"] = {"status": "SUCCESS", "fname": fname_04, "type": "PDF", "url": url}
            success_04 = True
            break
        else:
            print(f"  [WARN] Not valid PDF (HTML likely)")
            if os.path.exists(dest_04):
                os.remove(dest_04)

# Try 2: Semantic Scholar PDF url for Row 04
if not success_04:
    print("  [Tier-SS] Semantic Scholar full text link...")
    ss_url = "https://api.semanticscholar.org/graph/v1/paper/10.1007/s00540-016-2140-2?fields=openAccessPdf,externalIds"
    try:
        req = urllib.request.Request(ss_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        oa = data.get("openAccessPdf")
        if oa:
            print(f"  SS OA URL: {oa}")
            if download(oa.get("url",""), dest_04):
                if is_valid_pdf(dest_04):
                    print(f"  [SUCCESS] Row 04 via SS! {os.path.getsize(dest_04):,} bytes")
                    RESULTS["04"] = {"status": "SUCCESS", "fname": fname_04, "type": "PDF"}
                    success_04 = True
        # Also try PubMed PMC link
        eids = data.get("externalIds", {})
        pmcid = eids.get("PubMedCentral")
        if pmcid and not success_04:
            pdf_url = f"https://europepmc.org/articles/{pmcid}?pdf=render"
            print(f"  PMC from SS: PMC{pmcid} -> {pdf_url}")
            if download(pdf_url, dest_04):
                if is_valid_pdf(dest_04):
                    print(f"  [SUCCESS] Row 04 via PMC! {os.path.getsize(dest_04):,} bytes")
                    RESULTS["04"] = {"status": "SUCCESS", "fname": fname_04, "type": "PDF"}
                    success_04 = True
    except Exception as e:
        print(f"  [ERR] SS Row04: {e}")

if not success_04:
    print("  [FAILED] Row 04 all attempts exhausted.")
    RESULTS["04"] = {"status": "FAILED", "fname": None, "type": None}

# ──────────────────────────────────────────────────────────
# ROW 01: Springer 2026 (Radiological Physics and Technology)
# 可能在 J-STAGE 有 OA 版本
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Row 01: Establishing discard criteria (Springer 2026)")
fname_01 = "Establishing discard criteria for lead aprons using deep learning-based quantification of defect area on X-ray fluoroscopic video.pdf"
fname_01 = fname_01[:120] + ".pdf" if not fname_01.endswith(".pdf") else fname_01
dest_01 = os.path.join(PAPERS_DIR, fname_01)

urls_01 = [
    # J-STAGE (Japanese Science and Technology Agency) - Radiological Physics and Technology is Japanese journal
    "https://www.jstage.jst.go.jp/article/rpht/19/2/19_s12194-026-01086-2/_pdf",
    "https://www.jstage.jst.go.jp/article/rpht/19/2/19_s12194-026-01086-2/_pdf/-char/en",
    # ResearchGate PDF (author uploaded)
    "https://www.researchgate.net/publication/392843781_Establishing_discard_criteria_for_lead_aprons_using_deep_learning-based_quantification_of_defect_area_on_X-ray_fluoroscopic_video/fulltext/downloads",
    # Springer OA check
    "https://link.springer.com/content/pdf/10.1007/s12194-026-01086-2.pdf",
]

success_01 = False
for url in urls_01:
    print(f"  Trying: {url}")
    if download(url, dest_01):
        if is_valid_pdf(dest_01):
            print(f"  [SUCCESS] Row 01 PDF valid! {os.path.getsize(dest_01):,} bytes")
            RESULTS["01"] = {"status": "SUCCESS", "fname": fname_01, "type": "PDF", "url": url}
            success_01 = True
            break
        else:
            print(f"  [WARN] Not valid PDF")
            if os.path.exists(dest_01):
                os.remove(dest_01)

# J-STAGE search by DOI
if not success_01:
    print("  [Tier-JSTAGE] Searching J-STAGE by DOI...")
    jstage_url = f"https://api.jstage.jst.go.jp/searchapi/do?service=3&query=10.1007%2Fs12194-026-01086-2&lang=en"
    try:
        req = urllib.request.Request(jstage_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode(errors="ignore")
        print(f"  J-STAGE response preview: {content[:500]}")
    except Exception as e:
        print(f"  [ERR] J-STAGE: {e}")

if not success_01:
    print("  [FAILED] Row 01 all attempts exhausted.")
    RESULTS["01"] = {"status": "FAILED", "fname": None, "type": None}

# ──────────────────────────────────────────────────────────
# ROW 06: IOP Publishing 2026 - Radiation Protection Dosimetry
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Row 06: Occupational dose attenuation scoping review (IOP 2026)")
fname_06 = "Occupational dose attenuation and dosimetric performance of autonomous radiation protection systems in fluoroscopy.pdf"
dest_06 = os.path.join(PAPERS_DIR, fname_06)

urls_06 = [
    # IOPscience direct PDF
    "https://iopscience.iop.org/article/10.1088/1361-6498/ae7122/pdf",
    "https://iopscience.iop.org/article/10.1088/1361-6498/ae7122/ampdf",
    # EuropePMC try by DOI
    "https://europepmc.org/search?query=DOI:10.1088/1361-6498/ae7122",
]

success_06 = False
for url in urls_06:
    print(f"  Trying: {url}")
    if download(url, dest_06):
        if is_valid_pdf(dest_06):
            print(f"  [SUCCESS] Row 06 PDF valid! {os.path.getsize(dest_06):,} bytes")
            RESULTS["06"] = {"status": "SUCCESS", "fname": fname_06, "type": "PDF", "url": url}
            success_06 = True
            break
        else:
            print(f"  [WARN] Not valid PDF")
            if os.path.exists(dest_06):
                os.remove(dest_06)

# Try Semantic Scholar for Row 06
if not success_06:
    print("  [Tier-SS] Semantic Scholar...")
    try:
        ss_url = "https://api.semanticscholar.org/graph/v1/paper/10.1088/1361-6498/ae7122?fields=openAccessPdf,externalIds"
        req = urllib.request.Request(ss_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        oa = data.get("openAccessPdf")
        eids = data.get("externalIds", {})
        print(f"  SS data: OA={oa}, externalIds={eids}")
        pmcid = eids.get("PubMedCentral")
        if pmcid:
            pdf_url = f"https://europepmc.org/articles/{pmcid}?pdf=render"
            print(f"  PMC: {pdf_url}")
            if download(pdf_url, dest_06):
                if is_valid_pdf(dest_06):
                    RESULTS["06"] = {"status": "SUCCESS", "fname": fname_06, "type": "PDF"}
                    success_06 = True
                    print(f"  [SUCCESS] Row 06 via PMC!")
                else:
                    if os.path.exists(dest_06):
                        os.remove(dest_06)
        if oa and not success_06:
            oa_url = oa.get("url", "")
            if oa_url:
                print(f"  SS OA URL: {oa_url}")
                if download(oa_url, dest_06):
                    if is_valid_pdf(dest_06):
                        RESULTS["06"] = {"status": "SUCCESS", "fname": fname_06, "type": "PDF"}
                        success_06 = True
                        print(f"  [SUCCESS] Row 06 via SS OA URL!")
    except Exception as e:
        print(f"  [ERR] SS Row06: {e}")

if not success_06:
    print("  [FAILED] Row 06 all attempts exhausted.")
    RESULTS["06"] = {"status": "FAILED", "fname": None, "type": None}

# ──────────────────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("TARGETED DOWNLOAD RESULTS:")
for row, res in RESULTS.items():
    print(f"  Row {row}: {res['status']} | {res['type']} | {res['fname']}")

results_path = os.path.join(PAPERS_DIR, "targeted_results.json")
with open(results_path, "w", encoding="utf-8") as f:
    json.dump(RESULTS, f, ensure_ascii=False, indent=2)
print(f"\nSaved: {results_path}")
