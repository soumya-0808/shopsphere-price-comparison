$ErrorActionPreference = 'Stop'

Write-Host "=== ShopSphere - GitHub Publisher ===" -ForegroundColor Cyan

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or not available in PATH. Install Git for Windows, then run this script again."
}

$repo = Read-Host "Enter your GitHub repository URL (example: https://github.com/USERNAME/shopsphere-price-comparison.git)"
if ([string]::IsNullOrWhiteSpace($repo)) { throw "Repository URL is required." }

if (-not (Test-Path .git)) {
    git init
    git branch -M main
}

# Prevent accidental secret/config commits.
$blocked = @('.env', 'frontend/node_modules', 'frontend/dist', 'backend/__pycache__')
foreach ($path in $blocked) {
    if (Test-Path $path) { Write-Host "Note: $path exists locally and is ignored by Git." -ForegroundColor Yellow }
}

git add .

$status = git status --porcelain
if ($status) {
    git commit -m "feat: finalize ShopSphere price comparison platform"
} else {
    Write-Host "No new changes to commit." -ForegroundColor Yellow
}

$existing = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    git remote add origin $repo
} elseif ($existing -ne $repo) {
    git remote set-url origin $repo
}

git push -u origin main

Write-Host "`nPublished successfully. Open your repository in GitHub." -ForegroundColor Green
