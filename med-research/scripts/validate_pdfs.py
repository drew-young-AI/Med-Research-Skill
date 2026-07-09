import os
import pypdf
import sys

PAPERS_DIR = r'D:\project\Med Deep Research\papers'

def check_title(filepath, title):
    try:
        reader = pypdf.PdfReader(filepath)
        text = ''
        for i in range(min(2, len(reader.pages))):
            text += reader.pages[i].extract_text()
        
        title_words = set(title.lower().replace('-', ' ').split())
        text_lower = text.lower().replace('-', ' ')
        
        # Paywall Signatures
        if 'purchase' in text_lower or 'subscribe' in text_lower or 'access to this article' in text_lower or 'log in' in text_lower:
            return False, 'PAYWALL SIGNATURE'
            
        significant_words = [w for w in title_words if len(w)>3]
        if not significant_words: return True, 'NO SIG WORDS'
        match_count = sum(1 for w in significant_words if w in text_lower)
        ratio = match_count / len(significant_words)
        return ratio >= 0.3, f'Match ratio: {ratio:.2f}'
    except Exception as e:
        return False, f'Error: {e}'

def main():
    print("Content-Aware PDF Validation (Anti-Honeypot)")
    print("=" * 60)
    for f in os.listdir(PAPERS_DIR):
        if f.endswith('.pdf'):
            path = os.path.join(PAPERS_DIR, f)
            title = f.replace('.pdf', '').replace('_', ' ')
            
            # Special case for hardcoded file titles in earlier runs
            if f.startswith('A simple quality control'):
                title = 'A simple quality control tool for assessing integrity of lead equivalent aprons'
            elif f.startswith('Evaluation of lead aprons'):
                title = 'Evaluation of lead aprons and their maintenance and management at our hospital'
                
            valid, msg = check_title(path, title)
            
            # Safe print
            safe_f = f.encode('ascii', errors='replace').decode('ascii')
            print(f'{safe_f}: {valid} ({msg})')
            
            if not valid:
                print(f'  [DELETING] Invalid PDF: {safe_f}')
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"  [ERR] Could not delete {safe_f}: {e}")

if __name__ == '__main__':
    main()
