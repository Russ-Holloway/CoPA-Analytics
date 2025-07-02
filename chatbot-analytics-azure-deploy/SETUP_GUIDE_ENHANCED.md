# Enhanced Chatbot Analytics Setup Guide

Complete guide for deploying and configuring the Police Force Chatbot Analytics solution with Cosmos DB integration.

## Prerequisites

Before starting, ensure you have:

- **Azure Subscription** with sufficient permissions
- **Azure PowerShell** module installed (`Install-Module -Name Az`)
- **Azure Functions Core Tools** v4 (`npm install -g azure-functions-core-tools@4 --unsafe-perm true`)
- **PowerShell 5.1+** or **PowerShell Core 7+**

## Quick Start (One-Click Deployment)

### Option 1: Deploy to Azure Button

1. Click the "Deploy to Azure" button in the README.md
2. Fill in the parameters:
   - **Force Identifier**: Your police force code (e.g., "btp", "met", "gmp")
   - **Location**: Azure region (recommend "UK South" for UK forces)
3. Wait for deployment to complete (5-10 minutes)
4. Follow post-deployment steps below

### Option 2: Enhanced PowerShell Script

```powershell
# Basic deployment
.\deploy-enhanced.ps1 -ForceId "btp" -Location "UK South"

# With sample data seeding
.\deploy-enhanced.ps1 -ForceId "btp" -Location "UK South" -SeedData

# Production environment
.\deploy-enhanced.ps1 -ForceId "btp" -Location "UK South" -Environment "prod"
```

## What Gets Deployed

### Azure Resources

- ✅ **Resource Group**: `rg-{forceId}-chatbot-{environment}`
- ✅ **Storage Account**: For function app files
- ✅ **Function App**: Python 3.9 runtime with consumption plan
- ✅ **Application Insights**: Monitoring and logging
- ✅ **Cosmos DB Account**: NoSQL database for analytics data
  - Database: `chatbot-analytics`
  - Container: `interactions`
  - Partition key: `/forceId`
  - Free tier enabled (400 RU/s)

### Azure Functions

1. **TestFunction** (HTTP GET)
   - Health check endpoint
   - Tests connectivity and configuration

2. **GetAnalytics** (HTTP GET)
   - Main analytics data retrieval
   - Supports filtering by date range and category
   - Automatic fallback to mock data if Cosmos DB unavailable

3. **TimerTrigger** (Timer)
   - Runs daily at 2 AM UTC
   - Placeholder for scheduled analytics processing

4. **SeedData** (HTTP POST)
   - Seeds Cosmos DB with sample interaction data
   - Generates 30 days of realistic chatbot interactions

## Post-Deployment Configuration

### 1. Verify Deployment

```powershell
# Test the health endpoint
$functionAppUrl = "https://func-{forceId}-chatbot-analytics.azurewebsites.net"
Invoke-RestMethod -Uri "$functionAppUrl/api/TestFunction" -Method Get
```

### 2. Seed Sample Data (Optional)

```powershell
# Add sample data to Cosmos DB
Invoke-RestMethod -Uri "$functionAppUrl/api/SeedData" -Method Post
```

### 3. Test Analytics Endpoint

```powershell
# Get all analytics data
Invoke-RestMethod -Uri "$functionAppUrl/api/GetAnalytics" -Method Get

# Filter by category
Invoke-RestMethod -Uri "$functionAppUrl/api/GetAnalytics?category=crime_reporting" -Method Get

# Specify date range
Invoke-RestMethod -Uri "$functionAppUrl/api/GetAnalytics?startDate=2025-06-01&endDate=2025-06-30" -Method Get
```

## Advanced Configuration

### Environment Variables

The following environment variables are automatically configured:

| Variable | Description | Example |
|----------|-------------|---------|
| `FORCE_IDENTIFIER` | Police force code | `btp` |
| `COSMOS_DB_ENDPOINT` | Cosmos DB endpoint URL | `https://cosmos-btp-*.documents.azure.com:443/` |
| `COSMOS_DB_KEY` | Cosmos DB primary key | `[auto-generated]` |
| `COSMOS_DB_DATABASE` | Database name | `chatbot-analytics` |
| `COSMOS_DB_CONTAINER` | Container name | `interactions` |

### Cosmos DB Data Schema

Sample interaction document:
```json
{
  "id": "unique-interaction-id",
  "forceId": "btp",
  "userId": "user_123",
  "category": "crime_reporting",
  "timestamp": "2025-07-01T10:30:00Z",
  "duration": 180,
  "satisfaction": 4,
  "resolved": true,
  "query_type": "theft",
  "response_time": 1.2,
  "session_id": "session_456"
}
```

## API Documentation

### GET /api/GetAnalytics

Returns analytics data for the specified force and time period.

**Parameters:**
- `startDate` (optional): ISO date string (default: 7 days ago)
- `endDate` (optional): ISO date string (default: now)
- `category` (optional): Filter by interaction category

**Response:**
```json
{
  "forceId": "btp",
  "period": {
    "startDate": "2025-06-24T00:00:00Z",
    "endDate": "2025-07-01T00:00:00Z"
  },
  "summary": {
    "totalInteractions": 1250,
    "uniqueUsers": 340,
    "avgSessionDuration": "4.2 minutes",
    "satisfactionScore": 4.1
  },
  "categories": {
    "crime_reporting": {
      "count": 450,
      "avgResolutionTime": "2.1 minutes",
      "satisfaction": 4.3
    }
  },
  "metadata": {
    "data_source": "cosmos_db",
    "generated_at": "2025-07-01T12:00:00Z",
    "version": "1.0"
  }
}
```

## Monitoring and Troubleshooting

### Application Insights

1. Navigate to your Function App in Azure Portal
2. Click "Application Insights" in the sidebar
3. View:
   - Live metrics
   - Request traces
   - Exception details
   - Performance counters

### Common Issues

#### "cosmos_db_error" in analytics response

**Cause**: Cosmos DB connection failed
**Solutions**:
1. Verify Cosmos DB is deployed and running
2. Check environment variables in Function App configuration
3. Ensure Cosmos DB firewall allows Azure services

#### Function endpoints returning 404

**Cause**: Function code not deployed or failed to start
**Solutions**:
1. Check Function App logs in Azure Portal
2. Redeploy function code:
   ```powershell
   cd function-code
   func azure functionapp publish your-function-app-name --python --build remote
   ```

#### Deployment script fails

**Cause**: Various authentication or permission issues
**Solutions**:
1. Ensure Azure PowerShell module is up to date
2. Verify Azure subscription permissions
3. Check Azure Functions Core Tools installation

## Multi-Tenant Deployment

To deploy for multiple police forces:

```powershell
# Deploy for different forces
$forces = @("btp", "met", "gmp", "wmp")

foreach ($force in $forces) {
    Write-Host "Deploying for $force..."
    .\deploy-enhanced.ps1 -ForceId $force -Location "UK South" -Environment "prod"
}
```

## Security Considerations

1. **API Keys**: Functions use Azure function keys for authentication
2. **Cosmos DB**: Uses managed identity and firewall rules
3. **HTTPS**: All endpoints enforce HTTPS
4. **Data Isolation**: Each force has separate resource groups and data

## Cost Management

- **Function App**: Consumption plan - pay per execution
- **Cosmos DB**: Free tier provides 400 RU/s (suitable for moderate usage)
- **Storage**: Standard LRS for function app files
- **Application Insights**: Pay per data ingestion

Expected monthly cost for typical usage: £10-50 per force.

## Support and Maintenance

### Backup and Recovery

Cosmos DB automatically provides:
- Point-in-time restore (30 days)
- Geo-redundancy (if enabled)
- Automatic failover (if configured)

### Updates and Patches

1. Function runtime updates are automatic
2. Application code updates via deployment script
3. ARM template can be redeployed for infrastructure changes

## Next Steps

1. **Integrate with Chatbot**: Configure your chatbot to send interaction data to Cosmos DB
2. **Custom Analytics**: Extend GetAnalytics function for specific requirements
3. **Dashboards**: Create Power BI or Azure Dashboard visualizations
4. **Alerting**: Set up Application Insights alerts for critical metrics

For additional support or questions, contact the development team.
