# Secondary CoPPA Analytics Deployment Guide

This guide shows you how to deploy the CoPPA Analytics solution and configure it to work with a different Cosmos database by simply changing environment variables.

## Overview

This is the simplest approach - deploy the solution as normal, then update the environment variables to point to your secondary Cosmos database. Everything else remains the same.

## Step 1: Deploy the Solution

1. **Click the "Deploy to Azure" button** in the main README.md
2. **Fill in the deployment form** with your details:
   - **Force Prefix**: Use a different prefix (e.g., "BTP-SEC" instead of "BTP")
   - **Admin Email**: Your email for reports
   - **Cosmos DB fields**: You can leave these blank initially or enter your secondary database details now
   - **Other settings**: Configure as needed

3. **Deploy**: Click "Review + create" then "Create"
4. **Wait for deployment**: Usually takes 5-10 minutes
5. **Note the unique resource names**: The deployment will automatically add a unique 6-character suffix to all resource names to avoid conflicts (e.g., `func-coppa-btp-analytics-a1b2c3`)

## Important: Unique Resource Naming

The ARM template now automatically adds a unique suffix to all resource names:
- **Function App**: `func-coppa-[prefix]-analytics-[unique-suffix]`
- **App Service Plan**: `plan-coppa-[prefix]-analytics-[unique-suffix]`
- **Application Insights**: `appi-coppa-[prefix]-analytics-[unique-suffix]`

This ensures you can deploy multiple instances without naming conflicts, even with the same force prefix.

## Step 2: Update Environment Variables

After deployment completes:

1. **Go to Azure Portal** → Navigate to your new Function App
2. **Open Settings** → Click "Environment variables" 
3. **Update the Cosmos DB settings**:

   | Variable Name | New Value | Example |
   |---------------|-----------|---------|
   | `COSMOS_DB_ENDPOINT` | Your secondary Cosmos DB endpoint | `https://your-secondary-cosmos.documents.azure.com:443/` |
   | `COSMOS_DB_KEY` | Your secondary Cosmos DB key | `[your-secondary-key]` |
   | `COSMOS_DB_DATABASE` | Your secondary database name | `db_conversation_history` |
   | `COSMOS_DB_CONTAINER` | Your secondary container name | `conversations` |

4. **Save the changes**
5. **Restart the Function App**:
   - Go to "Overview" tab
   - Click "Restart"
   - Wait for restart to complete

## Step 3: Test the Secondary Configuration

Test that your analytics solution is now reading from the secondary database:

```bash
# Replace with your actual Function App URL (check deployment outputs for exact URL)
FUNCTION_URL="https://func-coppa-[your-prefix]-analytics-[unique-suffix].azurewebsites.net"

# Test basic function
curl "$FUNCTION_URL/api/TestFunction"

# Test analytics - should show data from your secondary Cosmos DB
curl "$FUNCTION_URL/api/GetAnalytics?days=7"

# View dashboard - should display analytics from secondary database
curl "$FUNCTION_URL/api/Dashboard"
```

**Finding Your Function App URL**: After deployment, check the ARM template outputs in the Azure Portal for the exact URL with the unique suffix.

## Step 4: Verify Data Source

You can verify which database you're connected to by checking the debug endpoint:

```bash
curl "$FUNCTION_URL/api/DebugEnvironment"
```

This will show you the current environment variables and confirm your Cosmos DB configuration.

## Multiple Deployments

You can now deploy multiple analytics instances easily:

1. **Use the same or different Force Prefix** - the unique suffix ensures no conflicts
2. **Deploy to the same or different resource groups**
3. **Configure each deployment** to point to its respective Cosmos database

Example deployments:
- Primary: `BTP` → `func-coppa-btp-analytics-a1b2c3`
- Secondary: `BTP` → `func-coppa-btp-analytics-d4e5f6` (different unique suffix)
- Test: `BTP-TEST` → `func-coppa-btp-test-analytics-g7h8i9`

The deployment outputs will show you the exact URLs for each deployment.

## Environment Variable Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `COSMOS_DB_ENDPOINT` | Cosmos DB endpoint URL | Yes | `https://cosmos-account.documents.azure.com:443/` |
| `COSMOS_DB_KEY` | Primary or secondary key | Yes | `[64-character key]` |
| `COSMOS_DB_DATABASE` | Database name | Yes | `db_conversation_history` |
| `COSMOS_DB_CONTAINER` | Container name | Yes | `conversations` |
| `FORCE_IDENTIFIER` | Police force code | Yes | `BTP` |
| `ADMIN_EMAIL` | Email for reports | Yes | `admin@force.police.uk` |

## Troubleshooting

### "Cannot connect to Cosmos DB"
- Verify the endpoint URL is correct
- Check that the key has read permissions
- Ensure Cosmos DB firewall allows Azure services

### "No data returned"
- Check that the database and container names are correct
- Verify that the container contains data in the expected format
- Use the DebugEnvironment endpoint to check configuration

### Function not responding
- Check Function App logs in Azure Portal
- Verify the Function App has restarted after environment variable changes
- Check Application Insights for detailed error messages

## Cost Considerations

Each deployment creates:
- Function App (consumption plan - pay per use)
- Storage Account (minimal cost)
- Application Insights (small data retention cost)

The main cost is typically the Function App execution time, which is minimal for analytics queries.

## Benefits of This Approach

✅ **Simple**: Just change environment variables  
✅ **Quick**: No code changes required  
✅ **Flexible**: Easy to switch between databases  
✅ **Cost-effective**: Separate analytics without duplicating code  
✅ **Independent**: Each deployment can be managed separately  

## Next Steps

After deployment and configuration:

1. **Set up monitoring alerts** in Application Insights
2. **Configure email reports** if needed
3. **Test the dashboard** and API endpoints
4. **Document your endpoint URLs** for your team

Your secondary analytics deployment is now ready and reading from your secondary Cosmos database!
