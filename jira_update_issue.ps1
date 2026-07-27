# Reusable JIRA issue update script (fix Chinese ??? encoding)
# Usage: powershell -ExecutionPolicy Bypass -File jira_update_issue.ps1 -IssueKey <key> -JsonFile <path>
param(
    [Parameter(Mandatory=$true)]
    [string]$IssueKey,
    [Parameter(Mandatory=$true)]
    [string]$JsonFile
)

# Load credentials from external file (not tracked by git)
$tokenFile = Join-Path $PSScriptRoot 'jira_token.ps1'
if (-not (Test-Path $tokenFile)) {
    Write-Host "ERROR: jira_token.ps1 not found."
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

# Read JSON body as UTF-8 and convert to byte array (avoid Latin1 ???)
$utf8 = New-Object System.Text.UTF8Encoding($false)
$body = [System.IO.File]::ReadAllText($JsonFile, $utf8)
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)

Write-Host "=== Updating $IssueKey ==="
try {
    Invoke-RestMethod -Uri "$base/rest/api/3/issue/$IssueKey" -Headers $headers -Method Put -Body $bodyBytes -ContentType 'application/json; charset=utf-8'
    Write-Host "SUCCESS! $IssueKey updated"
    Write-Host "URL: $base/browse/$IssueKey"
} catch {
    Write-Host "FAILED: $($_.Exception.Message)"
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $errBody = $reader.ReadToEnd()
    Write-Host "Error body: $errBody"
}
