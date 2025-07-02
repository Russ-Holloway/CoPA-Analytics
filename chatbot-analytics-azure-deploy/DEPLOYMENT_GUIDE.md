# CoPPA Analytics - Deployment Guide

## 🎯 Overview

This guide provides step-by-step instructions for deploying CoPPA Analytics to Azure. The solution is designed for police forces who already have a CoPPA chatbot deployment and want to add comprehensive analytics and reporting capabilities.

## 📋 Pre-Deployment Checklist

### ✅ Prerequisites
- [ ] Existing CoPPA chatbot deployment with Cosmos DB
- [ ] Azure subscription with appropriate permissions
- [ ] Cosmos DB connection string and database details
- [ ] Email account for automated reports (Office 365 recommended)
- [ ] Force identifier (3-8 character code for your police force)

### 🔑 Required Permissions
Your Azure account must have the following permissions:
- `Contributor` role on the target subscription or resource group
- `Storage Account Contributor` for hosting the dashboard
- `Application Insights Component Contributor` for monitoring

### 📊 Cosmos DB Requirements
- **API Type**: SQL (Core) API
- **Consistency Level**: Any (Session recommended)
- **Container Structure**: Must contain conversation/chat data with the following fields:
  - `timestamp` or `date` field
  - `message` or `content` field
  - Optional: `category`, `sentiment`, `user_id` fields

## 🚀 Deployment Methods

### Method 1: One-Click Azure Portal Deployment (Recommended)

1. **Navigate to Deployment**
   - Click the "Deploy to Azure" button in the main README
   - Sign in to your Azure account if prompted

2. **Configure Basic Settings**
   - **Subscription**: Select your Azure subscription
   - **Resource Group**: Create new or select existing
   - **Region**: Choose "UK South" for UK forces

3. **Police Force Information**
   - **Force Code**: Enter your 3-8 character force identifier (e.g., "btp", "met", "gmp")
   - **Administrator Email**: Email for deployment notifications and reports

4. **Cosmos DB Configuration**
   - **Connection String**: Paste your CoPPA Cosmos DB primary connection string
   - **Database Name**: Name of your CoPPA database (usually "coppa-chatbot")
   - **Container Name**: Container with conversation data (usually "conversations")

5. **Email Configuration**
   - **SMTP Server**: For Office 365, use "smtp.office365.com"
   - **SMTP Port**: Use "587" for TLS or "465" for SSL
   - **Username**: Email account for sending reports
   - **Password**: Email account password or app password

6. **Advanced Configuration** (Optional)
   - **Function App Plan**: Choose "Consumption" for pay-per-use or "Premium" for always-ready
   - **Storage Replication**: Choose "Standard_LRS" for cost-effectiveness
   - **Deploy Dashboard**: Check to include the web analytics dashboard

7. **Review and Deploy**
   - Review all settings
   - Check "I agree to the terms and conditions"
   - Click "Create"
   - Deployment typically takes 5-10 minutes

### Method 2: PowerShell Deployment

```powershell
# Prerequisites: Azure PowerShell module
Install-Module -Name Az -Force -AllowClobber

# Login to Azure
Connect-AzAccount

# Clone the repository
git clone https://github.com/british-transport-police/AI-Analytics.git
cd AI-Analytics/chatbot-analytics-azure-deploy

# Run enhanced deployment script
.\deploy-enhanced.ps1 `
  -ForceId "your-force-code" `
  -Location "UK South" `
  -AdminEmail "admin@yourforce.police.uk" `
  -CosmosConnectionString "your-cosmos-connection-string" `
  -CosmosDatabaseName "coppa-chatbot" `
  -CosmosContainerName "conversations" `
  -SmtpServer "smtp.office365.com" `
  -SmtpPort 587 `
  -EmailUsername "reports@yourforce.police.uk" `
  -EmailPassword "your-email-password"
```

### Method 3: Azure CLI Deployment

```bash
# Prerequisites: Azure CLI
az login

# Clone the repository
git clone https://github.com/british-transport-police/AI-Analytics.git
cd AI-Analytics/chatbot-analytics-azure-deploy

# Create resource group
az group create --name "rg-yourforce-coppa-analytics" --location "uksouth"

# Deploy ARM template
az deployment group create \
  --resource-group "rg-yourforce-coppa-analytics" \
  --template-file azuredeploy.json \
  --parameters forceIdentifier="yourforce" \
               adminEmail="admin@yourforce.police.uk" \
               cosmosConnectionString="your-cosmos-connection" \
               cosmosDatabaseName="coppa-chatbot" \
               cosmosContainerName="conversations"
```

## 🔧 Post-Deployment Configuration

### 1. Verify Deployment
After deployment completes, verify the following resources were created:
- **Function App**: `func-<force>-coppa-analytics`
- **Storage Account**: `st<force>coppa<random>`
- **Application Insights**: `appi-<force>-coppa-analytics`
- **Resource Group**: `rg-<force>-coppa-analytics`

### 2. Test Basic Functionality

#### Health Check
```bash
curl "https://func-<your-force>-coppa-analytics.azurewebsites.net/api/health"
```
Expected response: `{"status": "healthy", "database": "connected", "timestamp": "..."}`

#### Analytics API Test
```bash
curl "https://func-<your-force>-coppa-analytics.azurewebsites.net/api/get_coppa_analytics?days=7"
```

### 3. Access the Dashboard
Navigate to: `https://func-<your-force>-coppa-analytics.azurewebsites.net/dashboard`

### 4. Configure Email Recipients (Optional)
To add additional report recipients:
1. Go to Azure Portal → Function App → Configuration
2. Add new application setting: `ADDITIONAL_RECIPIENTS`
3. Value: `email1@force.police.uk;email2@force.police.uk`

## 🛠️ Customization Options

### Branding Customization
1. **Logo**: Upload your force logo to the storage account
2. **Colors**: Modify CSS variables in the dashboard
3. **Report Templates**: Customize email report templates

### Functional Customization
1. **Report Schedule**: Modify timer trigger in `function.json`
2. **Analytics Queries**: Customize Cosmos DB queries for force-specific data
3. **Alert Thresholds**: Configure custom monitoring alerts

## 🔍 Troubleshooting

### Common Issues

#### 1. Deployment Fails with "Storage Account Name Invalid"
**Problem**: Storage account names must be globally unique and 3-24 characters.
**Solution**: The deployment automatically generates a unique name. If it fails, try deploying to a different region.

#### 2. "Cannot Connect to Cosmos DB"
**Problem**: Invalid connection string or database permissions.
**Solution**: 
- Verify the connection string is correct and includes the key
- Ensure the database and container names exist
- Check Cosmos DB firewall settings

#### 3. Email Reports Not Sending
**Problem**: SMTP configuration or authentication issues.
**Solution**:
- Verify SMTP server settings (use smtp.office365.com for Office 365)
- Enable "Less secure app access" or use app passwords
- Check the email account isn't locked or suspended

#### 4. Dashboard Shows "No Data"
**Problem**: Function app cannot read from Cosmos DB or no data exists.
**Solution**:
- Verify Cosmos DB connection settings
- Check that conversations exist in the specified container
- Review Function App logs in Application Insights

### Diagnostic Commands

#### Check Function App Logs
```bash
# Using Azure CLI
az webapp log tail --name "func-<force>-coppa-analytics" --resource-group "rg-<force>-coppa-analytics"
```

#### Test Cosmos DB Connection
```python
# Run in Azure Cloud Shell or local Python environment
from azure.cosmos import CosmosClient
client = CosmosClient.from_connection_string("<your-connection-string>")
database = client.get_database_client("<database-name>")
container = database.get_container_client("<container-name>")
items = list(container.query_items("SELECT TOP 1 * FROM c", enable_cross_partition_query=True))
print(f"Found {len(items)} items")
```

## 📊 Monitoring and Alerts

### Built-in Monitoring
The deployment includes automatic monitoring via Application Insights:
- Function execution metrics
- Error tracking and stack traces
- Performance counters
- Custom telemetry from CoPPA functions

### Recommended Alerts
Configure these alerts in Azure Monitor:
1. **Function Failures**: Alert when function error rate > 5%
2. **High Response Time**: Alert when average response time > 30 seconds
3. **Database Connectivity**: Alert on Cosmos DB connection failures
4. **Email Delivery**: Alert on SMTP failures

### Custom Dashboards
Create custom Azure dashboards with:
- Function execution counts
- CoPPA conversation volumes
- Error rates and response times
- Cosmos DB request units and throttling

## 🔄 Maintenance and Updates

### Regular Maintenance Tasks

#### Weekly
- [ ] Review Application Insights for any errors or performance issues
- [ ] Check email report delivery logs
- [ ] Verify dashboard is accessible and showing current data

#### Monthly
- [ ] Review storage account usage and costs
- [ ] Check Function App scaling and performance
- [ ] Update email distribution lists if needed
- [ ] Review and optimize Cosmos DB queries

#### Quarterly
- [ ] Update Azure Function runtime if new versions available
- [ ] Review security recommendations in Azure Security Center
- [ ] Evaluate usage patterns and consider scaling adjustments
- [ ] Update deployment documentation with any force-specific changes

### Updating the Solution
When updates are available:
1. **Test Environment**: Deploy updates to a test environment first
2. **Backup**: Export current configuration and test data
3. **Deploy**: Use the same deployment method with updated templates
4. **Verify**: Test all functionality after update
5. **Monitor**: Watch for any issues in the first 24 hours

## 📞 Support

### Self-Service Resources
1. **Documentation**: Check README.md and this deployment guide
2. **Logs**: Review Application Insights and Function App logs
3. **Community**: Search GitHub Issues for similar problems

### Getting Help
1. **GitHub Issues**: Report bugs or request features
2. **Email Support**: Contact the development team for urgent issues
3. **Community Forum**: Connect with other forces using CoPPA Analytics

### Emergency Contacts
For critical issues affecting police operations:
- **Primary**: Create urgent GitHub issue with "URGENT" label
- **Secondary**: Email the development team directly
- **Escalation**: Contact your Azure support representative

---

**🎯 Deployment Success**: Your CoPPA Analytics solution is now ready to provide valuable insights into citizen engagement patterns and help improve community policing effectiveness!
