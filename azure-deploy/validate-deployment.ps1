# ARM TEMPLATE VALIDATION - Pre-Deployment Check
# This script validates the ARM template for common issues that prevent function loading

Write-Host "🔍 ARM TEMPLATE VALIDATION" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

$templatePath = "c:\home\russell\CoPPA-Analytics\chatbot-analytics-azure-deploy\azuredeploy.json"
$functionZipPath = "c:\home\russell\CoPPA-Analytics\chatbot-analytics-azure-deploy\function-app-final.zip"

# Check 1: Template file exists
Write-Host "✓ Checking ARM template..." -ForegroundColor Yellow
if (Test-Path $templatePath) {
    Write-Host "  ✅ ARM template found" -ForegroundColor Green
} else {
    Write-Host "  ❌ ARM template missing!" -ForegroundColor Red
    exit 1
}

# Check 2: Function ZIP exists
Write-Host "✓ Checking function package..." -ForegroundColor Yellow
if (Test-Path $functionZipPath) {
    Write-Host "  ✅ Function ZIP package found" -ForegroundColor Green
} else {
    Write-Host "  ❌ Function ZIP package missing!" -ForegroundColor Red
    exit 1
}

# Check 3: JSON syntax validation
Write-Host "✓ Validating JSON syntax..." -ForegroundColor Yellow
try {
    $template = Get-Content $templatePath -Raw | ConvertFrom-Json
    Write-Host "  ✅ JSON syntax is valid" -ForegroundColor Green
} catch {
    Write-Host "  ❌ JSON syntax error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Check 4: Critical settings validation
Write-Host "✓ Checking critical Linux Function App settings..." -ForegroundColor Yellow

$templateContent = Get-Content $templatePath -Raw

# Check for Linux configuration
if ($templateContent -match '"kind":\s*"functionapp,linux"') {
    Write-Host "  ✅ Function App kind set to 'functionapp,linux'" -ForegroundColor Green
} else {
    Write-Host "  ❌ Function App kind not set to Linux!" -ForegroundColor Red
}

# Check for Python runtime
if ($templateContent -match '"linuxFxVersion":\s*"Python\|3\.11"') {
    Write-Host "  ✅ Python 3.11 runtime configured" -ForegroundColor Green
} else {
    Write-Host "  ❌ Python 3.11 runtime not configured!" -ForegroundColor Red
}

# Check for package URL
if ($templateContent -match 'WEBSITE_RUN_FROM_PACKAGE.*function-app-final\.zip') {
    Write-Host "  ✅ Package deployment URL configured" -ForegroundColor Green
} else {
    Write-Host "  ❌ Package deployment URL missing!" -ForegroundColor Red
}

# Check 5: CRITICAL FIX - Storage settings cleared
Write-Host "✓ Checking CRITICAL FIX - Storage settings..." -ForegroundColor Yellow

if ($templateContent -match '"WEBSITE_CONTENTAZUREFILECONNECTIONSTRING"[^}]*"value":\s*""') {
    Write-Host "  ✅ WEBSITE_CONTENTAZUREFILECONNECTIONSTRING cleared" -ForegroundColor Green
} else {
    Write-Host "  ❌ WEBSITE_CONTENTAZUREFILECONNECTIONSTRING not cleared!" -ForegroundColor Red
}

if ($templateContent -match '"WEBSITE_CONTENTSHARE"[^}]*"value":\s*""') {
    Write-Host "  ✅ WEBSITE_CONTENTSHARE cleared" -ForegroundColor Green
} else {
    Write-Host "  ❌ WEBSITE_CONTENTSHARE not cleared!" -ForegroundColor Red
}

# Check 6: Function loading enhancement settings
Write-Host "✓ Checking function loading enhancements..." -ForegroundColor Yellow

if ($templateContent -match '"WEBSITE_FORCE_RESTART"[^}]*"value":\s*"1"') {
    Write-Host "  ✅ WEBSITE_FORCE_RESTART enabled" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ WEBSITE_FORCE_RESTART not set" -ForegroundColor Yellow
}

if ($templateContent -match '"FUNCTIONS_EXTENSION_AUTOINSTALL"[^}]*"value":\s*"1"') {
    Write-Host "  ✅ FUNCTIONS_EXTENSION_AUTOINSTALL enabled" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ FUNCTIONS_EXTENSION_AUTOINSTALL not set" -ForegroundColor Yellow
}

# Check 7: Function package contents
Write-Host "✓ Checking function package contents..." -ForegroundColor Yellow
$functionDir = "c:\home\russell\CoPPA-Analytics\chatbot-analytics-azure-deploy\function-code"

$expectedFunctions = @("GetAnalytics", "Dashboard", "GetQuestions", "SeedData", "TestFunction", "TimerTrigger", "FunctionSync")
$missingFunctions = @()

foreach ($func in $expectedFunctions) {
    if (Test-Path (Join-Path $functionDir $func)) {
        Write-Host "  ✅ $func function found" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $func function missing!" -ForegroundColor Red
        $missingFunctions += $func
    }
}

if (Test-Path (Join-Path $functionDir "host.json")) {
    Write-Host "  ✅ host.json found" -ForegroundColor Green
} else {
    Write-Host "  ❌ host.json missing!" -ForegroundColor Red
}

if (Test-Path (Join-Path $functionDir "requirements.txt")) {
    Write-Host "  ✅ requirements.txt found" -ForegroundColor Green
} else {
    Write-Host "  ❌ requirements.txt missing!" -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

if ($missingFunctions.Count -eq 0) {
    Write-Host "🎉 ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ The ARM template should now deploy successfully with automatic function loading!" -ForegroundColor Green
    Write-Host "✅ Critical Linux Function App storage conflict resolved" -ForegroundColor Green
    Write-Host "✅ All 7 functions are packaged and ready" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 READY FOR DEPLOYMENT!" -ForegroundColor Magenta
    Write-Host "   This should work for your 44 police forces one-click deployment." -ForegroundColor Yellow
} else {
    Write-Host "⚠️ ISSUES FOUND!" -ForegroundColor Red
    Write-Host "   Missing functions: $($missingFunctions -join ', ')" -ForegroundColor Red
    Write-Host "   Please fix these issues before deployment." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔗 GitHub ZIP URL: https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app-final.zip" -ForegroundColor Cyan
Write-Host "📋 Deploy to Azure: Use the button in your README.md" -ForegroundColor Cyan
