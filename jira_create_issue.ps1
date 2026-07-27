# Reusable JIRA issue creation script
# Usage: powershell -ExecutionPolicy Bypass -File jira_create_issue.ps1 -JsonFile <path> [-EpicKey AQEX-1]
# JsonFile: path to JSON body file (UTF-8, JIRA REST API v3 format)
# EpicKey: optional, link issue to this Epic (e.g. AQEX-1)

param(
    [Parameter(Mandatory=$true)]
    [string]$JsonFile,
    [string]$EpicKey
)

# Load credentials from external file (not tracked by git)
$tokenFile = Join-Path $PSScriptRoot 'jira_token.ps1'
if (-not (Test-Path $tokenFile)) {
    Write-Host "ERROR: jira_token.ps1 not found. Create it with:`n  `$email = 'your@email'`n  `$token = 'your_token'"
    exit 1
}
. $tokenFile
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
# Convert to UTF-8 byte array (Invoke-RestMethod default Latin1 causes Chinese ???)
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)

Write-Host "=== Creating JIRA issue ==="
try {
    $resp = Invoke-RestMethod -Uri "$base/rest/api/3/issue" -Headers $headers -Method Post -Body $bodyBytes -ContentType 'application/json; charset=utf-8'
    Write-Host "SUCCESS!"
    Write-Host "Key: $($resp.key)"
    Write-Host "URL: $base/browse/$($resp.key)"

    # Link to Epic if specified
    if ($EpicKey -and $EpicKey -ne '') {
        $linkBody = '{"fields":{"parent":{"key":"' + $EpicKey + '"}}}'
        $linkBytes = [System.Text.Encoding]::UTF8.GetBytes($linkBody)
        try {
            Invoke-RestMethod -Uri "$base/rest/api/3/issue/$($resp.key)" -Headers $headers -Method Put -Body $linkBytes -ContentType 'application/json; charset=utf-8'
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
