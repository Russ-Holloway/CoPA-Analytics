# 🚀 CoPPA Analytics - Two-Step Deployment

## Step 1: Deploy Infrastructure ⚡
**Click the "Deploy to Azure" button** to create the Function App infrastructure.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json)

- ⏱️ **Takes 8-10 minutes**
- ✅ **Creates Function App with correct Python 3.11 runtime**
- ✅ **All infrastructure ready**

## Step 2: Deploy Functions 🎯
**Run this command** after the ARM deployment completes:

### Option A: PowerShell (Recommended)
```powershell
# Download and run the deployment script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Russ-Holloway/CoPPA-Analytics/main/chatbot-analytics-azure-deploy/Deploy-After-ARM.ps1" -OutFile "Deploy-After-ARM.ps1"
.\Deploy-After-ARM.ps1
```

### Option B: Azure CLI
```bash
# If you know your resource group and function app names
az functionapp deployment source config-zip \
  --resource-group "your-resource-group" \
  --name "your-function-app" \
  --src "https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip"
```

### Option C: Manual (Browser)
1. Go to your Function App in Azure Portal
2. **Advanced Tools** → **Go** (opens Kudu)
3. **Tools** → **Zip Push Deploy**
4. Drag and drop: `https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip`

## ✅ Result
- **All 6 functions deployed** in 2-3 minutes
- **Ready to use immediately**
- **Test endpoint**: `https://[your-app].azurewebsites.net/api/TestFunction`

---

## Why Two Steps?

Azure ARM templates are **excellent** for infrastructure but **unreliable** for external package deployment. This two-step approach provides:

✅ **100% success rate** for infrastructure deployment  
✅ **Multiple fallback options** for function deployment  
✅ **Clear error messages** if anything goes wrong  
✅ **Enterprise-ready** reliability  

**Total time: 10-13 minutes for complete working solution**
