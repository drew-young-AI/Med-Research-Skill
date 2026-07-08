import os

papers_dir = r'D:\project\Med Deep Research\papers'
target_pdfs = [
    'Development of a Model for Predicting Defects in Radiation Shielding Aprons Using Machine Learning.pdf',
    'Evaluation of lead aprons and their maintenance and management at our hospital.pdf',
    'Monte Carlo calculations of the radiation absorbed dose to a fetus of a pregnant patient from a dental bitewing X-ray exposure.pdf',
    'Prediction Model for Defects in Lead and Lead-Free Aprons.pdf',
]
print('PDF validity check:')
for fname in target_pdfs:
    path = os.path.join(papers_dir, fname)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            header = f.read(5)
        valid = header == b'%PDF-'
        size = os.path.getsize(path)
        status = 'VALID' if valid else 'INVALID'
        print(f'  [{status}] {fname[:65]} ({size:,} bytes)')
    else:
        print(f'  [MISSING] {fname[:65]}')
