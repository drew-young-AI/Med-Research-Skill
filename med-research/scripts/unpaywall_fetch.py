import urllib.request
import json
import os
import urllib.error
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

dois = {
    '10.1007/s12194-026-01086-2': 'Establishing discard criteria for lead aprons using deep learning-based quantification of defect area on X-ray fluoroscopic video',
    '10.1097/HP.0000000000001847': 'Prediction Model for Defects in Lead and Lead-Free Aprons',
    '10.1007/s00540-016-2140-2': 'Evaluation of lead aprons and their maintenance and management at our hospital',
    '10.1088/1361-6498/ae7122': 'Occupational dose attenuation and dosimetric performance of autonomous radiation protection systems in fluoroscopy: a scoping review with implications for the role of conventional lead aprons'
}

papers_dir = r'D:\project\Med Deep Research\papers'
if not os.path.exists(papers_dir):
    os.makedirs(papers_dir)

for doi, title in dois.items():
    print(f'Checking DOI: {doi}')
    url = f'https://api.unpaywall.org/v2/{doi}?email=bot@example.com'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data.get('is_oa'):
                pdf_url = data['best_oa_location'].get('url_for_pdf')
                if pdf_url:
                    print(f'Found OA PDF: {pdf_url}')
                    safe_title = title.replace(':', '').replace('/', '-')
                    out_path = os.path.join(papers_dir, f'{safe_title}.pdf')
                    try:
                        req_pdf = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req_pdf) as response_pdf, open(out_path, 'wb') as out_file:
                            out_file.write(response_pdf.read())
                        print(f'SUCCESS Downloaded: {out_path}')
                    except Exception as e:
                        print(f'Failed to download {pdf_url}: {e}')
                else:
                    print('OA but no PDF URL found.')
            else:
                print('Not Open Access (is_oa=False)')
    except urllib.error.HTTPError as e:
        print(f'HTTP Error: {e.code}')
    except Exception as e:
        print(f'Error: {e}')
