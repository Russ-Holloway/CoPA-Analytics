# Citation Click Tracking - Implementation Summary

## What Was Added

### ✅ Core Feature: Citation Click Tracking
You can now track when users click on citations to verify sources. This directly answers your question: **"Are users checking sources after using CoPA?"**

### ✅ New Azure Function: `TrackCitationClick`
- **Endpoint**: `POST /api/TrackCitationClick`
- **Purpose**: Records citation click events to Cosmos DB
- **Location**: `/TrackCitationClick/`

### ✅ Enhanced Analytics Function
The `GetAnalytics` function now calculates:

#### Primary Metric (Your Request):
- **Citation Check Rate**: % of responses where users clicked at least one citation

#### Additional Engagement Metrics:
- **Avg Messages Per Conversation**: Shows conversation depth
- **Returning User Rate**: % of users who come back
- **Responses With Citations Rate**: Quality indicator for AI responses
- **Avg Conversations Per User**: Shows breadth of usage

### ✅ Updated Dashboard
The dashboard now displays two new rows of metrics:

**Row 2 - Engagement Metrics:**
1. Citation Check Rate (with explanation)
2. Avg Messages Per Conversation
3. Returning User Rate
4. Responses With Citations

**Citation Engagement Insights Section:**
- Visual display of conversations with citation clicks
- Percentage of users checking sources
- Total click statistics across all conversations

## Files Modified

1. **`/TrackCitationClick/__init__.py`** (NEW)
   - Azure Function to track citation clicks
   
2. **`/TrackCitationClick/function.json`** (NEW)
   - Configuration for the tracking function

3. **`/GetAnalytics/__init__.py`** (MODIFIED)
   - Added citation click tracking logic
   - Added engagement metrics calculation
   - Added returning user tracking

4. **`/Dashboard/__init__.py`** (MODIFIED)
   - Added new metric display cards
   - Added citation engagement insights section
   - Updated JavaScript to populate new metrics

5. **`/CITATION_TRACKING_FEATURE.md`** (NEW)
   - Comprehensive documentation

6. **`/ADDITIONAL_METRICS_GUIDE.md`** (NEW)
   - Detailed explanation of all metrics
   - Future metric recommendations

7. **`/TrackCitationClick/INTEGRATION_EXAMPLE.html`** (NEW)
   - Frontend integration examples (JavaScript, React, Vue.js)

## Next Steps to Go Live

### 1. Deploy the New Function
```bash
# Deploy to Azure Functions
func azure functionapp publish <your-function-app-name>
```

### 2. Update Frontend to Track Clicks
Add click tracking to your chat interface wherever citations are displayed:

```javascript
// When user clicks a citation link
async function onCitationClick(citation, conversationId, userId) {
    await fetch('/api/TrackCitationClick', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            conversationId: conversationId,
            citationTitle: citation.title,
            citationUrl: citation.url,
            userId: userId,
            timestamp: new Date().toISOString()
        })
    });
}
```

See `/TrackCitationClick/INTEGRATION_EXAMPLE.html` for complete examples.

### 3. Test the Feature
1. Deploy the functions
2. Update frontend code to track clicks
3. Have a test conversation with citations
4. Click on a citation link
5. Refresh the dashboard - you should see the metrics update

### 4. Monitor the Metrics

Access your dashboard at:
```
https://<your-function-app>.azurewebsites.net/api/Dashboard
```

Key metrics to watch:

- **Citation Check Rate**: Target 20-40% (shows healthy engagement)
- **Returning User Rate**: Target >40% (shows tool value)
- **Avg Messages Per Conversation**: Target 3-8 (shows good interaction)

## Understanding the Citation Check Rate

### What It Tells You:

✅ **10-20%**: Baseline engagement - users occasionally verify sources  
✅ **20-40%**: Healthy engagement - users regularly check sources  
⚠️ **<10%**: Possible issues - citations not visible OR users fully trust responses  
⚠️ **>50%**: High verification - might indicate trust issues OR very diligent users

### What Affects It:

1. **Citation Visibility**: Are citations easy to see and click?
2. **Response Confidence**: Clear answers = less verification needed
3. **User Type**: Law enforcement may verify more than others
4. **Query Complexity**: Complex legal questions = more verification

### How to Improve It:

1. Make citations more prominent in the UI
2. Add "View Sources" button
3. Show citation snippets inline
4. Highlight when response is heavily cited

## Additional Metrics Recommendations

Based on your analytics needs, consider adding these in the future:

### High Priority:
- **Citation Check Rate by Source Type**: Which sources users trust most
- **Session Duration**: How long users spend in the tool
- **Peak Usage by Day of Week**: Staffing and support planning

### Medium Priority:
- **Question Refinement Rate**: How often users rephrase questions
- **New vs Returning User Comparison**: Behavior differences
- **Error Rate**: Reliability monitoring

### Future Enhancements:
- **User Feedback/Ratings**: Direct satisfaction measure
- **Export/Copy Rate**: Shows which answers are most useful
- **Theme Trend Analysis**: Month-over-month topic changes

See `/ADDITIONAL_METRICS_GUIDE.md` for detailed recommendations.

## Troubleshooting

### Citation Clicks Not Being Tracked?

1. **Check function deployment**:
   ```bash
   func azure functionapp list-functions <your-app-name>
   ```
   Look for `TrackCitationClick` in the list

2. **Check frontend integration**:
   - Open browser DevTools Console
   - Click a citation
   - Look for POST request to `/api/TrackCitationClick`

3. **Check function logs**:
   ```bash
   func azure functionapp logstream <your-app-name>
   ```

4. **Verify Cosmos DB**:
   - Check that events with `type: "citation_click"` are being stored
   - Verify container name matches environment variables

### Metrics Showing 0%?

- Need to accumulate data over time
- Ensure frontend is deployed with tracking code
- Check that conversations have citations to click
- Verify date range includes recent activity

## Data Privacy Considerations

The tracking records:
- ✅ Conversation ID (anonymous identifier)
- ✅ Citation title (document name)
- ✅ Citation URL (source link)
- ✅ User ID (your existing user identifier)
- ✅ Timestamp

No sensitive personal data or question content is stored in click events.

## Performance Impact

- **Minimal**: Tracking is asynchronous and non-blocking
- **No user delay**: Tracking happens in background
- **Fail-safe**: If tracking fails, user navigation continues
- **Efficient**: Single small POST request per click

## Questions?

Refer to these documents:
- `/CITATION_TRACKING_FEATURE.md` - Detailed technical documentation
- `/ADDITIONAL_METRICS_GUIDE.md` - Metrics explanations and recommendations
- `/TrackCitationClick/INTEGRATION_EXAMPLE.html` - Frontend code examples

## Success Criteria

You'll know it's working when:

✅ Dashboard shows "Citation Check Rate" > 0%  
✅ "Conversations with Citation Clicks" increases over time  
✅ You can see which % of users are verifying sources  
✅ Metrics help you answer: "Are users trusting but verifying?"  

This gives you data-driven insights into user behavior and trust in the system!
