<#
Maxford book key: the key that opens the locked book pages, kept on Cloudflare (tools/book-key-worker).

Chalane ka tareeqa (project folder D:\MAXFORD GLOBLE se):
  powershell -ExecutionPolicy Bypass -File tools\book-key.ps1 <kaam> [website]

Kaam:
  status                 Worker kaam kar raha hai? kaun si websites key le sakti hain?
  sites                  Websites ki list
  add-site <website>     Nayi website ko key lene do      (masalan: add-site https://maxford.com)
  remove-site <website>  Website ko key dena band karo
  set-key [file]         Key Cloudflare par rakho          (file na di to %TEMP%\maxford-book-key.txt)
  remove-key             Key Cloudflare se hata do         (naye log password page dekhenge)
  new-password           Books naye password se dobara lock karo aur nayi key Cloudflare par rakho
                         (is ke baad git commit + push karna hoga, script batayegi)

Key aur password kabhi project folder ya GitHub par nahi rakhe jate.
#>
param(
  [Parameter(Position = 0)][string]$Action = 'help',
  [Parameter(Position = 1)][string]$Value
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$WorkerDir = Join-Path $PSScriptRoot 'book-key-worker'
$Toml = Join-Path $WorkerDir 'wrangler.toml'
$WorkerUrl = 'https://maxford-book-key.book-key-worker.workers.dev'
$KeyFile = Join-Path $env:TEMP 'maxford-book-key.txt'
$NoBom = New-Object System.Text.UTF8Encoding $false

function Get-Sites {
  $line = (Get-Content $Toml) | Where-Object { $_ -match '^\s*SITES\s*=' } | Select-Object -First 1
  if (-not $line) { throw "SITES not found in $Toml" }
  $text = ($line -replace '^\s*SITES\s*=\s*"', '') -replace '"\s*$', ''
  @($text.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

function Set-Sites([string[]]$Sites) {
  $joined = ($Sites | Select-Object -Unique) -join ','
  $lines = (Get-Content $Toml) | ForEach-Object { if ($_ -match '^\s*SITES\s*=') { "SITES = `"$joined`"" } else { $_ } }
  [IO.File]::WriteAllText($Toml, (($lines -join "`n") + "`n"), $NoBom)
}

# https://maxford.com/books/  ->  https://maxford.com   (the browser sends only this part)
function Get-Origin([string]$Url) {
  if (-not $Url) { throw 'Website ka address do, masalan: https://maxford.com' }
  if ($Url -notmatch '^https?://') { $Url = "https://$Url" }
  ([Uri]$Url).GetLeftPart([UriPartial]::Authority).ToLower()
}

function Invoke-Wrangler([string[]]$WranglerArgs) {
  Push-Location $WorkerDir
  # (npm writes its warnings to stderr; PowerShell 5.1 would stop on them, so only the exit code decides)
  $before = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  try {
    # (npx.cmd, not npx: inside a -File script the npx.ps1 shim hands npm a broken command name)
    & npx.cmd --yes wrangler@4 @WranglerArgs 2>&1 | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -ne 0) { throw "wrangler $($WranglerArgs -join ' ') failed" }
  } finally { $ErrorActionPreference = $before; Pop-Location }
}

function Publish-Worker {
  Write-Host 'Worker deploy ho raha hai...'
  Invoke-Wrangler @('deploy')
}

# Puts the key as the BOOK_KEY secret through a JSON file (no BOM, no line break), deleted right after.
function Send-Key([string]$Path) {
  if (-not (Test-Path $Path)) { throw "Key file nahi mili: $Path" }
  $key = (Get-Content $Path -Raw).Trim()
  if ($key -notmatch '^[A-Za-z0-9+/]{43}=$') { throw "Yeh key sahi nahi lagti (44 harf ki base64 honi chahiye): $Path" }
  $json = Join-Path $env:TEMP ("maxford-secret-" + [Guid]::NewGuid().ToString('N') + '.json')
  try {
    [IO.File]::WriteAllText($json, ('{"BOOK_KEY":"' + $key + '"}'), $NoBom)
    Invoke-Wrangler @('secret', 'bulk', $json)
  } finally { Remove-Item $json -Force -ErrorAction SilentlyContinue }
  Write-Host 'Key Cloudflare par rakh di.'
}

function Show-Status {
  $sites = Get-Sites
  Write-Host "Worker: $WorkerUrl"
  Write-Host 'Websites jo key le sakti hain:'
  $sites | ForEach-Object { Write-Host "  $_" }
  try {
    $answer = Invoke-WebRequest $WorkerUrl -UseBasicParsing -Headers @{ Origin = $sites[0] }
    $hasKey = $answer.Content -match '"key"'
    Write-Host ("Key: " + $(if ($hasKey) { 'Cloudflare par mojood hai (website bina password khulegi)' } else { 'nahi mili' }))
  } catch {
    $code = $_.Exception.Response.StatusCode.value__
    Write-Host "Key: nahi mili (jawab $code). Website password page dikhayegi."
  }
}

switch ($Action.ToLower()) {
  'status' { Show-Status }
  'sites' { Get-Sites | ForEach-Object { Write-Host $_ } }
  'add-site' {
    $origin = Get-Origin $Value
    $sites = Get-Sites
    if ($sites -contains $origin) { Write-Host "$origin pehle se list mein hai."; break }
    Set-Sites ($sites + $origin)
    Publish-Worker
    Write-Host "$origin ab key le sakti hai. (wrangler.toml badla hai: git commit kar lein)"
  }
  'remove-site' {
    $origin = Get-Origin $Value
    $sites = Get-Sites
    if ($sites -notcontains $origin) { Write-Host "$origin list mein nahi hai."; break }
    if ($sites.Count -eq 1) { throw 'Yeh aakhri website hai; isay hatane ke bajaye remove-key chalayein.' }
    Set-Sites ($sites | Where-Object { $_ -ne $origin })
    Publish-Worker
    Write-Host "$origin ab key nahi le sakti. (wrangler.toml badla hai: git commit kar lein)"
  }
  'set-key' {
    Send-Key $(if ($Value) { $Value } else { $KeyFile })
  }
  'remove-key' {
    $sure = Read-Host 'Key Cloudflare se hata dein? Naye log password page dekhenge. (haan likhein)'
    if ($sure -notin @('haan', 'han', 'yes', 'y')) { Write-Host 'Kuch nahi badla.'; break }
    Invoke-Wrangler @('secret', 'delete', 'BOOK_KEY', '--force')
    Write-Host 'Key hata di. Wapas rakhne ke liye: set-key'
  }
  'new-password' {
    $first = Read-Host 'Naya password (kam az kam 8 harf)' -AsSecureString
    $again = Read-Host 'Dobara wahi password' -AsSecureString
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($first))
    $plain2 = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($again))
    if ($plain -ne $plain2) { throw 'Dono password alag hain. Kuch nahi badla.' }
    if ($plain.Length -lt 8) { throw 'Password kam az kam 8 harf ka ho.' }
    $env:BOOK_PASSWORD = $plain
    $env:BOOK_KEY_OUT = $KeyFile
    try {
      & python (Join-Path $PSScriptRoot 'lock_books.py')
      if ($LASTEXITCODE -ne 0) { throw 'lock_books.py failed' }
    } finally {
      Remove-Item Env:BOOK_PASSWORD, Env:BOOK_KEY_OUT -ErrorAction SilentlyContinue
    }
    [IO.File]::WriteAllText((Join-Path $env:TEMP 'maxford-book-password.txt'), $plain, $NoBom)
    Send-Key $KeyFile
    Write-Host ''
    Write-Host "Password aur key yahan hain (mehfooz jagah copy kar lein): $env:TEMP"
    Write-Host 'Ab books/ ki tabdeeli GitHub par bhejni hai: git add books ; git commit ; git push'
  }
  default { Get-Help $PSCommandPath -Detailed | Out-String | Write-Host }
}
