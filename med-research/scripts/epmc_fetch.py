import urllib.request
import urllib.parse
import json
import os

query = urllib.parse.quote('("lead apron" OR "radiation protection") AND "quality control" AND (OPEN_ACCESS:y)')
url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={query}&format=json&resultType=core'

papers_dir = r'D:\project\Med Deep Research\papers'
if not os.path.exists(papers_dir):
    os.makedirs(papers_dir)

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        results = data.get('resultList', {}).get('result', [])
        
        downloaded = False
        for res in results:
            title = res.get('title')
            pmcid = res.get('pmcid')
            doi = res.get('doi')
            if pmcid:
                pdf_url = f'https://europepmc.org/articles/{pmcid}?pdf=render'
                safe_title = title.replace(':', '').replace('/', '-').replace('"', '').replace('?', '')
                out_path = os.path.join(papers_dir, f'{safe_title}.pdf')
                
                print(f'Attempting to download: {title}')
                print(f'DOI: {doi}, PMCID: {pmcid}')
                print(f'URL: {pdf_url}')
                
                try:
                    pdf_req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(pdf_req) as pdf_res:
                        with open(out_path, 'wb') as f:
                            f.write(pdf_res.read())
                    print(f'SUCCESS Downloaded: {out_path}')
                    
                    # Save metadata for agent to read
                    meta_path = os.path.join(papers_dir, 'latest_download_meta.json')
                    with open(meta_path, 'w', encoding='utf-8') as mf:
                        json.dump({'title': title, 'doi': doi, 'pmcid': pmcid, 'path': out_path}, mf)
                    
                    downloaded = True
                    break
                except Exception as e:
                    print(f'Failed to download PDF: {e}')
        
        if not downloaded:
            print('No PDFs could be downloaded.')
            
except Exception as e:
    print(f'Error: {e}')
