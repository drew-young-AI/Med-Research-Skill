import urllib.request
import urllib.parse
import ssl
import json
import re
import hashlib
import time
import os

ssl._create_default_https_context = ssl._create_unverified_context

PAPERS_DIR = r"D:\project\Med Deep Research\papers"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

def is_valid_pdf(path):
    try:
        with open(path, "rb") as f:
            return f.read(5) == b"%PDF-"
    except Exception:
        return False

def safe_remove(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

def content_check(path, title):
    try:
        import pypdf
        reader = pypdf.PdfReader(path)
        text = "".join((reader.pages[i].extract_text() or "") for i in range(min(2, len(reader.pages))))
        text_lower = text.lower().replace("-", " ")
        paywall_phrases = ["purchase access", "buy this article", "log in to your account", "access to this article is restricted", "purchase this article", "restricted access"]
        for pw in paywall_phrases:
            if pw in text_lower:
                return False, f"PAYWALL:{pw}"
        sig = [w for w in title.lower().replace("-", " ").split() if len(w) > 3]
        if not sig:
            return True, "OK"
        matched = sum(1 for w in sig if w in text_lower)
        ratio = matched / len(sig)
        return ratio >= 0.5, f"{ratio:.0%} ({matched}/{len(sig)})"
    except Exception as e:
        return False, str(e)

def solve_cloudpmc_pow(challenge, difficulty):
    """Solve PMC's CloudPMC-Viewer Proof of Work (POW) Challenge."""
    print(f"    [POW Solver] Solving challenge: {challenge[:25]}... (difficulty: {difficulty})")
    target_prefix = "0" * difficulty
    nonce = 0
    t0 = time.time()
    while True:
        c = challenge + str(nonce)
        h = hashlib.sha256(c.encode("utf-8")).hexdigest()
        if h.startswith(target_prefix):
            duration = time.time() - t0
            print(f"    [POW Solver] Found nonce {nonce} in {duration:.2f}s (hash: {h[:15]}...)")
            return nonce
        nonce += 1

def download_file_with_pow(url, dest, referer=None, extra_headers=None):
    """Download a file, handling potential CloudPMC POW challenge screens."""
    h = dict(HEADERS)
    if referer:
        h["Referer"] = referer
    if extra_headers:
        h.update(extra_headers)
    
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            final_url = resp.geturl()
            headers = resp.info()
        
        # If response content is small HTML and contains POW challenge
        if len(data) < 10000 and b"POW_CHALLENGE" in data:
            html_text = data.decode("utf-8", errors="ignore")
            m_chal = re.search(r'const POW_CHALLENGE\s*=\s*"([^"]+)"', html_text)
            m_diff = re.search(r'const POW_DIFFICULTY\s*=\s*"([^"]+)"', html_text)
            m_cookie = re.search(r'const POW_COOKIE_NAME\s*=\s*"([^"]+)"', html_text)
            
            if m_chal and m_diff and m_cookie:
                challenge = m_chal.group(1)
                difficulty = int(m_diff.group(1))
                cookie_name = m_cookie.group(1)
                
                # Solve POW challenge
                nonce = solve_cloudpmc_pow(challenge, difficulty)
                
                # Inject cookie and retry
                h["Cookie"] = f"{cookie_name}={challenge},{nonce}"
                print(f"    [POW Solver] Retrying with cookie: {cookie_name}")
                
                req_retry = urllib.request.Request(url, headers=h)
                with urllib.request.urlopen(req_retry, timeout=30) as resp_retry:
                    data = resp_retry.read()
                    final_url = resp_retry.geturl()
            else:
                print("    [POW Solver] Failed to parse POW parameters from HTML")
                return False
                
        if len(data) < 5000:
            print(f"    [WARN] Response too small: {len(data)} bytes")
            return False
            
        with open(dest, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"    [ERR] {e}")
        return False

def try_download_and_validate(url, dest, title, label, referer=None, extra_headers=None):
    print(f"  [{label}] {url}")
    if download_file_with_pow(url, dest, referer, extra_headers):
        if not is_valid_pdf(dest):
            print(f"    [FAIL] Not a PDF (magic bytes)")
            if os.path.exists(dest): os.remove(dest)
            return False
        ok, msg = content_check(dest, title)
        if ok:
            print(f"    [PASS] {msg} | {os.path.getsize(dest):,} bytes")
            return True
        else:
            print(f"    [FAIL] Content check: {msg}")
            if os.path.exists(dest): os.remove(dest)
    return False

# ─── Master Matrix: All 8 Rows ───────────────────────────────────────────
ROWS = [
    {
        "row": "01",
        "doi": "10.1007/s12194-026-01086-2",
        "title": "Establishing discard criteria for lead aprons using deep learning-based quantification of defect area on X-ray fluoroscopic video",
        "fname": "Establishing discard criteria for lead aprons using deep learning.pdf",
        "pmid": "42319669",
        "pmcid": None,
        "ssrn": None,
        "rg_id": "392843781",
    },
    {
        "row": "02",
        "doi": "10.1097/HP.0000000000001847",
        "title": "Prediction Model for Defects in Lead and Lead-Free Aprons",
        "fname": "Prediction Model for Defects in Lead and Lead-Free Aprons.pdf",
        "pmid": None,
        "pmcid": None,
        "ssrn": None,
        "rg_id": None,
    },
    {
        "row": "03",
        "doi": "10.4103/ijri.IJRI_374_17",
        "title": "A simple quality control tool for assessing integrity of lead equivalent aprons",
        "fname": "A simple quality control tool for assessing integrity of lead equivalent aprons.pdf",
        "pmid": "30050253",
        "pmcid": "PMC6038217",
        "ssrn": None,
        "rg_id": "326034101",
        "publisher": "medknow",
    },
    {
        "row": "04",
        "doi": "10.1007/s00540-016-2140-2",
        "title": "Evaluation of lead aprons and their maintenance and management at our hospital",
        "fname": "Evaluation of lead aprons and their maintenance and management at our hospital.pdf",
        "pmid": "26842670",
        "pmcid": None,
        "ssrn": None,
        "rg_id": "296831524",
    },
    {
        "row": "05",
        "doi": "10.30699/fhi.v13i7.1284",
        "title": "Development of a Model for Predicting Defects in Radiation Shielding Aprons Using Machine Learning",
        "fname": "Development of a Model for Predicting Defects in Radiation Shielding Aprons Using Machine Learning.pdf",
        "pmid": None,
        "pmcid": None,
        "ssrn": None,
        "rg_id": None,
    },
    {
        "row": "06",
        "doi": "10.2139/ssrn.5373992",
        "title": "Development of a Computational Algorithm for the Automation of Quality Control in Leaded Personal Protective Equipment",
        "fname": "Development of a Computational Algorithm for the Automation of Quality.pdf",
        "pmid": None,
        "pmcid": None,
        "ssrn": "5373992",
        "rg_id": None,
    },
    {
        "row": "07",
        "doi": "10.1093/rpd/ncaf174",
        "title": "Monte Carlo calculations of the radiation absorbed dose to a fetus of a pregnant patient from a dental bitewing X-ray exposure",
        "fname": "Monte Carlo calculations of the radiation absorbed dose to a fetus of a pregnant patient from a dental bitewing X-ray exposure.pdf",
        "pmid": "40354870",
        "pmcid": None,
        "ssrn": None,
        "rg_id": None,
    },
    {
        "row": "08",
        "doi": None,
        "title": "The Lambert and McKeon (Pillay and Stam) Rejection Criteria for Lead Aprons",
        "fname": None,
        "pmid": None,
        "pmcid": None,
        "ssrn": None,
        "rg_id": None,
    },
]

# ─── Tier Implementations ────────────────────────────────────────────────

def tier1_unpaywall(doi, dest, title):
    if not doi:
        return False
    url = f"https://api.unpaywall.org/v2/{doi}?email=research@example.com"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        best = data.get("best_oa_location") or {}
        for key in ["url_for_pdf", "url"]:
            pdf_url = best.get(key)
            if pdf_url:
                print(f"  [T1-Unpaywall] {pdf_url}")
                if try_download_and_validate(pdf_url, dest, title, "Unpaywall"):
                    return True
    except Exception as e:
        print(f"  [T1-Unpaywall] ERR: {e}")
    return False

def tier2_europepmc(pmcid, dest, title):
    if not pmcid:
        return False
    # Attempting direct EuropePMC or CloudPMC PDF endpoint formats
    urls = [
        f"https://europepmc.org/articles/{pmcid}?pdf=render",
        f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/pdf/",
        f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/IJRI-28-258.pdf" if pmcid == "PMC6038217" else None
    ]
    for url in urls:
        if not url:
            continue
        if try_download_and_validate(url, dest, title, f"T2-EPMC-{pmcid}", referer=f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/"):
            return True
        time.sleep(0.3)
    return False

def tier3_semanticscholar(doi, dest, title):
    if not doi:
        return False
    try:
        ss_url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=openAccessPdf,externalIds"
        req = urllib.request.Request(ss_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        oa = data.get("openAccessPdf") or {}
        oa_url = oa.get("url")
        if oa_url:
            print(f"  [T3-SS-OA] {oa_url}")
            if try_download_and_validate(oa_url, dest, title, "SS-OA"):
                return True
        eids = data.get("externalIds") or {}
        pmcid = eids.get("PubMedCentral")
        if pmcid:
            pmc_str = f"PMC{pmcid}" if not str(pmcid).startswith("PMC") else str(pmcid)
            if tier2_europepmc(pmc_str, dest, title):
                return True
    except Exception as e:
        print(f"  [T3-SS] ERR: {e}")
    return False

def tier4_crossref(doi, dest, title):
    if not doi:
        return False
    try:
        cr_url = f"https://api.crossref.org/works/{doi}"
        req = urllib.request.Request(cr_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        links = data.get("message", {}).get("link", [])
        for link in links:
            if link.get("content-type") == "application/pdf":
                pdf_url = link.get("URL")
                if pdf_url:
                    if try_download_and_validate(pdf_url, dest, title, "T4-CrossRef"):
                        return True
    except Exception as e:
        print(f"  [T4-CrossRef] ERR: {e}")
    return False

def tier5_direct_publisher(doi, dest, title):
    if not doi:
        return False
    patterns = []
    if "10.1007/" in doi:
        patterns.append(f"https://link.springer.com/content/pdf/{doi}.pdf")
    if "10.4103/" in doi:
        patterns.append(f"https://www.thieme-connect.de/products/ejournals/pdf/{doi}.pdf")
    if "10.1097/" in doi:
        patterns.append(f"https://journals.lww.com/{doi}")
    if "10.1093/" in doi:
        patterns.append(f"https://academic.oup.com/rpd/article-pdf/doi/{doi}")
    for url in patterns:
        if try_download_and_validate(url, dest, title, "T5-Publisher"):
            return True
        time.sleep(0.3)
    return False

def tier6_ssrn(ssrn_id, dest, title):
    if not ssrn_id:
        return False
    urls = [
        f"https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID{ssrn_id}_code.pdf?abstractid={ssrn_id}&mirid=1",
    ]
    for url in urls:
        if try_download_and_validate(url, dest, title, "T6-SSRN"):
            return True
    return False

def tier7_ncbi_pmid(pmid, dest, title):
    if not pmid:
        return False
    try:
        url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={pmid}&format=json&tool=medresearch&email=demo@example.com"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        for rec in data.get("records", []):
            pmcid = rec.get("pmcid")
            if pmcid and rec.get("status") != "error":
                print(f"  [T7-NCBI] Discovered PMCID: {pmcid}")
                if tier2_europepmc(pmcid, dest, title):
                    return True
    except Exception as e:
        print(f"  [T7-NCBI] ERR: {e}")
    return False

def tier8_openalex(doi, dest, title):
    if not doi:
        return False
    try:
        url = f"https://api.openalex.org/works/doi:{doi}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        locations = data.get("locations") or []
        for loc in locations:
            if loc.get("is_oa") and loc.get("pdf_url"):
                pdf_url = loc["pdf_url"]
                if try_download_and_validate(pdf_url, dest, title, "T8-OpenAlex"):
                    return True
                time.sleep(0.3)
    except Exception as e:
        print(f"  [T8-OpenAlex] ERR: {e}")
    return False

def tier9_core(doi, dest, title):
    if not doi:
        return False
    try:
        enc_doi = urllib.parse.quote(doi, safe="")
        url = f"https://api.core.ac.uk/v3/search/works?q=doi:{enc_doi}&limit=3"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        for result in data.get("results", []):
            dl_url = result.get("downloadUrl") or result.get("fullTextUrl")
            src_urls = result.get("sourceFulltextUrls") or []
            candidates = ([dl_url] if dl_url else []) + src_urls
            for cu in candidates:
                if cu and cu.startswith("http"):
                    if try_download_and_validate(cu, dest, title, "T9-CORE"):
                        return True
                    time.sleep(0.3)
    except Exception as e:
        print(f"  [T9-CORE] ERR: {e}")
    return False

def tier10_researchgate_public(rg_id, dest, title):
    if not rg_id:
        return False
    try:
        probe_url = f"https://www.researchgate.net/publication/{rg_id}"
        rg_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }
        req = urllib.request.Request(probe_url, headers=rg_headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read(100000).decode("utf-8", errors="ignore")

        has_request_form = "Request full-text" in html or "request-full-text" in html
        has_public_dl = (
            "fulltext/downloads" in html
            or "Download full-text PDF" in html
            or '"pdfUrl"' in html
            or "publication/" in html
        )

        if not has_public_dl:
            print(f"  [T10-RG] No public PDF found for RG {rg_id}, skipping")
            return False

        # Extract direct PDF URLs
        pdf_urls = re.findall(r'"pdfUrl"\s*:\s*"([^"]+)"', html)
        pdf_urls += re.findall(r'href=["\']([^"\']*fulltext/downloads[^"\']*)["\']', html)
        pdf_urls += re.findall(r'"(https?://[^"]+publication/[^"]+/links/[^"]+)"', html)

        for pu in pdf_urls[:3]:
            full_url = pu if pu.startswith("http") else "https://www.researchgate.net" + pu
            # Note: RG usually returns 403 on urllib but we try anyway
            if try_download_and_validate(full_url, dest, title, "T10-RG", extra_headers=rg_headers):
                return True
            time.sleep(0.5)
    except Exception as e:
        print(f"  [T10-RG] ERR: {e}")
    return False

def tier11_medknow_oa(doi, dest, title, row_info):
    publisher = row_info.get("publisher")
    if publisher != "medknow":
        return False
    pmid = row_info.get("pmid")
    candidates = [
        "https://www.ijri.org/text.asp?2018/28/3/347/241461",
    ]
    if pmid:
        candidates += [
            f"https://journals.lww.com/_layouts/15/oaks.journals/downloadpdf.aspx?an={pmid}",
        ]
    candidates += [
        "https://www.ijri.org/downloadpdf.asp?issn=0971-3026;year=2018;volume=28;issue=3;spage=347;epage=355;aulast=Jafari",
        "https://article.medknow.com/downloadpdf.asp?issn=0971-3026;year=2018;volume=28;issue=3;spage=347;epage=355;aulast=Jafari",
    ]
    for url in candidates:
        if try_download_and_validate(url, dest, title, "T11-Medknow", {"Referer": "https://www.ijri.org/"}):
            return True
        time.sleep(0.5)
    return False

def tier12_doi_landing_scrape(doi, dest, title):
    if not doi:
        return False
    try:
        doi_url = f"https://doi.org/{doi}"
        req = urllib.request.Request(doi_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read(200000).decode("utf-8", errors="ignore")
            final_url = resp.geturl()
        print(f"  [T12-Scrape] Landed: {final_url}")
        base = "/".join(final_url.split("/")[:3])

        candidates = []
        candidates += re.findall(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', html, re.IGNORECASE)
        candidates += re.findall(r'"pdf[Uu]rl"\s*:\s*"([^"]+)"', html)
        candidates += re.findall(r'"downloadUrl"\s*:\s*"([^"]+)"', html)
        candidates += re.findall(r'(https?://[^\s"\'<>]+\.pdf)', html)

        seen = set()
        for c in candidates[:10]:
            full = c if c.startswith("http") else base + "/" + c.lstrip("/")
            if full in seen:
                continue
            seen.add(full)
            if try_download_and_validate(full, dest, title, "T12-Scrape"):
                return True
            time.sleep(0.3)
    except Exception as e:
        print(f"  [T12-Scrape] ERR: {e}")
    return False

def tier13_duckduckgo_search(title, dest):
    """
    Tier 13: Search DuckDuckGo HTML for public PDF download links.
    Crawls search results to discover alternative unpaywalled hosting.
    """
    print(f"  [T13-DDG-Search] Searching DuckDuckGo...")
    query = f'"{title}" pdf'
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        encoded_links = re.findall(r'uddg=([^&"\'<>]+)', html)
        pdf_urls = []
        for el in encoded_links:
            dec = urllib.parse.unquote(el)
            if dec.startswith("http"):
                if ".pdf" in dec.lower() or "pdf" in dec.lower():
                    pdf_urls.append(dec)
        
        href_links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)
        for hl in href_links:
            if "duckduckgo.com" not in hl:
                if ".pdf" in hl.lower() or "pdf" in hl.lower():
                    pdf_urls.append(hl)
                    
        seen = set()
        dedup = []
        for u in pdf_urls:
            if u not in seen:
                seen.add(u)
                dedup.append(u)
                
        print(f"  [T13-DDG-Search] Discovered {len(dedup)} candidate search result links.")
        for u in dedup[:5]:
            if try_download_and_validate(u, dest, title, "T13-DDG-Search"):
                return True
            time.sleep(0.5)
    except Exception as e:
        print(f"  [T13-DDG-Search] ERR: {e}")
    return False

def tier14_google_scholar(title, dest):
    """
    Tier 14: Search Google Scholar HTML for public PDF and ResearchGate links.
    """
    print(f"  [T14-Scholar] Searching Google Scholar...")
    url = "https://scholar.google.com/scholar?q=" + urllib.parse.quote(title)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        if "captcha" in html.lower() or "not a robot" in html.lower() or "/recaptcha/" in html:
            print("    [T14-Scholar] Blocked by CAPTCHA.")
            return False
            
        links = re.findall(r'href=["\'](https?://[^"\']+\.pdf[^"\']*)["\']', html)
        rg_links = re.findall(r'href=["\'](https?://www\.researchgate\.net/publication/[^"\']+)["\']', html)
        
        candidates = list(set(links + rg_links))
        print(f"    [T14-Scholar] Discovered {len(candidates)} candidates.")
        for u in candidates[:5]:
            if "researchgate.net" in u:
                rg_id_match = re.search(r'publication/(\d+)', u)
                if rg_id_match:
                    if tier10_researchgate_public(rg_id_match.group(1), dest, title):
                        return True
            else:
                if try_download_and_validate(u, dest, title, "T14-Scholar"):
                    return True
            time.sleep(0.5)
    except Exception as e:
        print(f"    [T14-Scholar] ERR: {e}")
    return False

def tier15_proquest(title, dest):
    """
    Tier 15: Search ProQuest open-access documents via DuckDuckGo site query.
    Converts docview URLs to direct open-access guest viewer URLs.
    """
    print(f"  [T15-ProQuest] Searching ProQuest via DDG...")
    query = f'site:proquest.com "{title}"'
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        encoded_links = re.findall(r'uddg=([^&"\'<>]+)', html)
        
        pq_ids = []
        for el in encoded_links:
            dec = urllib.parse.unquote(el)
            if "proquest.com" in dec:
                m = re.search(r'(docview|openview)/(\d+)', dec)
                if m:
                    pq_ids.append(m.group(2))
                    
        pq_ids = list(set(pq_ids))
        print(f"    [T15-ProQuest] Discovered {len(pq_ids)} doc IDs.")
        for doc_id in pq_ids[:3]:
            openview_url = f"https://www.proquest.com/openview/{doc_id}/1?pq-origsite=gscholar&cbl=18750"
            if try_download_and_validate(openview_url, dest, title, "T15-ProQuest"):
                return True
            time.sleep(0.5)
    except Exception as e:
        print(f"    [T15-ProQuest] ERR: {e}")
    return False

# ─── Main Audit Loop ─────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  FULL AUDIT & DOWNLOAD v5.0  (15-Tier Ladder + CloudPMC POW Solver)")
    print("=" * 70)

    audit_results = {}

    for row_info in ROWS:
        row = row_info["row"]
        title = row_info["title"]
        fname = row_info["fname"]
        doi = row_info.get("doi")
        pmid = row_info.get("pmid")
        pmcid = row_info.get("pmcid")
        ssrn = row_info.get("ssrn")
        rg_id = row_info.get("rg_id")

        print(f"\n{'─' * 70}")
        print(f"[ROW {row}] {title[:75]}")
        print(f"{'─' * 70}")

        if fname is None:
            print(f"  [SKIP] Clinical Standard")
            audit_results[row] = {"status": "N/A"}
            continue

        dest = os.path.join(PAPERS_DIR, fname)

        # Phase 1: Validate existing
        if os.path.exists(dest):
            print(f"  [EXISTS] {os.path.getsize(dest):,} bytes")
            if is_valid_pdf(dest):
                ok, msg = content_check(dest, title)
                if ok:
                    print(f"  [VALID] {msg}")
                    audit_results[row] = {"status": "VALID", "fname": fname}
                    continue
                else:
                    print(f"  [HONEYPOT] {msg} -> DELETING")
                    safe_remove(dest)
            else:
                print(f"  [INVALID] Bad magic bytes -> DELETING")
                safe_remove(dest)

        # Phase 2: 15-Tier Download  (ordered: easiest → hardest)
        # ── Tier  1- 4: Pure REST APIs (zero scraping, highest success rate)
        # ── Tier  5- 6: Preprint / DOI-resolved direct links
        # ── Tier  7- 9: Publisher-specific open-access portals
        # ── Tier 10-12: HTML scraping (Cloudflare / landing pages)
        # ── Tier 13-15: Search-engine discovery (CAPTCHA / multi-hop)
        print(f"  [DOWNLOAD] Starting 15-tier ladder...")
        downloaded = False

        tiers = [
            # ── 難度 ★☆☆☆☆ ── Pure REST APIs ──────────────────────────────
            ("T1",  lambda: tier1_unpaywall(doi, dest, title)),          # Unpaywall JSON API
            ("T2",  lambda: tier8_openalex(doi, dest, title)),           # OpenAlex JSON API
            ("T3",  lambda: tier9_core(doi, dest, title)),               # CORE.ac.uk REST API
            ("T4",  lambda: tier2_europepmc(pmcid, dest, title)),        # EuropePMC REST API
            # ── 難度 ★★☆☆☆ ── Preprint / Semantic APIs ───────────────────
            ("T5",  lambda: tier3_semanticscholar(doi, dest, title)),    # S2 Graph API
            ("T6",  lambda: tier4_crossref(doi, dest, title)),           # CrossRef links API
            ("T7",  lambda: tier6_ssrn(ssrn, dest, title)),              # SSRN preprint direct
            # ── 難度 ★★★☆☆ ── Publisher OA / NCBI (with POW solver) ──────
            ("T8",  lambda: tier7_ncbi_pmid(pmid, dest, title)),         # NCBI PMC + POW solver
            ("T9",  lambda: tier11_medknow_oa(doi, dest, title, row_info)),  # Medknow OA portal
            ("T10", lambda: tier5_direct_publisher(doi, dest, title)),   # DOI-resolved publisher
            # ── 難度 ★★★★☆ ── HTML / Cloudflare Scraping ─────────────────
            ("T11", lambda: tier10_researchgate_public(rg_id, dest, title)),  # RG public PDF scrape
            ("T12", lambda: tier12_doi_landing_scrape(doi, dest, title)),     # DOI landing HTML mine
            # ── 難度 ★★★★★ ── Search-Engine Discovery (CAPTCHA / multi-hop)
            ("T13", lambda: tier13_duckduckgo_search(title, dest)),      # DuckDuckGo title search
            ("T14", lambda: tier15_proquest(title, dest)),               # ProQuest openview DDG
            ("T15", lambda: tier14_google_scholar(title, dest)),         # Google Scholar (CAPTCHA risk)
        ]

        for tier_name, tier_fn in tiers:
            try:
                if tier_fn():
                    downloaded = True
                    audit_results[row] = {"status": "DOWNLOADED", "fname": fname, "tier": tier_name}
                    break
            except Exception as e:
                print(f"  [{tier_name}] Unhandled ERR: {e}")
            time.sleep(0.2)

        if not downloaded:
            print(f"  [FAILED] All 15 tiers exhausted")
            audit_results[row] = {"status": "FAILED"}

    # Summary
    print(f"\n{'=' * 70}")
    print("  AUDIT SUMMARY v5.0")
    print(f"{'=' * 70}")
    icons = {"VALID": "OK", "DOWNLOADED": "NEW", "FAILED": "XX", "N/A": "--"}
    for row, res in sorted(audit_results.items()):
        icon = icons.get(res["status"], "??")
        fname = res.get("fname", "N/A") or "N/A"
        tier = res.get("tier", "")
        safe_f = fname.encode("ascii", errors="replace").decode("ascii")
        print(f"  [{icon}] Row {row}: {res['status']:10s} {tier:4s} | {safe_f}")

    with open(os.path.join(PAPERS_DIR, "audit_v5_results.json"), "w", encoding="utf-8") as f:
        json.dump(audit_results, f, ensure_ascii=False, indent=2)
    print(f"\nDone.")

if __name__ == "__main__":
    main()
