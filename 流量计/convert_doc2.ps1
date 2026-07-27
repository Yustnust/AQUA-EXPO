# 用UTF-8 BOM编码保存
$OutputEncoding = [System.Text.Encoding]::UTF8
$word = New-Object -ComObject Word.Application
$word.Visible = $false

# 获取目录下所有doc/docx文件
$files = Get-ChildItem -Path "d:\work\CTI\流量计" -Include "*.doc","*.docx" -Recurse

foreach ($file in $files) {
    Write-Output "处理: $($file.Name)"
    try {
        $doc = $word.Documents.Open($file.FullName)
        $txtFile = $file.FullName -replace '\.(doc|docx)$', '.txt'
        $doc.Content.Text | Out-File -FilePath $txtFile -Encoding UTF8
        $doc.Close()
        Write-Output "  -> 已转换: $txtFile"
    } catch {
        Write-Output "  -> 转换失败: $_"
    }
}

$word.Quit()
Write-Output "全部完成"
