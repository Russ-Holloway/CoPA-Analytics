# Setup Guide for Police Forces

## Prerequisites

### Azure Requirements
- Azure subscription with sufficient permissions
- Resource creation permissions (Contributor role or higher)
- Azure Functions and Storage account creation permissions

### Development Tools (for manual deployment)
- PowerShell 5.1 or later
- Azure PowerShell module
- Azure Functions Core Tools v4

### Install Required Tools

#### Azure PowerShell Module
```powershell
Install-Module -Name Az -AllowClobber -Scope CurrentUser
```

#### Azure Functions Core Tools
```powershell
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

## Deployment Options

### Option 1: One-Click Azure Deployment (Recommended)

1. Click the "Deploy to Azure" button in README.md
2. Fill in the parameters:
   - **Force Identifier**: Your police force code (e.g., "btp", "met", "gmp")
   - **Location**: Choose "UK South" for UK forces
3. Click "Review + create"
4. Wait 5-10 minutes for deployment to complete
5. Navigate to your Function App and test the endpoints

### Option 2: PowerShell Script Deployment

1. Clone or download this repository
2. Open PowerShell as Administrator
3. Navigate to the deployment folder:
   ```powershell
   cd "path\to\chatbot-analytics-azure-deploy"
   ```
4. Run the deployment script:
   ```powershell
   .\deploy.ps1 -ForceId "your-force-code" -Location "UK South"
   ```
5. Follow the prompts and wait for completion

### Option 3: GitHub Actions CI/CD

1. Fork this repository to your organization
2. Set up the following secrets in your repository:
   - `AZURE_CREDENTIALS`: Service principal credentials
   - `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID
   - `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`: Function App publish profile
3. Trigger the workflow manually or push changes to main branch

## Post-Deployment Configuration

### 1. Environment Variables
Configure these in your Function App settings:

```
COSMOS_DB_CONNECTION_STRING=<your-cosmos-db-connection>
COSMOS_DB_DATABASE=chatbot-analytics
COSMOS_DB_CONTAINER=analytics-data
```

### 2. Testing Your Deployment

Test each endpoint to ensure everything is working:

```bash
# Test Function
curl "https://func-{your-force}-chatbot-analytics.azurewebsites.net/api/TestFunction?name=Test"

# Analytics Function
curl "https://func-{your-force}-chatbot-analytics.azurewebsites.net/api/GetAnalytics"

# Analytics with parameters
curl "https://func-{your-force}-chatbot-analytics.azurewebsites.net/api/GetAnalytics?category=crime_reporting&startDate=2024-01-01&endDate=2024-01-31"
```

### 3. Monitoring Setup

1. Go to Azure portal → Your Function App → Monitoring
2. Set up Application Insights alerts for:
   - Function failures
   - High response times
   - Unusual traffic patterns
3. Configure email notifications for your team

### 4. Security Configuration

1. **Function Keys**: Use function-level authentication keys
2. **CORS**: Configure allowed origins for your police force domains
3. **IP Restrictions**: Limit access to your police force IP ranges
4. **Managed Identity**: Enable for secure access to other Azure services

## Customization for Your Force

### Resource Naming Convention
Resources are automatically named with your force identifier:
- Resource Group: `rg-{forceId}-chatbot-analytics`
- Function App: `func-{forceId}-chatbot-analytics`
- Storage Account: `st{forceId}{uniqueString}`

### Analytics Data Customization

1. Modify the analytics data structure in `GetAnalytics/__init__.py`
2. Update categories to match your force's incident types
3. Customize metrics based on your KPIs

Example categories for different forces:
```python
# Metropolitan Police
"categories": {
    "violent_crime": {...},
    "theft": {...},
    "traffic_violations": {...},
    "antisocial_behaviour": {...}
}

# British Transport Police
"categories": {
    "fare_evasion": {...},
    "antisocial_behaviour": {...},
    "lost_property": {...},
    "safety_concerns": {...}
}
```

### Cosmos DB Integration

To connect to your existing Cosmos DB:

1. Add connection string to Function App settings
2. Update the analytics functions to use your database schema
3. Modify queries to match your data structure

Example Cosmos DB setup:
```python
from azure.cosmos import CosmosClient

def connect_to_cosmos():
    connection_string = os.environ.get('COSMOS_DB_CONNECTION_STRING')
    client = CosmosClient.from_connection_string(connection_string)
    database = client.get_database_client('chatbot-analytics')
    container = database.get_container_client('analytics-data')
    return container
```

## Scaling for Multiple Forces

### Multi-Tenant Architecture
1. Deploy separate Function Apps per force
2. Use shared Cosmos DB with force-specific containers
3. Implement force-specific configuration

### Cost Optimization
1. Use consumption plan for low-traffic forces
2. Consider premium plan for high-traffic forces
3. Share Application Insights across forces
4. Use single storage account for multiple forces

### Management
1. Use Azure Resource Groups per force
2. Implement Azure Policy for consistent deployment
3. Use Azure DevOps or GitHub Actions for automated deployment
4. Set up centralized monitoring dashboard

## Troubleshooting

### Common Issues

1. **Function not responding**
   - Check Function App logs in Azure portal
   - Verify storage account connection
   - Check Application Insights for errors

2. **Deployment failures**
   - Verify Azure permissions
   - Check resource name uniqueness
   - Review ARM template parameters

3. **Authentication errors**
   - Verify function keys
   - Check CORS settings
   - Review IP restrictions

### Support Contacts

- **Technical Issues**: Contact your Azure support team
- **Deployment Questions**: Review this guide and Azure documentation
- **Customization**: Modify function code as needed for your force

## Maintenance

### Regular Tasks
1. Monitor function performance monthly
2. Review and rotate function keys quarterly
3. Update dependencies annually
4. Test disaster recovery procedures

### Updates
1. Test updates in development environment first
2. Use GitHub Actions for automated testing
3. Deploy to production during maintenance windows
4. Keep backups of working configurations

---

This setup guide provides everything needed to deploy and maintain the chatbot analytics solution for any police force. For specific questions about your deployment, consult the Azure documentation or contact your technical team.
