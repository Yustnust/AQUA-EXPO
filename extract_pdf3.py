import fitz

pdf_path = r'D:\work\CTI\注射泵\泵阀一体 MODBUS协议_V1.7.pdf'
doc = fitz.open(pdf_path)
for i, page in enumerate(doc):
    text = page.get_text()
    if text:
        print(f'=== Page {i+1} ===')
        print(text)
