import PyPDF2, os

p = r'D:\work\CTI\注射泵\泵阀一体 MODBUS协议_V1.7.pdf'
print('FILE:', p)
print('EXISTS:', os.path.exists(p))
print('SIZE:', os.path.getsize(p) if os.path.exists(p) else 0)

with open(p,'rb') as f:
    r = PyPDF2.PdfReader(f)
    print('PAGES:', len(r.pages))
    for i,page in enumerate(r.pages):
        txt = page.extract_text()
        print(f'--- PAGE {i+1} ---')
        if txt:
            print(txt)
        else:
            print('[NO TEXT]')
