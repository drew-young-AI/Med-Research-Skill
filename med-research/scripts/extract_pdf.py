import re

file_path = r'D:\project\Med Deep Research\papers\Prediction Model for Defects in Lead and Lead-Free Aprons.pdf'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Look for pdf links in the HTML
pdf_links = re.findall(r'href=[\'\"]([^\'\"]+\.pdf)[\'\"]', content)
pdf_links_2 = re.findall(r'href=[\'\"]([^\'\"]+)[\'\"][^>]*>PDF', content, re.IGNORECASE)
print('Direct PDF links:', pdf_links)
print('Links with PDF text:', pdf_links_2)
