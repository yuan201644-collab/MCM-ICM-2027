$ErrorActionPreference = 'Continue'
$work = $PSScriptRoot
$root = Split-Path $work -Parent
Set-Location $root
Write-Output "== root: $root"

if (-not (Test-Path (Join-Path $root '.git'))) {
    git init -b main
    git config core.quotepath false
    git config core.autocrlf false
}

git config user.name  'yuan201644-collab'
git config user.email 'yuan201644@gmail.com'

Write-Output "== git add"
git add -A
Write-Output "== staged files: $((git diff --cached --name-only | Measure-Object).Count)"

git commit -m "Initial commit: MCM/ICM 2022 and 2024 problems, O-award papers, Chinese translations, reading materials"
Write-Output "== commit exit: $LASTEXITCODE"

Write-Output "== gh repo create + push"
gh repo create MCM-ICM-2027 --public --source . --remote origin --push --description "MCM/ICM 2027 team preparation: problems, O-award papers, translations, study materials"
Write-Output "== gh exit: $LASTEXITCODE"

git status -sb
git remote -v
