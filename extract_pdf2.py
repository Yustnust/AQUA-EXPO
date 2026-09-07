import fitz

pdf_path = r'D:\work\CTI\注射泵\SY-03BM全陶瓷磁编注射泵(ASCII)_V1.0.pdf'
doc = fitz.open(pdf_path)
for i, page in enumerate(doc):
    text = page.get_text()
    if text:
        print(f'=== Page {i+1} ===')
        print(text)
