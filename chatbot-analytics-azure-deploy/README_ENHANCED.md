# Chatbot Analytics - Enhanced Azure Deployment

🚀 **Complete one-click deployment** of Azure Functions for Police Force Chatbot Analytics with **Cosmos DB integration** and **real-time data processing**.

## ✨ Enhanced Features

- ✅ **One-Click Deployment** with working GitHub URL
- ✅ **Cosmos DB Integration** for real analytics data
- ✅ **Sample Data Seeding** for immediate testing
- ✅ **Enhanced PowerShell Deployment** script
- ✅ **Automatic Fallback** from Cosmos DB to mock data
- ✅ **Production-Ready** with monitoring and logging

## 🚀 Quick Deploy

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fbritish-transport-police%2FAI-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json)

## 🏗️ What Gets Deployed

### Azure Resources
- **Resource Group** - Container for all resources
- **Storage Account** - For function app files and data
- **Function App** - Serverless compute with Python 3.9 runtime
- **Application Insights** - Monitoring and logging
- **Cosmos DB Account** - NoSQL database with free tier (400 RU/s)
  - Database: `chatbot-analytics`
  - Container: `interactions`
  - Partition key: `/forceId`

### Azure Functions
- **TestFunction** - Health check endpoint (`GET /api/TestFunction`)
- **GetAnalytics** - Data analytics endpoint (`GET /api/GetAnalytics`)
- **TimerTrigger** - Daily data extraction (2 AM UTC)
- **SeedData** - Sample data generator (`POST /api/SeedData`)

## 📊 Enhanced Analytics Features

### Real Cosmos DB Integration
```json
{
  "forceId": "btp",
  "summary": {
    "totalInteractions": 1250,
    "uniqueUsers": 340,
    "satisfactionScore": 4.1
  },
  "categories": {
    "crime_reporting": { "count": 450, "satisfaction": 4.3 },
    "traffic_incidents": { "count": 380, "satisfaction": 4.0 }
  },
  "metadata": {
    "data_source": "cosmos_db",
    "generated_at": "2025-07-01T12:00:00Z"
  }
}
```

### Query Parameters
- `startDate` & `endDate` - Filter by date range
- `category` - Filter by interaction category (`crime_reporting`, `traffic_incidents`, etc.)

## 🛠️ Enhanced Deployment Options

### Option 1: PowerShell Script (Recommended)

```powershell
# Basic deployment
.\deploy-enhanced.ps1 -ForceId "btp" -Location "UK South"

# With sample data seeding
.\deploy-enhanced.ps1 -ForceId "btp" -Location "UK South" -SeedData

# Production environment
.\deploy-enhanced.ps1 -ForceId "btp" -Location "UK South" -Environment "prod"
```

### Option 2: One-Click Azure Portal
Click the "Deploy to Azure" button above and fill in parameters.

### Option 3: Azure CLI
```bash
az deployment group create \
  --resource-group rg-btp-chatbot-dev \
  --template-file azuredeploy.json \
  --parameters @azuredeploy.parameters.json
```

## 📋 Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `forceIdentifier` | Police force code | Required | `btp`, `met`, `gmp` |
| `location` | Azure region | `UK South` | `UK South`, `West Europe` |
| `environment` | Environment type | `dev` | `dev`, `test`, `prod` |

## 🔗 Endpoints (after deployment)

Base URL: `https://func-{forceId}-chatbot-{environment}.azurewebsites.net`

### API Endpoints
- **Health Check**: `GET /api/TestFunction`
- **Analytics**: `GET /api/GetAnalytics[?startDate=&endDate=&category=]`
- **Seed Data**: `POST /api/SeedData`
- **Timer**: Automatic daily execution

### Sample Queries
```powershell
# Get all analytics
Invoke-RestMethod -Uri "$baseUrl/api/GetAnalytics"

# Filter by category
Invoke-RestMethod -Uri "$baseUrl/api/GetAnalytics?category=crime_reporting"

# Date range
Invoke-RestMethod -Uri "$baseUrl/api/GetAnalytics?startDate=2025-06-01&endDate=2025-06-30"

# Seed sample data
Invoke-RestMethod -Uri "$baseUrl/api/SeedData" -Method Post
```

## 🔧 Post-Deployment Setup

### 1. Verify Deployment
```powershell
# Test health endpoint
$url = "https://func-btp-chatbot-dev.azurewebsites.net/api/TestFunction"
Invoke-RestMethod -Uri $url
```

### 2. Seed Sample Data (Optional)
```powershell
# Generate 30 days of sample interactions
$seedUrl = "https://func-btp-chatbot-dev.azurewebsites.net/api/SeedData"
Invoke-RestMethod -Uri $seedUrl -Method Post
```

### 3. Monitor Performance
- Navigate to Function App in Azure Portal
- View Application Insights for metrics and logs
- Check Cosmos DB for data storage

## 🎯 Data Source Indicators

The analytics endpoint includes a `metadata.data_source` field:
- `"cosmos_db"` - Real data from Cosmos DB
- `"mock_data"` - Fallback mock data (when Cosmos DB unavailable)
- `"cosmos_db_error"` - Cosmos DB connection failed

## 🛡️ Security & Configuration

### Environment Variables (Auto-configured)
- `FORCE_IDENTIFIER` - Police force code
- `COSMOS_DB_ENDPOINT` - Cosmos DB endpoint URL
- `COSMOS_DB_KEY` - Primary access key
- `COSMOS_DB_DATABASE` - Database name (`chatbot-analytics`)
- `COSMOS_DB_CONTAINER` - Container name (`interactions`)

### Security Features
- HTTPS enforced on all endpoints
- Azure Function keys for API authentication
- Cosmos DB firewall and managed identity
- Application Insights for monitoring

## 📚 Documentation

- **[Enhanced Setup Guide](SETUP_GUIDE_ENHANCED.md)** - Complete deployment instructions
- **[Original Setup Guide](SETUP_GUIDE.md)** - Basic setup reference
- **[ARM Template](azuredeploy.json)** - Infrastructure as code
- **[Function Code](function-code/)** - Python function implementations

## 🔄 Multi-Tenant Support

Deploy for multiple police forces:
```powershell
$forces = @("btp", "met", "gmp", "wmp")
foreach ($force in $forces) {
    .\deploy-enhanced.ps1 -ForceId $force -Location "UK South" -Environment "prod"
}
```

## 💰 Cost Estimation

**Expected monthly cost per force:**
- Function App (Consumption): £5-15
- Cosmos DB (Free tier): £0
- Storage Account: £1-3
- Application Insights: £2-5
- **Total: £8-23 per force**

## 🆘 Troubleshooting

### Common Issues

#### "cosmos_db_error" in response
- **Cause**: Cosmos DB connection failed
- **Solution**: Check environment variables and Cosmos DB status

#### Function returns 404
- **Cause**: Function code not deployed
- **Solution**: Redeploy using `func azure functionapp publish`

#### Deployment script fails
- **Cause**: Missing tools or permissions
- **Solution**: Install Azure PowerShell and Functions Core Tools

### Support Commands
```powershell
# Check deployment status
Get-AzResourceGroupDeployment -ResourceGroupName "rg-btp-chatbot-dev"

# View function app logs
func azure functionapp logstream your-function-app-name

# Test endpoints
Invoke-RestMethod -Uri "https://your-function-app.azurewebsites.net/api/TestFunction"
```

## 🚀 Next Steps

1. **Deploy**: Use the enhanced PowerShell script or one-click button
2. **Seed Data**: Run the SeedData function for sample analytics
3. **Integrate**: Connect your chatbot to send data to Cosmos DB
4. **Monitor**: Set up alerts and dashboards in Azure Portal
5. **Scale**: Deploy to additional police forces as needed

## 📞 Support

For technical support:
1. Check the [Enhanced Setup Guide](SETUP_GUIDE_ENHANCED.md)
2. Review Azure Function App logs
3. Contact the development team

---

**🎉 Ready to deploy?** Use the enhanced PowerShell script for the best experience:
```powershell
.\deploy-enhanced.ps1 -ForceId "your-force-code" -Location "UK South" -SeedData
```
