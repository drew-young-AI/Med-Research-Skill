import re
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import html.parser

class HTMLTextExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
    def handle_data(self, d):
        self.result.append(d)
    def get_text(self):
        return ''.join(self.result)

file_path = r'D:\project\Med Deep Research\papers\Prediction Model for Defects in Lead and Lead-Free Aprons.pdf'
# Read the HTML content (which was wrongly saved as .pdf)
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Try to extract the main text from the body
extractor = HTMLTextExtractor()
extractor.feed(content)
text = extractor.get_text()

# Clean up multiple whitespaces/newlines
text = re.sub(r'\n+', '\n\n', text)
paragraphs = text.split('\n\n')

# Create a true PDF
doc = SimpleDocTemplate(file_path, pagesize=letter)
styles = getSampleStyleSheet()
styleN = styles['Normal']

story = []
story.append(Paragraph('Prediction Model for Defects in Lead and Lead-Free Aprons (Fulltext Extraction)', styles['Title']))
story.append(Spacer(1, 12))

for p in paragraphs:
    p = p.strip()
    if p:
        # reportlab Paragraph needs some xml-escaping
        p = p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(p, styleN))
        story.append(Spacer(1, 6))

doc.build(story)
print(f'Successfully re-generated valid PDF at {file_path}')
