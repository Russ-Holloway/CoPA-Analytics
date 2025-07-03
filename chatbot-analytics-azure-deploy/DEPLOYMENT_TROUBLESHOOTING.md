# Reliable Auto-Deployment Solution

## Root Cause Analysis
The `WEBSITE_RUN_FROM_PACKAGE` with external GitHub URLs can be unreliable due to:
1. GitHub rate limiting
2. Azure's external URL restrictions
3. Timing issues with package extraction

## Better Solution: Storage Account + Post-Deployment

Let's implement a more reliable approach that:
1. Uploads the ZIP to Azure Storage during deployment
2. Uses the storage blob URL for `WEBSITE_RUN_FROM_PACKAGE`
3. Includes a restart command to ensure functions load

## Implementation Steps

### 1. Update ARM Template
Add these resources to upload ZIP to storage and trigger deployment:

```json
{
    "type": "Microsoft.Storage/storageAccounts/blobServices/containers",
    "apiVersion": "2021-09-01",
    "name": "[concat(variables('storageAccountName'), '/default/deployments')]",
    "dependsOn": [
        "[resourceId('Microsoft.Storage/storageAccounts', variables('storageAccountName'))]"
    ],
    "properties": {
        "publicAccess": "None"
    }
},
{
    "type": "Microsoft.Resources/deploymentScripts",
    "apiVersion": "2020-10-01",
    "name": "upload-function-package",
    "location": "[variables('location')]",
    "dependsOn": [
        "[resourceId('Microsoft.Storage/storageAccounts/blobServices/containers', variables('storageAccountName'), 'default', 'deployments')]"
    ],
    "kind": "AzurePowerShell",
    "identity": {
        "type": "UserAssigned",
        "userAssignedIdentities": {
            "[resourceId('Microsoft.ManagedIdentity/userAssignedIdentities', 'deployment-identity')]": {}
        }
    },
    "properties": {
        "azPowerShellVersion": "8.3",
        "timeout": "PT30M",
        "retentionInterval": "PT1H",
        "scriptContent": "
            # Download ZIP from GitHub and upload to storage
            $zipUrl = 'https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip'
            $tempFile = New-TemporaryFile
            Invoke-WebRequest -Uri $zipUrl -OutFile $tempFile.FullName
            
            # Upload to storage account
            $ctx = New-AzStorageContext -StorageAccountName $storageAccountName -UseConnectedAccount
            Set-AzStorageBlobContent -File $tempFile.FullName -Container 'deployments' -Blob 'function-app.zip' -Context $ctx
            
            # Get blob URL
            $blobUrl = (Get-AzStorageBlob -Container 'deployments' -Blob 'function-app.zip' -Context $ctx).ICloudBlob.StorageUri.PrimaryUri
            Write-Output \"Blob URL: $blobUrl\"
        "
    }
}
```

### 2. Alternative: Direct MSDeploy
Use the MSDeploy extension for more reliable deployment:

```json
{
    "type": "Microsoft.Web/sites/extensions",
    "apiVersion": "2021-02-01",
    "name": "[concat(variables('functionAppName'), '/MSDeploy')]",
    "dependsOn": [
        "[resourceId('Microsoft.Web/sites', variables('functionAppName'))]"
    ],
    "properties": {
        "packageUri": "https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip"
    }
}
```

## Immediate Fix
For now, let's create a PowerShell script that users can run after deployment to ensure functions load.
