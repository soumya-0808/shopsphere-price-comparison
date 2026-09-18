# Publish ShopSphere to GitHub

This repository is intended to be public portfolio code. Do not commit `.env`, passwords, API keys, database dumps, `node_modules`, build output, or PostgreSQL volumes.

## Easiest method on Windows

Open PowerShell in the project root and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\publish-github.ps1
```

When prompted, paste your GitHub repository URL, for example:

```text
https://github.com/YOUR_USERNAME/shopsphere-price-comparison.git
```

Git Credential Manager may ask you to authenticate with GitHub. No GitHub token should be placed inside the project files.

## Manual commands

```powershell
git init
git branch -M main
git add .
git commit -m "feat: finalize ShopSphere price comparison platform"
git remote add origin https://github.com/YOUR_USERNAME/shopsphere-price-comparison.git
git push -u origin main
```
