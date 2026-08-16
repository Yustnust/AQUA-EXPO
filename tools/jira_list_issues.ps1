# List AQEX project issues
. (Join-Path (Join-Path $PSScriptRoot '..') 'jira_token.ps1')
$base = 'https://yusongtao.atlassian.net'
$pair = "$email`:$token"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$b64 = [System.Convert]::ToBase64String($bytes)
$headers = @{
    Authorization = "Basic $b64"
    Accept = 'application/json'
}

$jql = $args[0]
if (-not $jql) { $jql = 'project=AQEX' }

$uri = "$base/rest/api/3/search/jql?jql=" + [Uri]::EscapeDataString($jql) + "&maxResults=100&fields=summary,status,issuetype,parent"

try {
    $resp = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
    $resp.issues | Select-Object key, @{n='summary';e={$_.fields.summary}}, @{n='status';e={$_.fields.status.name}}, @{n='issuetype';e={$_.fields.issuetype.name}}, @{n='parent';e={$_.fields.parent.key}} | Format-Table -AutoSize
    Write-Host "Total: $($resp.total)"
} catch {
    Write-Host "FAILED: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host $reader.ReadToEnd()
    }
}
