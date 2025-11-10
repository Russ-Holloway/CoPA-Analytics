# CSV Data Export Function

The ExportToCSV function allows administrators to extract conversation data from Cosmos DB in CSV format for offline analysis, reporting, or integration with other tools.

## Endpoint

```
GET /api/ExportToCSV
```

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | integer | 30 | Number of days to look back from today |
| `startDate` | string (ISO date) | - | Start date in YYYY-MM-DD format |
| `endDate` | string (ISO date) | - | End date in YYYY-MM-DD format |
| `format` | string | conversations | Export format: 'conversations' or 'messages' |

## Export Formats

### Conversations Format (`format=conversations`)

Exports conversation-level data with the following columns:

- **ID**: Unique conversation identifier
- **Title**: Conversation title/summary
- **Type**: Type of record (conversation)
- **Category**: Category/theme classification
- **User ID**: User identifier
- **Created At**: Timestamp when conversation was created
- **Updated At**: Timestamp when conversation was last updated
- **Message Count**: Number of messages in the conversation
- **Themes**: Comma-separated list of detected themes

**Use case**: High-level analysis of conversation topics, volume trends, and user engagement patterns.

### Messages Format (`format=messages`)

Exports message-level data with the following columns:

- **ID**: Unique message identifier
- **Conversation ID**: Parent conversation identifier
- **Type**: Type of record (message)
- **Role**: Message role (user, assistant, tool)
- **Content Preview**: First 100 characters of message content
- **User ID**: User identifier
- **Created At**: Timestamp when message was created
- **Has Citations**: Whether the message includes citations (Yes/No)

**Use case**: Detailed analysis of conversation flow, response patterns, and citation usage.

## Usage Examples

### Basic Export (Last 30 Days, Conversations)

```
https://func-[your-prefix]-analytics.azurewebsites.net/api/ExportToCSV
```

Downloads a CSV file named: `copa_analytics_[force-id]_conversations_[timestamp].csv`

### Last 7 Days of Conversations

```
https://func-[your-prefix]-analytics.azurewebsites.net/api/ExportToCSV?days=7
```

### Custom Date Range (Conversations)

```
https://func-[your-prefix]-analytics.azurewebsites.net/api/ExportToCSV?startDate=2025-01-01&endDate=2025-01-31
```

### Message-Level Export

```
https://func-[your-prefix]-analytics.azurewebsites.net/api/ExportToCSV?days=7&format=messages
```

### Last Quarter (90 Days)

```
https://func-[your-prefix]-analytics.azurewebsites.net/api/ExportToCSV?days=90&format=conversations
```

## Response

### Success (200 OK)

- **Content-Type**: `text/csv`
- **Content-Disposition**: `attachment; filename="copa_analytics_[force-id]_[format]_[timestamp].csv"`
- **Body**: CSV file content

The browser will automatically download the file.

### Error Responses

#### 400 Bad Request
```json
"Invalid format parameter. Use 'conversations' or 'messages'."
```
or
```json
"Invalid date format. Use YYYY-MM-DD format."
```

#### 500 Internal Server Error
```json
"COSMOS_DB_ENDPOINT or COSMOS_DB_KEY environment variable not set"
```
or
```json
"Error exporting data: [error details]"
```

## Security Considerations

- The function uses the same Cosmos DB connection as other analytics functions
- No authentication is required (anonymous access) - ensure proper network security
- Consider implementing IP whitelisting or Azure AD authentication for production environments
- CSV files contain conversation data - handle according to your data governance policies

## Integration with Other Tools

### Excel/Google Sheets

Simply open the downloaded CSV file in Excel or upload to Google Sheets for analysis.

### Power BI

1. In Power BI Desktop, select **Get Data** → **Web**
2. Enter the ExportToCSV endpoint URL with desired parameters
3. Power BI will download and import the CSV data
4. Set up automatic refresh if needed

### Python/Pandas

```python
import pandas as pd

# Read CSV directly from URL
url = "https://func-[prefix]-analytics.azurewebsites.net/api/ExportToCSV?days=30"
df = pd.read_csv(url)

# Analyze data
print(df.head())
print(df['Category'].value_counts())
```

### R

```r
library(readr)

# Read CSV from URL
url <- "https://func-[prefix]-analytics.azurewebsites.net/api/ExportToCSV?days=30"
data <- read_csv(url)

# Analyze data
summary(data)
```

## Limitations

- Maximum date range: Limited by Cosmos DB query performance (typically 1-2 years of data works well)
- Large exports may take several seconds to process
- CSV file size depends on conversation volume
- Content preview in messages format is truncated to 100 characters

## Troubleshooting

**Export returns empty file:**
- Check date range - ensure there's data in that period
- Verify Cosmos DB connection settings
- Check Function App logs for errors

**Export times out:**
- Reduce the date range (`days` parameter)
- Try exporting in smaller chunks
- Check Cosmos DB RU/s capacity

**Invalid date errors:**
- Ensure dates are in YYYY-MM-DD format
- Start date must be before end date
- Dates should be within reasonable range (not far future)

## Performance Tips

- Use specific date ranges rather than large `days` values
- Use conversations format for overview analysis (smaller files)
- Use messages format only when detailed analysis is needed
- Consider implementing caching for frequently accessed date ranges
