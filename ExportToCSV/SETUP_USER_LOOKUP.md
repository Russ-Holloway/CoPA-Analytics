# Setup Guide: Enable User Name Lookup in CSV Exports

The enhanced ExportToCSV function can automatically lookup user names from Microsoft Entra ID (Azure AD) using the Microsoft Graph API. This adds user details to your CSV exports.

## What Gets Added to Exports

### Conversations Format
New columns added:
- **User Name** - Display name (e.g., "John Smith")
- **User Email** - User principal name (e.g., "john.smith@btp.police.uk")
- **User Job Title** - Job title from Entra ID
- **User Department** - Department from Entra ID

### Messages Format
New columns added:
- **User Name** - Display name
- **User Email** - User principal name

## Prerequisites

✅ **You already have:**
- App Registration in Microsoft Entra ID
- `User.Read.All` permission granted and admin consented

## Setup Steps

### Step 1: Get Your App Registration Details

1. **Go to Azure Portal** → **Microsoft Entra ID** → **App registrations**
2. **Find your app registration** (the one with User.Read.All permission)
3. **Note down these values:**
   - **Application (client) ID** - Found on the Overview page
   - **Directory (tenant) ID** - Found on the Overview page
4. **Create a Client Secret** (if you don't have one already):
   - Go to **Certificates & secrets**
   - Click **+ New client secret**
   - Add description: "CoPA Analytics Export"
   - Set expiration (recommended: 24 months)
   - Click **Add**
   - **Copy the secret VALUE immediately** (you won't see it again!)

### Step 2: Add Environment Variables to Function App

**For CoPA Analytics Function App:**

1. **Go to Azure Portal** → Your Function App: `func-coppa-btp-analytics`
2. **Settings** → **Environment variables** (or Configuration)
3. **Click + New application setting** for each of these:

| Name | Value | Description |
|------|-------|-------------|
| `GRAPH_CLIENT_ID` | Your Application (client) ID | From Step 1 |
| `GRAPH_TENANT_ID` | Your Directory (tenant) ID | From Step 1 |
| `GRAPH_CLIENT_SECRET` | Your client secret value | From Step 1 |

4. **Click Save** (important!)
5. **Restart the Function App**:
   - Go to **Overview**
   - Click **Restart**
   - Wait 1-2 minutes

**For Stop & Search Function App:**

Repeat the same steps for: `func-coppa-btp-analytics-g2ys7u`

### Step 3: Test the Enhanced Export

1. **Copy one of your export URLs** (e.g., Last 7 Days)
2. **Paste into browser and download CSV**
3. **Open in Excel**
4. **Verify new columns** are present with user names and emails

Example:
```
https://func-coppa-btp-analytics.azurewebsites.net/api/ExportToCSV?days=7&format=conversations
```

## Expected Results

**Before (without user lookup):**
```csv
User ID
a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**After (with user lookup):**
```csv
User ID,User Name,User Email,User Job Title,User Department
a1b2c3d4-e5f6-7890-abcd-ef1234567890,John Smith,john.smith@btp.police.uk,Police Officer,Operations
```

## Behavior Without Configuration

If the environment variables are **not configured**:
- ✅ Export still works normally
- ❌ User name columns will be empty
- ℹ️ Log message: "Graph API credentials not configured. User lookup disabled."

This ensures backwards compatibility - existing exports continue to work.

## Troubleshooting

### User Names Are Empty

**Check these:**

1. **Environment variables are set correctly**:
   - Go to Function App → Configuration
   - Verify all three variables exist and have values
   - No typos in variable names

2. **App Registration has correct permissions**:
   - Entra ID → App registrations → Your app → API permissions
   - Should show: `User.Read.All` (Application permission)
   - Status should be: **Granted for [Your Organization]** (green checkmark)

3. **Client secret is valid**:
   - Entra ID → App registrations → Your app → Certificates & secrets
   - Check expiration date
   - If expired, create new secret and update `GRAPH_CLIENT_SECRET`

4. **Check Function App logs**:
   - Function App → Monitoring → Log stream
   - Run an export and watch logs
   - Look for:
     - ✅ "Successfully obtained Graph API token for user lookup"
     - ❌ "Failed to obtain Graph API token" (indicates auth issue)

### "Unknown" Appears in User Name Column

This can happen if:
- User ID in database doesn't exist in Entra ID (deleted user)
- User ID format is invalid
- Network timeout when calling Graph API

This is normal for occasional entries and doesn't stop the export.

### Performance Considerations

- User lookup adds **~1-2 seconds per 100 unique users**
- Results are cached during export (each user looked up only once)
- For exports with thousands of users, expect slight delay
- Consider using smaller date ranges if performance is critical

## Security Notes

- ✅ Client secret is stored securely in Azure Function App settings (encrypted)
- ✅ `User.Read.All` permission is read-only (cannot modify users)
- ✅ Token is obtained per-request and not stored
- ✅ Only user display name, email, title, and department are retrieved
- ✅ No sensitive user data (passwords, tokens, etc.) are accessed

## API Rate Limits

Microsoft Graph API has rate limits:
- **Per-app limit**: 2,000 requests per second
- For typical exports (10-500 users), this is not a concern
- Very large exports (5000+ unique users) may take longer

## Advanced: Customize User Fields

If you want to add/remove user fields, edit `/ExportToCSV/__init__.py`:

**Current fields fetched:**
```python
user_cache[user_id] = {
    'displayName': user_data.get('displayName', 'Unknown'),
    'email': user_data.get('userPrincipalName', ''),
    'jobTitle': user_data.get('jobTitle', ''),
    'department': user_data.get('department', '')
}
```

**Available fields from Graph API:**
- `displayName`
- `userPrincipalName`
- `mail`
- `jobTitle`
- `department`
- `officeLocation`
- `mobilePhone`
- `businessPhones`
- `employeeId`

See [Microsoft Graph User documentation](https://learn.microsoft.com/en-us/graph/api/user-get) for full list.

## Cost

- ✅ No additional cost for Graph API calls (included in Microsoft 365/Entra ID)
- ✅ Minimal increase in Function App execution time
- ✅ No additional Azure services required

## Support

If you encounter issues:
1. Check Function App logs (Log stream)
2. Verify App Registration permissions in Entra ID
3. Test Graph API access manually: [Microsoft Graph Explorer](https://developer.microsoft.com/en-us/graph/graph-explorer)
4. Ensure client secret hasn't expired
