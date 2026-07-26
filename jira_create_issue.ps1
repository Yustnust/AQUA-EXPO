# Reusable JIRA issue creation script
# Usage: powershell -ExecutionPolicy Bypass -File jira_create_issue.ps1 -JsonFile <path> [-EpicKey AQEX-1]
# JsonFile: path to JSON body file (UTF-8, JIRA REST API v3 format)
# EpicKey: optional, link issue to this Epic (e.g. AQEX-1)

param(
    [Parameter(Mandatory=$true)]
    [string]$JsonFile,
    [string]$EpicKey
)

$email = 'yusongt@gmail.com'
$token = 'ATATT3xFfGF0HF4yTIrmyVArQm2HtPKXXH8Zgj_ko7DKcHA5zHwps2IjK7ROdgjfHCGavpTc-sKfER21Hwonsty7Xm3DtUqvJS2OBIoBLUZSYL82-Aab4EDXs-UExx25OExoopRiP48vg3vstgcJnm5oKsnjyG1eLVjZ2N2jdsSp22_1HECuj1E=F1481C58'
$base = 'https://yusongtao.atlassian.net'

$pair = "$email`:$token"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$b64 = [System.Convert]::ToBase64String($bytes)
$headers = @{
    Authorization = "Basic $b64"
    Accept = 'application/json'
}

# Read JSON body as UTF-8
$utf8 = New-Object System.Text.UTF8Encoding($false)
$body = [System.IO.File]::ReadAllText($JsonFile, $utf8)

Write-Host "=== Creating JIRA issue ==="
try {
    $resp = Invoke-RestMethod -Uri "$base/rest/api/3/issue" -Headers $headers -Method Post -Body $body -ContentType 'application/json'
    Write-Host "SUCCESS!"
    Write-Host "Key: $($resp.key)"
    Write-Host "URL: $base/browse/$($resp.key)"

    # Link to Epic if specified
    if ($EpicKey -and $EpicKey -ne '') {
        $linkBody = '{"fields":{"parent":{"key":"' + $EpicKey + '"}}}'
        try {
            Invoke-RestMethod -Uri "$base/rest/api/3/issue/$($resp.key)" -Headers $headers -Method Put -Body $linkBody -ContentType 'application/json'
            Write-Host "Linked to Epic: $EpicKey"
        } catch {
            Write-Host "WARNING: Epic link failed: $($_.Exception.Message)"
        }
    }
} catch {
    Write-Host "FAILED: $($_.Exception.Message)"
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $errBody = $reader.ReadToEnd()
    Write-Host "Error body: $errBody"
}
