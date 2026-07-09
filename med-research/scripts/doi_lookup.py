import urllib.request, json, ssl, time
ssl._create_default_https_context = ssl._create_unverified_context

dois = {
    "03": "10.4103/ijri.IJRI_374_17",
    "04": "10.1007/s00540-016-2140-2",
}

for row, doi in dois.items():
    print(f"=== Row {row} (DOI: {doi}) ===")
    
    # Method 1: NCBI ID Converter by DOI
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={doi}&format=json&tool=medresearch&email=demo@example.com"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        print("NCBI ID Converter:")
        for rec in data.get("records", []):
            pmid = rec.get("pmid", "N/A")
            pmcid = rec.get("pmcid", "N/A")
            rdoi = rec.get("doi", "N/A")
            status = rec.get("status", "ok")
            print(f"  PMID={pmid}  PMCID={pmcid}  DOI={rdoi}  status={status}")
    except Exception as e:
        print(f"  ERR: {e}")
    
    time.sleep(1)
    
    # Method 2: PubMed ESearch by DOI
    esearch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={doi}[doi]&retmode=json"
    try:
        req = urllib.request.Request(esearch_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        ids = data.get("esearchresult", {}).get("idlist", [])
        print(f"PubMed ESearch: PMIDs = {ids}")
    except Exception as e:
        print(f"  ERR: {e}")
    
    print()
    time.sleep(1)

# Also check CrossRef for Row 03 to get alternative full-text links
print("=== Row 03: CrossRef metadata ===")
cr_url = "https://api.crossref.org/works/10.4103/ijri.IJRI_374_17"
try:
    req = urllib.request.Request(cr_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    msg = data.get("message", {})
    links = msg.get("link", [])
    print(f"  Title: {msg.get('title', ['N/A'])[0]}")
    print(f"  Container: {msg.get('container-title', ['N/A'])[0]}")
    print(f"  License: {[l.get('URL') for l in msg.get('license', [])]}")
    for lnk in links:
        print(f"  Link: {lnk.get('URL')} ({lnk.get('content-type')})")
except Exception as e:
    print(f"  ERR: {e}")

print()

# CrossRef for Row 04
print("=== Row 04: CrossRef metadata ===")
cr_url = "https://api.crossref.org/works/10.1007/s00540-016-2140-2"
try:
    req = urllib.request.Request(cr_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    msg = data.get("message", {})
    links = msg.get("link", [])
    print(f"  Title: {msg.get('title', ['N/A'])[0]}")
    print(f"  Container: {msg.get('container-title', ['N/A'])[0]}")
    print(f"  License: {[l.get('URL') for l in msg.get('license', [])]}")
    for lnk in links:
        print(f"  Link: {lnk.get('URL')} ({lnk.get('content-type')})")
except Exception as e:
    print(f"  ERR: {e}")
