import PyPDF2, os, sys

pdfs = [
    r'D:\work\CTI\注射泵\泵阀一体 MODBUS协议_V1.7.pdf',
    r'D:\work\CTI\注射泵\SY11全陶瓷(ASCII)_V1.8.pdf',
    r'D:\work\CTI\注射泵\SY11全陶瓷_V1.5.pdf',
]

for p in pdfs:
    print('='*60)
    print(os.path.basename(p))
    print('='*60)
    try:
        with open(p,'rb') as f:
            r = PyPDF2.PdfReader(f)
            print(f'pages: {len(r.pages)}')
            for i,page in enumerate(r.pages[:15]):
                txt = page.extract_text()
                if txt:
                    print(f'--- page {i+1} ---')
                    print(txt[:3000])
    except Exception as e:
        print('ERROR:', e)
