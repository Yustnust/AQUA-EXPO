$src = 'd:\work\CTI\docs\commissioning\STEP7符号表_8套通用版_v1.0_V25_3列.csv'
$dst = 'd:\work\CTI\docs\commissioning\STEP7符号表_V25_GBK.csv'
$utf8 = [System.Text.Encoding]::UTF8
$gbk = [System.Text.Encoding]::GetEncoding('GBK')
$content = [System.IO.File]::ReadAllText($src, $utf8)
[System.IO.File]::WriteAllText($dst, $content, $gbk)
Write-Host "Done: $dst"
