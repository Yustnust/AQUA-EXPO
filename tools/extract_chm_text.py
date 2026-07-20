"""
批量提取McgsPro官方文档(UTF-8 HTML)正文内容
输出:/tmp/chm_text/ 下按目录结构生成.txt文件
"""
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

SRC = '/tmp/utf8_out'
DST = '/tmp/chm_text'

os.makedirs(DST, exist_ok=True)

def html_to_text(html_path):
    """HTML转纯文本,保留标题层级"""
    try:
        with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        # 移除style/script
        for tag in soup(['style', 'script']):
            tag.decompose()
        # 获取标题
        title = soup.title.string if soup.title else ''
        # 获取正文
        body = soup.body if soup.body else soup
        # 转文本,保留换行
        text = body.get_text(separator='\n', strip=True)
        # 清理多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        return f"=== {title} ===\n\n{text}"
    except Exception as e:
        return f"=== 错误: {e} ==="

# 遍历所有.htm文件
count = 0
for root, dirs, files in os.walk(SRC):
    for fname in files:
        if fname.endswith('.htm'):
            src_path = os.path.join(root, fname)
            rel_path = os.path.relpath(src_path, SRC)
            # 改扩展名为.txt
            rel_path_txt = os.path.splitext(rel_path)[0] + '.txt'
            dst_path = os.path.join(DST, rel_path_txt)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            text = html_to_text(src_path)
            with open(dst_path, 'w', encoding='utf-8') as f:
                f.write(text)
            count += 1

print(f"已转换 {count} 个HTML文件")
print(f"输出目录: {DST}")

# 列出关键文件大小
key_files = [
    '脚本程序/基本语句.txt',
    '脚本程序/语言要素.txt',
    '脚本函数/运行环境操作函数.txt',
    '脚本函数/数据对象操作函数.txt',
    '脚本函数/权限管理操作函数.txt',
    '设备窗口/设备组态.txt',
    '实时数据/添加数据对象.txt',
    '用户窗口/创建窗口.txt',
    '快速入门/制作组态工程.txt',
    '快速入门/下载组态工程.txt',
]
print("\n关键文件大小:")
for kf in key_files:
    p = os.path.join(DST, kf)
    if os.path.exists(p):
        size = os.path.getsize(p)
        print(f"  {kf}: {size} bytes")
