# CoPPA Analytics - Police Force Deployment Guide

## 🚔 For Police Force IT Teams

This guide explains how any police force can deploy CoPPA Analytics in their Azure tenant.

## 📋 Prerequisites

### What You Need:
1. **Existing CoPPA Chatbot** with Cosmos DB deployment
2. **Azure Subscription** with appropriate permissions
3. **Admin Email Address** for receiving analytics reports
4. **5-10 minutes** for deployment

### Required Azure Permissions:
- `Contributor` role on Azure subscription or resource group
- Ability to create: Function Apps, Storage Accounts, Application Insights

## 🚀 Deployment Options

### Option 1: One-Click Azure Portal (Easiest)

1. **Visit the GitHub Repository:**
   ```
   https://github.com/british-transport-police/AI-Analytics
   ```

2. **Click "Deploy to Azure" Button** in the README

3. **Fill in Deployment Form:**
   - **Force Prefix**: Your force code (e.g., "BTP", "MET", "GMP", "WMP")
   - **Admin Email**: Email for daily reports (e.g., analytics@yourforce.police.uk)
   - **Cosmos DB Endpoint**: Your existing CoPPA Cosmos DB URL
   - **Cosmos DB Key**: Your existing CoPPA Cosmos DB primary key
   - **Database Name**: Usually "coppa-conversations" (check your CoPPA deployment)
   - **Container Name**: Usually "conversations" (check your CoPPA deployment)

4. **Deploy** (takes 5-10 minutes)

5. **Access Your Dashboard:**
   - Dashboard URL will be shown in deployment outputs
   - Format: `https://func-coppa-[yourforce]-analytics.azurewebsites.net/api/Dashboard`

### Option 2: PowerShell Script (For IT Teams)

1. **Clone Repository:**
   ```powershell
   git clone https://github.com/british-transport-police/AI-Analytics.git
   cd AI-Analytics/chatbot-analytics-azure-deploy
   ```

2. **Run Deployment Script:**
   ```powershell
   .\deploy-coppa.ps1 -ForceId "YourForce" -ResourceGroupName "rg-coppa-analytics" -AdminEmail "analytics@yourforce.police.uk"
   ```

3. **Follow Prompts** for Cosmos DB details

### Option 3: Azure CLI (Advanced)

```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-coppa-analytics --location "UK South"

# Deploy template
az deployment group create \
  --resource-group rg-coppa-analytics \
  --template-uri https://raw.githubusercontent.com/british-transport-police/AI-Analytics/main/chatbot-analytics-azure-deploy/azuredeploy.json \
  --parameters forcePrefix=YourForce adminEmail=analytics@yourforce.police.uk
```

## 🔧 Finding Your CoPPA Cosmos DB Details

### In Azure Portal:
1. Go to your existing CoPPA resource group
2. Find your Cosmos DB account
3. Go to **Keys** section
4. Copy:
   - **URI** (this is your endpoint)
   - **PRIMARY KEY** (this is your key)
   - **Database name** (usually "coppa-conversations")
   - **Container name** (usually "conversations")

### Example Values:
```
Endpoint: https://cosmos-yourforce-coppa.documents.azure.com:443/
Key: [64-character key from Azure portal]
Database: coppa-conversations
Container: conversations
```

## 📊 What Gets Deployed

Your deployment creates:
- **Function App**: `func-coppa-[yourforce]-analytics`
- **Storage Account**: `coppa[yourforce][uniqueid]`
- **Application Insights**: `ai-coppa-[yourforce]-analytics`
- **Service Plan**: `plan-coppa-[yourforce]-analytics`

## 🎯 Immediate Access

After deployment (5-10 minutes):

### 📈 Dashboard Access:
```
https://func-coppa-[yourforce]-analytics.azurewebsites.net/api/Dashboard
```

### 📊 Analytics API:
```
https://func-coppa-[yourforce]-analytics.azurewebsites.net/api/analytics
```

### 📧 Daily Reports:
- Automatically sent to your admin email
- 7:00 AM daily summary
- Weekly trends every Monday

## 🔒 Security & Privacy

- **Secure Connection**: All data encrypted in transit (HTTPS/TLS 1.2)
- **Azure Security**: Follows Azure security best practices
- **Data Isolation**: Your analytics remain in your Azure tenant
- **No Data Sharing**: BTP cannot access your analytics data
- **GDPR Compliant**: Personal data handling follows UK police standards

## 🛠️ Customization Options

### Branding:
- Force logo and colors can be customized
- Email templates can be branded for your force
- Dashboard title shows your force name

### Categories:
- Default: Crime Reporting, Traffic, General Enquiry, etc.
- Can be customized for your force's specific needs

### Reports:
- Daily/weekly frequency can be adjusted
- Additional recipients can be added
- Custom metrics can be included

## 🧪 Testing Your Deployment

### 1. Dashboard Test:
Visit your dashboard URL - should show demo data if no conversations yet

### 2. API Test:
```
https://func-coppa-[yourforce]-analytics.azurewebsites.net/api/analytics?days=7
```

### 3. Email Test:
Check your admin email for a welcome message

## 🆘 Troubleshooting

### Common Issues:

**Dashboard shows "Loading..." forever:**
- Check Cosmos DB connection details
- Verify your CoPPA database has conversation data

**No daily emails:**
- Check admin email address is correct
- Check Azure Function App logs

**"Access Denied" errors:**
- Verify Cosmos DB key is correct
- Check firewall settings on Cosmos DB

**Function deployment failed:**
- Check Azure permissions
- Verify resource group exists
- Try deploying to different Azure region

### Getting Help:
1. Check Azure Function App logs in Azure Portal
2. Review deployment logs in Azure Portal
3. Contact your Azure support team
4. File issues on GitHub repository

## 💰 Cost Estimates

### Monthly Costs (approximate):
- **Function App**: £5-20/month (depends on usage)
- **Storage**: £1-5/month 
- **Application Insights**: £5-15/month
- **Total**: ~£15-40/month for typical force

### Cost Optimization:
- Uses consumption-based pricing
- Scales automatically with usage
- No fixed monthly fees
- Can set spending limits

## 📞 Support Contacts

### For Deployment Issues:
- Your Azure support team
- Your IT department Azure administrators

### For CoPPA Analytics Questions:
- GitHub Issues: https://github.com/british-transport-police/AI-Analytics/issues
- Documentation: Available in repository

## 🎉 Success Checklist

After deployment, you should have:
- ✅ Working dashboard with your force branding
- ✅ Analytics API returning your conversation data
- ✅ Daily email reports being received
- ✅ Application Insights monitoring active
- ✅ All resources properly named with your force prefix

---

## 📧 Sample Email to Force IT Teams

**Subject: CoPPA Analytics - Self-Service Deployment Available**

Your force can now deploy its own CoPPA Analytics dashboard in minutes:

🔗 **Deploy Now:** https://github.com/british-transport-police/AI-Analytics
📊 **What You Get:** Real-time analytics, automated reports, executive dashboards
⏱️ **Time Required:** 5-10 minutes setup
💰 **Cost:** ~£15-40/month (consumption-based)
🔒 **Security:** Deployed in your Azure tenant, GDPR compliant

**Next Steps:**
1. Click "Deploy to Azure" button in repository
2. Enter your force details and Cosmos DB connection
3. Access your analytics dashboard immediately

Questions? Check the deployment guide or contact your Azure team.

---

*This solution is provided by BTP Digital Analytics Team for use by all UK police forces with CoPPA deployments.*
