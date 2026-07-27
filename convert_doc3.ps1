$word = New-Object -ComObject Word.Application
$word.Visible = $false

$dir = [System.IO.Path]::GetFullPath("d:\work\CTI\" + [char]0x6D41 + [char]0x91CF + [char]0x8BA1)
Write-Output "Directory: $dir"

$files = Get-ChildItem -Path $dir -Filter "*.doc*" -Recurse

foreach ($file in $files) {
    Write-Output "Processing: $($file.Name)"
    try {
        $doc = $word.Documents.Open($file.FullName)
        $txtFile = [System.IO.Path]::ChangeExtension($file.FullName, ".txt")
        $doc.Content.Text | Out-File -FilePath $txtFile -Encoding UTF8
        $doc.Close()
        Write-Output "  -> OK: $txtFile"
    } catch {
        Write-Output "  -> FAIL: $_"
    }
}

$word.Quit()
Write-Output "All done"
