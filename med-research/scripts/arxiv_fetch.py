import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os

titles = [
    'Establishing discard criteria for lead aprons using deep learning-based quantification of defect area on X-ray fluoroscopic video',
    'Prediction Model for Defects in Lead and Lead-Free Aprons',
    'Evaluation of lead aprons and their maintenance and management at our hospital',
    'Occupational dose attenuation and dosimetric performance of autonomous radiation protection systems in fluoroscopy: a scoping review with implications for the role of conventional lead aprons'
]

papers_dir = r'D:\project\Med Deep Research\papers'
if not os.path.exists(papers_dir):
    os.makedirs(papers_dir)

for title in titles:
    query = urllib.parse.quote(f'ti:"{title}"')
    url = f'http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=1'
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entry = root.find('atom:entry', ns)
            if entry is not None:
                pdf_link = None
                for link in entry.findall('atom:link', ns):
                    if link.attrib.get('title') == 'pdf':
                        pdf_link = link.attrib.get('href')
                        break
                
                if pdf_link:
                    print(f'Found arxiv PDF for {title}: {pdf_link}')
                    safe_title = title.replace(':', '').replace('/', '-')
                    out_path = os.path.join(papers_dir, f'{safe_title}.pdf')
                    urllib.request.urlretrieve(pdf_link + '.pdf', out_path)
                    print(f'SUCCESS Downloaded: {out_path}')
                else:
                    print(f'No PDF link in arxiv entry for {title}')
            else:
                print(f'No arxiv preprint found for {title}')
    except Exception as e:
        print(f'Error querying arxiv for {title}: {e}')
