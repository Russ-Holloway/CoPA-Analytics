# Citation Click Tracking Feature

## Overview
This feature tracks when users click on citations in responses, providing insights into whether users are verifying sources after receiving answers from CoPA.

## New Components

### 1. TrackCitationClick Function
**Location**: `/TrackCitationClick/`

**Purpose**: Records citation click events to Cosmos DB

**API Endpoint**: `POST /api/TrackCitationClick`

**Request Body**:
```json
{
  "conversationId": "string",
  "citationTitle": "string",
  "citationUrl": "string (optional)",
  "userId": "string (optional)",
  "timestamp": "ISO datetime string (optional)"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Citation click tracked"
}
```

### 2. Enhanced Analytics

The `GetAnalytics` function now calculates:

#### Citation Engagement Metrics
- **Citation Check Rate**: % of responses where users clicked at least one citation
- **Total Citation Clicks**: Total number of citation link clicks
- **Conversations with Clicks**: Number of unique conversations where citations were clicked

#### User Engagement Metrics
- **Avg Messages Per Conversation**: Average conversation length
- **Avg Conversations Per User**: How many conversations each user typically has
- **Returning User Rate**: % of users who return after their first visit
- **Responses With Citations Rate**: % of AI responses that include citations

### 3. Updated Dashboard

The dashboard now displays:

#### New Metric Cards (Row 2)
1. **Citation Check Rate** - Shows engagement with sources
2. **Avg Messages Per Conversation** - Indicates conversation depth
3. **Returning User Rate** - Shows user retention
4. **Responses With Citations** - Quality indicator

#### Citation Engagement Insights Section
- Visual display of conversations with citation clicks
- Percentage of users checking sources
- Total click statistics

## Integration Instructions

### For Frontend/Chat Application

To track citation clicks, add an onclick handler to citation links:

```javascript
// When rendering a citation link
function renderCitation(citation, conversationId, userId) {
  const link = document.createElement('a');
  link.href = citation.url;
  link.textContent = citation.title;
  link.target = '_blank';
  
  // Track click event
  link.addEventListener('click', async () => {
    try {
      await fetch('/api/TrackCitationClick', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          conversationId: conversationId,
          citationTitle: citation.title,
          citationUrl: citation.url,
          userId: userId,
          timestamp: new Date().toISOString()
        })
      });
    } catch (error) {
      console.error('Failed to track citation click:', error);
    }
  });
  
  return link;
}
```

### Data Structure

Citation click events are stored in Cosmos DB with this structure:

```json
{
  "id": "citation-click-{conversationId}-{timestamp}",
  "type": "citation_click",
  "conversationId": "conversation-123",
  "citationTitle": "College of Policing - Arrest Guidance",
  "citationUrl": "https://...",
  "userId": "user-456",
  "timestamp": "2025-12-07T10:30:00Z",
  "createdAt": "2025-12-07T10:30:00Z"
}
```

## Additional Metrics Explained

### Why These Metrics Matter

1. **Citation Check Rate (Primary Request)**
   - **What it shows**: The percentage of AI responses where users clicked at least one citation
   - **Why it matters**: Indicates users are fact-checking and verifying information
   - **Ideal range**: 20-40% (shows engaged users without indicating distrust)

2. **Avg Messages Per Conversation**
   - **What it shows**: How long conversations typically last
   - **Why it matters**: Longer conversations suggest complex queries and good engagement
   - **Ideal range**: 3-8 messages (shows back-and-forth interaction)

3. **Returning User Rate**
   - **What it shows**: Percentage of users who come back after first use
   - **Why it matters**: Indicates the tool provides value and builds trust
   - **Ideal range**: 40-60% (high retention shows value)

4. **Responses With Citations Rate**
   - **What it shows**: How often AI responses include source citations
   - **Why it matters**: Higher rates indicate comprehensive, well-sourced answers
   - **Ideal range**: 70-90% (most answers should have sources)

5. **Avg Conversations Per User**
   - **What it shows**: How many separate conversations each user initiates
   - **Why it matters**: Shows tool is being used for multiple use cases
   - **Ideal range**: 2-5 conversations per user

## Viewing the Dashboard

Access the dashboard at: `https://your-function-app.azurewebsites.net/api/Dashboard`

The dashboard automatically updates every time you change the date range or theme filter.

## Testing

To test the citation click tracking:

1. Deploy the new `TrackCitationClick` function
2. Update your frontend to call the tracking endpoint when citations are clicked
3. Generate some test conversations with citations
4. Click on citation links
5. Refresh the dashboard to see the metrics update

## Troubleshooting

If citation clicks aren't being tracked:

1. Check that the `TrackCitationClick` function is deployed
2. Verify the frontend is calling the endpoint correctly
3. Check function logs for errors: `func logs TrackCitationClick`
4. Ensure Cosmos DB connection settings are correct
5. Verify the citation click events are being stored with `type: "citation_click"`
