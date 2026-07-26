# Create JIRA bug task - reads JSON body from file
# No Chinese in this script to avoid PS5.1 encoding issues

$email = 'yusongt@gmail.com'
$token = 'ATATT3xFfGF0HF4yTIrmyVArQm2HtPKXXH8Zgj_ko7DKcHA5zHwps2IjK7ROdgjfHCGavpTc-sKfER21Hwonsty7Xm3DtUqvJS2OBIoBLUZSYL82-Aab4EDXs-UExx25OExoopRiP48vg3vstgcJnm5oKsnjyG1eLVjZ2N2jdsSp22_1HECuj1E=F1481C58'
$base = 'https://yusongtao.atlassian.net'
$jsonFile = 'd:\work\CTI\jira_bug_body.json'

$pair = "$email`:$token"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$b64 = [System.Convert]::ToBase64String($bytes)
$headers = @{
    Authorization = "Basic $b64"
    Accept = 'application/json'
}

# Read JSON body as UTF-8
$utf8 = New-Object System.Text.UTF8Encoding($false)
$body = [System.IO.File]::ReadAllText($jsonFile, $utf8)

Write-Host "=== Creating bug task ==="
try {
    $resp = Invoke-RestMethod -Uri "$base/rest/api/3/issue" -Headers $headers -Method Post -Body $body -ContentType 'application/json'
    Write-Host "SUCCESS!"
    Write-Host "Key: $($resp.key)"
    Write-Host "ID: $($resp.id)"
    Write-Host "URL: $base/browse/$($resp.key)"
} catch {
    Write-Host "FAILED: $($_.Exception.Message)"
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $errBody = $reader.ReadToEnd()
    Write-Host "Error body: $errBody"
}
