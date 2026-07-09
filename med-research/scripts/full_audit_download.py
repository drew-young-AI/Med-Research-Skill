"""
Med Deep Research - Full Audit & Download v3.0
===============================================
Phase 1: Content-Aware Validation (Anti-Honeypot) on ALL existing PDFs
Phase 2: Multi-Tier Download for missing/invalid PDFs
Phase 3: Report summary
"""
import os
import sys
import json
import urllib.request
import urllib.parse
import ssl
import time

ssl._create_default_https_context = ssl._create_unverified_context

PAPERS_DIR = r"D:\project\Med Deep Research\papers"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ─── Master Matrix: All 8 Rows ───────────────────────────────────────────
ROWS = [
    {
        "row": "01",
        "doi": "10.1007/s12194-026-01086-2",
        "title": "Establishing discard criteria for lead aprons using deep learning-based quantification of defect area on X-ray fluoroscopic video",
        "fname": "Establishing discard criteria for lead aprons using deep learning-based quantification of defect area on X-ray fluoroscopic video.pdf",
        "pmid": None,
        "pmcid": None,
    },
    {
        "row": "02",
        "doi": "10.1097/HP.0000000000001847",
        "title": "Prediction Model for Defects in Lead and Lead-Free Aprons",
        "fname": "Prediction Model for Defects in Lead and Lead-Free Aprons.pdf",
        "pmid": None,
        "pmcid": None,
    },
    {
        "row": "03",
        "doi": "10.4103/ijri.IJRI_374_17",
        "title": "A simple quality control tool for assessing integrity of lead equivalent aprons",
        "fname": "A simple quality control tool for assessing integrity of lead equivalent aprons.pdf",
        "pmid": "30319195",
        "pmcid": "PMC6166353",
    },
    {
        "row": "04",
        "doi": "10.1007/s00540-016-2140-2",
        "title": "Evaluation of lead aprons and their maintenance and management at our hospital",
        "fname": "Evaluation of lead aprons and their maintenance and management at our hospital.pdf",
        "pmid": "26842670",
        "pmcid": "PMC4799263",
    },
    {
        "row": "05",
        "doi": "10.30699/fhi.v13i7.1284",
        "title": "Development of a Model for Predicting Defects in Radiation Shielding Aprons Using Machine Learning",
        "fname": "Development of a Model for Predicting Defects in Radiation Shielding Aprons Using Machine Learning.pdf",
        "pmid": None,
        "pmcid": None,
    },
    {
        "row": "06",
        "doi": "10.2139/ssrn.5373992",
        "title": "Development of a Computational Algorithm for the Automation of Quality Control in Leaded Personal Protective Equipment",
        "fname": "Development of a Computational Algorithm for the Automation of Quality.pdf",
        "pmid": None,
        "pmcid": None,
        "ssrn": "5373992",
    },
    {
        "row": "07",
        "doi": "10.1093/rpd/ncaf174",
        "title": "Monte Carlo calculations of the radiation absorbed dose to a fetus of a pregnant patient from a dental bitewing X-ray exposure",
        "fname": "Monte Carlo calculations of the radiation absorbed dose to a fetus of a pregnant patient from a dental bitewing X-ray exposure.pdf",
        "pmid": "40354870",
        "pmcid": None,
    },
    {
        "row": "08",
        "doi": None,
        "title": "The Lambert and McKeon (Pillay and Stam) Rejection Criteria for Lead Aprons",
        "fname": None,  # Clinical standard, no PDF expected
        "pmid": None,
        "pmcid": None,
    },
]

# ─── Utility Functions ───────────────────────────────────────────────────

def is_valid_pdf(path):
    """Check PDF magic bytes."""
    try:
        with open(path, 'rb') as f:
            return f.read(5) == b'%PDF-'
    except Exception:
        return False

def content_aware_validate(path, title):
    """Anti-Honeypot: extract text from first 2 pages and check title keyword match."""
    try:
        import pypdf
        reader = pypdf.PdfReader(path)
        text = ''
        for i in range(min(2, len(reader.pages))):
            text += reader.pages[i].extract_text() or ''

        text_lower = text.lower().replace('-', ' ')

        # Paywall signature check
        paywall_words = ['purchase', 'subscribe', 'access to this article', 'log in', 'buy this article']
        for pw in paywall_words:
            if pw in text_lower:
                return False, f"PAYWALL: '{pw}'"

        # Title keyword match (words > 3 chars)
        title_words = set(title.lower().replace('-', ' ').split())
        significant = [w for w in title_words if len(w) > 3]
        if not significant:
            return True, "NO_SIG_WORDS"
        matched = sum(1 for w in significant if w in text_lower)
        ratio = matched / len(significant)
        if ratio >= 0.3:
            return True, f"MATCH {ratio:.0%} ({matched}/{len(significant)})"
        else:
            return False, f"HONEYPOT {ratio:.0%} ({matched}/{len(significant)})"
    except Exception as e:
        return False, f"PARSE_ERR: {e}"

def download_file(url, dest, label=""):
    """Download with size check."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) < 5000:
            print(f"    [WARN] Too small: {len(data)} bytes | {label}")
            return False
        with open(dest, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"    [ERR] {e} | {label}")
        return False

def try_download_and_validate(url, dest, title, label=""):
    """Download then run both magic-byte and content-aware validation."""
    if download_file(url, dest, label):
        if not is_valid_pdf(dest):
            print(f"    [FAIL] Not a PDF (magic bytes) | {label}")
            safe_remove(dest)
            return False
        ok, msg = content_aware_validate(dest, title)
        if ok:
            size = os.path.getsize(dest)
            print(f"    [PASS] Content validated: {msg} | {size:,} bytes | {label}")
            return True
        else:
            print(f"    [FAIL] Content check: {msg} | {label}")
            safe_remove(dest)
            return False
    return False

def safe_remove(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

# ─── Multi-Tier Download Ladder ──────────────────────────────────────────

def tier1_unpaywall(doi, dest, title):
    """Tier 1: Unpaywall API."""
    if not doi:
        return False
    url = f"https://api.unpaywall.org/v2/{doi}?email=research@example.com"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        best = data.get("best_oa_location") or {}
        pdf_url = best.get("url_for_pdf") or best.get("url")
        if pdf_url:
            print(f"  [T1-Unpaywall] {pdf_url}")
            return try_download_and_validate(pdf_url, dest, title, "Unpaywall")
    except Exception as e:
        print(f"  [T1-Unpaywall] ERR: {e}")
    return False

def tier2_europepmc(pmcid, dest, title):
    """Tier 2: EuropePMC PDF render."""
    if not pmcid:
        return False
    urls = [
        f"https://europepmc.org/articles/{pmcid}?pdf=render",
        f"https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmcid}&blobtype=pdf",
    ]
    for url in urls:
        print(f"  [T2-EPMC] {url}")
        if try_download_and_validate(url, dest, title, "EuropePMC"):
            return True
    return False

def tier3_semanticscholar(doi, dest, title):
    """Tier 3: Semantic Scholar openAccessPdf + PMC discovery."""
    if not doi:
        return False
    ss_url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf,externalIds"
    try:
        req = urllib.request.Request(ss_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        # Try OA PDF
        oa = data.get("openAccessPdf") or {}
        oa_url = oa.get("url")
        if oa_url:
            print(f"  [T3-SS-OA] {oa_url}")
            if try_download_and_validate(oa_url, dest, title, "SS-OA"):
                return True
        # Try discovered PMC
        eids = data.get("externalIds") or {}
        pmcid = eids.get("PubMedCentral")
        if pmcid:
            pmc_str = f"PMC{pmcid}" if not str(pmcid).startswith("PMC") else str(pmcid)
            return tier2_europepmc(pmc_str, dest, title)
    except Exception as e:
        print(f"  [T3-SS] ERR: {e}")
    return False

def tier4_crossref(doi, dest, title):
    """Tier 4: CrossRef links."""
    if not doi:
        return False
    cr_url = f"https://api.crossref.org/works/{doi}"
    try:
        req = urllib.request.Request(cr_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        links = data.get("message", {}).get("link", [])
        for link in links:
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL")
                if pdf_url:
                    print(f"  [T4-CrossRef] {pdf_url}")
                    if try_download_and_validate(pdf_url, dest, title, "CrossRef"):
                        return True
    except Exception as e:
        print(f"  [T4-CrossRef] ERR: {e}")
    return False

def tier5_direct_publisher(doi, dest, title):
    """Tier 5: Direct publisher PDF URL patterns."""
    if not doi:
        return False
    patterns = []
    if "10.4103/" in doi:
        # Indian Journal style (e.g. IJRI) - OA journals
        patterns.append(f"https://journals.lww.com/ijri/{doi.split('/')[-1]}")
    if "10.1097/" in doi:
        # LWW journals
        patterns.append(f"https://journals.lww.com/{doi}")
    if "10.1007/" in doi:
        # Springer
        suffix = doi.replace("10.1007/", "")
        patterns.append(f"https://link.springer.com/content/pdf/{doi}.pdf")
    if "10.30699/" in doi:
        # FHI journal
        patterns.append(f"https://fhi.uswr.ac.ir/article-1-1284-en.pdf")
    if "10.1093/" in doi:
        # OUP journals
        patterns.append(f"https://academic.oup.com/{doi.split('/')[1]}/article-pdf/doi/{doi}")

    for url in patterns:
        print(f"  [T5-Publisher] {url}")
        if try_download_and_validate(url, dest, title, "Publisher"):
            return True
    return False

def tier6_ssrn(ssrn_id, dest, title):
    """Tier 6: SSRN preprint download."""
    if not ssrn_id:
        return False
    urls = [
        f"https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID{ssrn_id}_code.pdf?abstractid={ssrn_id}&mirid=1",
        f"https://ssrn.com/abstract={ssrn_id}",
    ]
    for url in urls:
        print(f"  [T6-SSRN] {url}")
        if try_download_and_validate(url, dest, title, "SSRN"):
            return True
    return False

def tier7_ncbi_pmid(pmid, dest, title):
    """Tier 7: NCBI/PubMed PMC lookup by PMID."""
    if not pmid:
        return False
    # Use NCBI eutils to find PMC
    eutils_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&rettype=xml"
    try:
        req = urllib.request.Request(eutils_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_text = resp.read().decode(errors='ignore')
        # Try to extract PMC ID from the XML
        import re
        pmc_match = re.search(r'PMC\d+', xml_text)
        if pmc_match:
            pmcid = pmc_match.group()
            print(f"  [T7-NCBI] Found PMCID: {pmcid}")
            return tier2_europepmc(pmcid, dest, title)
    except Exception as e:
        print(f"  [T7-NCBI] ERR: {e}")
    return False

# ─── Main Audit Loop ─────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  FULL AUDIT & DOWNLOAD v3.0 (Content-Aware Anti-Honeypot)")
    print("=" * 70)

    audit_results = {}

    for row_info in ROWS:
        row = row_info["row"]
        title = row_info["title"]
        fname = row_info["fname"]
        doi = row_info["doi"]
        pmid = row_info.get("pmid")
        pmcid = row_info.get("pmcid")
        ssrn = row_info.get("ssrn")

        print(f"\n{'─' * 70}")
        print(f"[ROW {row}] {title[:80]}")
        print(f"{'─' * 70}")

        # Row 08: Clinical standard, no PDF expected
        if fname is None:
            print(f"  [SKIP] No PDF expected (Clinical Standard)")
            audit_results[row] = {"status": "N/A", "reason": "Clinical Standard"}
            continue

        dest = os.path.join(PAPERS_DIR, fname)

        # ─── Phase 1: Validate existing PDF ──────────────────────────
        if os.path.exists(dest):
            print(f"  [EXISTS] {fname} ({os.path.getsize(dest):,} bytes)")
            if not is_valid_pdf(dest):
                print(f"  [FAIL] Magic bytes invalid -> DELETING")
                safe_remove(dest)
            else:
                ok, msg = content_aware_validate(dest, title)
                if ok:
                    print(f"  [VALID] Content check PASSED: {msg}")
                    audit_results[row] = {"status": "VALID", "fname": fname, "source": "existing"}
                    continue
                else:
                    print(f"  [HONEYPOT] Content check FAILED: {msg} -> DELETING")
                    safe_remove(dest)

        # ─── Phase 2: Multi-Tier Download ────────────────────────────
        print(f"  [DOWNLOADING] Attempting multi-tier download...")
        downloaded = False

        # Tier 1: Unpaywall
        if not downloaded:
            downloaded = tier1_unpaywall(doi, dest, title)

        # Tier 2: EuropePMC (if PMCID known)
        if not downloaded and pmcid:
            downloaded = tier2_europepmc(pmcid, dest, title)

        # Tier 3: Semantic Scholar (discover OA + PMC)
        if not downloaded:
            time.sleep(0.5)  # rate limit courtesy
            downloaded = tier3_semanticscholar(doi, dest, title)

        # Tier 4: CrossRef
        if not downloaded:
            time.sleep(0.5)
            downloaded = tier4_crossref(doi, dest, title)

        # Tier 5: Direct publisher URL patterns
        if not downloaded:
            downloaded = tier5_direct_publisher(doi, dest, title)

        # Tier 6: SSRN (preprint)
        if not downloaded and ssrn:
            downloaded = tier6_ssrn(ssrn, dest, title)

        # Tier 7: NCBI PMID -> PMC discovery
        if not downloaded and pmid:
            downloaded = tier7_ncbi_pmid(pmid, dest, title)

        if downloaded:
            audit_results[row] = {"status": "DOWNLOADED", "fname": fname, "source": "multi-tier"}
        else:
            audit_results[row] = {"status": "FAILED", "fname": None, "source": None}
            print(f"  [FAILED] All tiers exhausted for Row {row}")

    # ─── Phase 3: Summary Report ─────────────────────────────────────
    print(f"\n{'=' * 70}")
    print("  AUDIT SUMMARY")
    print(f"{'=' * 70}")
    for row, res in audit_results.items():
        status = res['status']
        icon = {"VALID": "OK", "DOWNLOADED": "NEW", "FAILED": "XX", "N/A": "--"}.get(status, "??")
        fname = res.get('fname', 'N/A') or 'N/A'
        source = res.get('source', '') or ''
        safe_fname = fname.encode('ascii', errors='replace').decode('ascii')
        print(f"  [{icon}] Row {row}: {status:12s} | {source:12s} | {safe_fname}")

    # Save results
    results_path = os.path.join(PAPERS_DIR, "audit_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {results_path}")

if __name__ == "__main__":
    main()
