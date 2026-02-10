# Language Pack Installer for TinyWorld AI
# Run this script as Administrator to download Tesseract language packs

$languages = @{
    "hin"     = "Hindi"
    "urd"     = "Urdu"
    "san"     = "Sanskrit"
    "ara"     = "Arabic"
    "fra"     = "French"
    "spa"     = "Spanish"
    "deu"     = "German"
    "chi_sim" = "Chinese Simplified"
}

$tessdata_path = "C:\Program Files\Tesseract-OCR\tessdata"
$base_url = "https://github.com/tesseract-ocr/tessdata/raw/main"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "TinyWorld AI - Language Pack Installer" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select Run as Administrator" -ForegroundColor Yellow
    pause
    exit 1
}

# Check if Tesseract is installed
if (-not (Test-Path $tessdata_path)) {
    Write-Host "ERROR: Tesseract not found at $tessdata_path" -ForegroundColor Red
    Write-Host "Please install Tesseract first using: winget install --id UB-Mannheim.TesseractOCR" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Tesseract found! Starting language pack download..." -ForegroundColor Green
Write-Host ""

$success_count = 0
$fail_count = 0

foreach ($lang in $languages.Keys) {
    $lang_name = $languages[$lang]
    $filename = "$lang.traineddata"
    $filepath = Join-Path $tessdata_path $filename
    $download_url = "$base_url/$filename"
    
    # Check if already exists
    if (Test-Path $filepath) {
        Write-Host "Already installed: $lang_name ($lang)" -ForegroundColor Gray
        $success_count++
        continue
    }
    
    Write-Host "Downloading $lang_name ($lang)..." -ForegroundColor Yellow -NoNewline
    
    try {
        Invoke-WebRequest -Uri $download_url -OutFile $filepath -ErrorAction Stop
        Write-Host " Success!" -ForegroundColor Green
        $success_count++
    }
    catch {
        Write-Host " Failed!" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        $fail_count++
    }
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Successful: $success_count languages" -ForegroundColor Green
if ($fail_count -gt 0) {
    Write-Host "Failed: $fail_count languages" -ForegroundColor Red
}
Write-Host ""
Write-Host "You can now use these languages in TinyWorld AI!" -ForegroundColor Cyan
Write-Host ""
pause
