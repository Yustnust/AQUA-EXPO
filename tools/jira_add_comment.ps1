# Add comment to JIRA issue
param(
    [Parameter(Mandatory=$true)]
    [string]$IssueKey,
    [Parameter(Mandatory=$true)]
    [string]$CommentFile
)

. (Join-Path (Join-Path $PSScriptRoot '..') 'jira_token.ps1')
$base = 'https://yusongtao.atlassian.net'
$pair = "$email`:$token"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$b64 = [System.Convert]::ToBase64String($bytes)
$headers = @{
    Authorization = "Basic $b64"
    Accept = 'application/json'
}

$utf8 = New-Object System.Text.UTF8Encoding($false)
$body = [System.IO.File]::ReadAllText($CommentFile, $utf8)
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)

Write-Host "=== Adding comment to $IssueKey ==="
try {
    $resp = Invoke-RestMethod -Uri "$base/rest/api/3/issue/$IssueKey/comment" -Headers $headers -Method Post -Body $bodyBytes -ContentType 'application/json; charset=utf-8'
    Write-Host "SUCCESS! Comment added to $IssueKey"
    Write-Host "URL: $base/browse/$IssueKey"
} catch {
    Write-Host "FAILED: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "Error body: $($reader.ReadToEnd())"
    }
}
