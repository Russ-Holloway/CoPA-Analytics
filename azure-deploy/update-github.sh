#!/bin/bash
# Update GitHub Repository for Deploy to Azure Button
# This script commits the updated function package and ARM template

echo "🚀 Updating CoPPA Analytics for Deploy to Azure"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "azuredeploy.json" ]; then
    echo "❌ Error: azuredeploy.json not found. Please run this script from the chatbot-analytics-azure-deploy directory."
    exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed or not in PATH."
    exit 1
fi

echo "📋 Files to update:"
echo "  ✅ azuredeploy.json (ARM template with Python fixes)"
echo "  ✅ function-app-updated.zip (Updated function package)"
echo "  ✅ host.json (Python 3.11 extension bundle)"
echo "  ✅ requirements.txt (Updated dependencies)"
echo "  ✅ README.md (Deploy to Azure instructions)"
echo "  ✅ DEPLOY_TO_AZURE_GUIDE.md (Comprehensive guide)"
echo "  ✅ verify-deployment.ps1 (Post-deployment verification)"
echo ""

# Stage all changes
echo "📤 Staging changes for commit..."
git add azuredeploy.json
git add function-app-updated.zip
git add function-code/host.json
git add function-code/requirements.txt
git add README.md
git add DEPLOY_TO_AZURE_GUIDE.md
git add verify-deployment.ps1
git add complete-python-fix.ps1
git add fix-python-runtime.ps1
git add fix-python-runtime.bat
git add PYTHON_RUNTIME_FIX_README.md

# Check for changes
if ! git diff --staged --quiet; then
    echo "✅ Changes staged successfully"
    
    # Commit changes
    echo "💾 Committing changes..."
    git commit -m "Fix Python 3.11 runtime issues for Deploy to Azure button

- Updated azuredeploy.json with Python 3.11 settings and build configuration
- Updated host.json to use extension bundle [4.0.0, 5.0.0) for Python 3.11
- Updated requirements.txt with latest compatible package versions
- Added comprehensive Deploy to Azure guide
- Added post-deployment verification script
- Added automated fix scripts for existing deployments
- Updated README with improved Deploy to Azure instructions

This resolves the 503 'function host not running' error when using Deploy to Azure."
    
    # Push to main branch
    echo "🌐 Pushing to GitHub..."
    git push origin main
    
    echo ""
    echo "✅ Successfully updated GitHub repository!"
    echo ""
    echo "🎯 Your Deploy to Azure button will now work correctly with:"
    echo "   📦 Updated function package: function-app-updated.zip"
    echo "   ⚙️  Python 3.11 runtime configuration"
    echo "   🔧 All necessary build settings"
    echo "   📚 Comprehensive deployment guide"
    echo ""
    echo "🔗 Test your Deploy to Azure button at:"
    echo "   https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json"
    echo ""
    echo "📖 Share the deployment guide with users:"
    echo "   https://github.com/Russ-Holloway/CoPPA-Analytics/blob/main/chatbot-analytics-azure-deploy/DEPLOY_TO_AZURE_GUIDE.md"
    
else
    echo "ℹ️  No changes to commit - repository is already up to date"
fi

echo ""
echo "🎉 Deploy to Azure setup complete!"
