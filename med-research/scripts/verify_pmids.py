import urllib.request, json, ssl, time, re
ssl._create_default_https_context = ssl._create_unverified_context

# Row 01 PMID=42319669 - check if it's in PMC
url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=42319669&format=json&tool=medresearch&email=demo@example.com"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
print("Row 01 PMID=42319669 PMC lookup:")
print(json.dumps(data.get("records", []), indent=2))

time.sleep(1)

# Row 03 efetch to get the correct article details
url2 = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30050253&rettype=xml&retmode=xml"
req2 = urllib.request.Request(url2, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req2, timeout=15) as resp:
    xml = resp.read().decode(errors="ignore")

pmcs = re.findall(r"PMC\d+", xml)
title_match = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", xml)
doi_match = re.search(r'EIdType="doi"[^>]*>(.*?)</ELocationID>', xml)
journal_match = re.search(r"<Title>(.*?)</Title>", xml)
print("\nRow 03 PMID=30050253 efetch:")
print(f"  Title: {title_match.group(1) if title_match else 'N/A'}")
print(f"  Journal: {journal_match.group(1) if journal_match else 'N/A'}")
print(f"  DOI: {doi_match.group(1) if doi_match else 'N/A'}")
print(f"  PMC IDs found: {list(set(pmcs))}")

time.sleep(1)

# Also check Row 03 correct DOI - maybe PMID 30050253 is NOT our paper
# Our paper DOI is 10.4103/ijri.IJRI_374_17
# Let's search by exact DOI
url3 = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=10.4103/ijri.IJRI_374_17[doi]&retmode=json"
req3 = urllib.request.Request(url3, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req3, timeout=15) as resp:
    data3 = json.loads(resp.read().decode())
ids = data3.get("esearchresult", {}).get("idlist", [])
print(f"\nRow 03 DOI esearch PMIDs: {ids}")

# Fetch those IDs' details
for pmid in ids[:2]:
    time.sleep(0.5)
    url4 = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&rettype=xml&retmode=xml"
    req4 = urllib.request.Request(url4, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req4, timeout=15) as resp:
        xml4 = resp.read().decode(errors="ignore")
    pmcs4 = re.findall(r"PMC\d+", xml4)
    title4 = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", xml4)
    print(f"  PMID {pmid}: title={title4.group(1)[:80] if title4 else 'N/A'}, PMCs={list(set(pmcs4))}")
