# Convert STL files from UTF-8 to GBK encoding
# Source directory stays UTF-8, output to stl_gbk subfolder
$srcDir = 'd:\work\CTI\plc\stl'
$dstDir = 'd:\work\CTI\plc\stl_gbk'

if (-not (Test-Path $dstDir)) {
    New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
}

$utf8 = New-Object System.Text.UTF8Encoding($false)
$gbk  = [System.Text.Encoding]::GetEncoding('GBK')

Write-Host "Source dir exists: $(Test-Path $srcDir)"
Write-Host "Source dir: $srcDir"

$files = Get-ChildItem -Path $srcDir -Filter '*.stl'
Write-Host "Files found: $($files.Count)"

$count = 0
foreach ($f in $files) {
    $srcPath = $f.FullName
    $dstPath = Join-Path $dstDir $f.Name
    $text = [System.IO.File]::ReadAllText($srcPath, $utf8)
    [System.IO.File]::WriteAllText($dstPath, $text, $gbk)
    $count++
    Write-Host "Converted: $($f.Name)"
}

Write-Host ""
Write-Host "Total: $count files converted to GBK"
Write-Host "Output directory: $dstDir"
