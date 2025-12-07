import azure.functions as func
import logging
import os
import json
from collections import Counter, defaultdict
from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('GetAnalytics function processed a request.')
        # Cosmos DB connection using endpoint and key (align with GetQuestions)
        endpoint = os.environ.get('COSMOS_DB_ENDPOINT')
        key = os.environ.get('COSMOS_DB_KEY')
        database_name = os.environ.get('COSMOS_DB_DATABASE', 'coppa-db')
        container_name = os.environ.get('COSMOS_DB_CONTAINER', 'questions')
        if not endpoint or not key:
            raise Exception('COSMOS_DB_ENDPOINT or COSMOS_DB_KEY environment variable not set')

        # Debug logging for diagnostics (do not log key value)
        logging.info(f"Cosmos DB endpoint: {endpoint}")
        logging.info(f"Cosmos DB key length: {len(key) if key else 'None'}")
        logging.info(f"Cosmos DB database: {database_name}")
        logging.info(f"Cosmos DB container: {container_name}")

        client = CosmosClient(endpoint, key)
        db = client.get_database_client(database_name)
        container = db.get_container_client(container_name)

        # Parse date filters from query params
        from datetime import datetime, timezone
        start_date = req.params.get('startDate')
        end_date = req.params.get('endDate')
        category_filter = req.params.get('category')
        theme_filter = req.params.get('theme')
        date_filter = None
        start_dt = None
        end_dt = None
        if start_date and end_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except Exception as e:
                logging.warning(f"Invalid date filter: {e}")
        # Query all items (filtering in Python for flexibility)
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        logging.info(f"GetAnalytics: Retrieved {len(items)} items from Cosmos DB.")
        if items:
            logging.info(f"GetAnalytics: Sample item: {json.dumps(items[0], indent=2)}")
        # Filter by date and category if provided
        filtered_items = items
        if start_dt and end_dt:
            # Make start_dt and end_dt naive for comparison with naive DB datetimes
            if start_dt.tzinfo is not None:
                start_dt = start_dt.replace(tzinfo=None)
            if end_dt.tzinfo is not None:
                end_dt = end_dt.replace(tzinfo=None)
            def in_range(item):
                ts = item.get('createdAt') or item.get('timestamp')
                if not ts:
                    return False
                try:
                    dt = datetime.fromisoformat(ts)
                    if dt.tzinfo is not None:
                        dt = dt.replace(tzinfo=None)
                    return start_dt <= dt <= end_dt
                except Exception:
                    return False
            filtered_items = [item for item in filtered_items if in_range(item)]
            logging.info(f"GetAnalytics: {len(filtered_items)} items after date filter.")
        if theme_filter and theme_filter != 'all':
            theme_filter_lc = theme_filter.strip().lower()
            def has_theme(item):
                # Match if the theme keyword appears anywhere in the title (case-insensitive substring)
                title = (item.get('title') or '').lower()
                if theme_filter_lc in title:
                    return True
                # Also check in the item's themes list (case-insensitive)
                themes_list = [str(t).strip().lower() for t in item.get('themes', []) if t]
                return any(theme_filter_lc in t for t in themes_list)
            filtered_items = [item for item in filtered_items if has_theme(item)]
            logging.info(f"GetAnalytics: {len(filtered_items)} items after theme filter.")
        elif category_filter and category_filter != 'all':
            filtered_items = [item for item in filtered_items if (item.get('category') or item.get('type')) == category_filter]
            logging.info(f"GetAnalytics: {len(filtered_items)} items after category filter.")
        items = filtered_items

        # Conversation title breakdown (AI-generated overviews, filtered period)
        conversation_title_counter = Counter()
        for item in items:
            if item.get('type') == 'conversation':
                title = (item.get('title') or '').strip()
                if title:
                    conversation_title_counter[title] += 1
        conversation_title_breakdown = [
            {"title": title, "count": count}
            for title, count in conversation_title_counter.most_common(10)
        ]

        # --- All-time totals (before filtering) ---
        # Re-query all items for all-time stats (not filtered)
        all_items = list(container.query_items(query="SELECT * FROM c", enable_cross_partition_query=True))
        all_time_total_questions = sum(1 for item in all_items if item.get('role') == 'user')
        all_time_unique_users = len(set(item.get('userId') for item in all_items if item.get('role') == 'user' and item.get('userId')))

        total_interactions = len(items)
        unique_users = set()
        total_questions = 0
        total_user_questions = sum(1 for item in items if item.get('role') == 'user')
        categories = Counter()
        themes = Counter()
        hourly_distribution = [0]*24
        recent_questions = []
        response_times = []
        # Pre-index all responses by conversationId for fast lookup
        responses_by_conversation = defaultdict(list)
        for item in items:
            if item.get('type') == 'message' and item.get('role') == 'tool' and item.get('conversationId'):
                responses_by_conversation[item['conversationId']].append(item)

        # Theme keywords (expand as needed)
        theme_keywords = [
            'stalking', 'domestic abuse', 'warrant', 'warrants', 'theft', 'burglary', 'assault',
            'missing', 'runaway', 'violence', 'abuse', 'drugs', 'alcohol', 'mental health',
            'child', 'safeguarding', 'investigation', 'arrest', 'bail', 'custody', 'suicide',
            'complaint', 'noise', 'property', 'traffic', 'crime', 'enquiry', 'lost', 'report',
        ]

        # Citation tracking
        citation_sources = defaultdict(lambda: {'count': 0, 'questions': set()})
        unmatched_samples = []  # Store sample unmatched citations for debugging
        citation_categories = {
            'CoP-APP': ['cop-app', 'cop app', 'college of policing', 'authorised professional practice', 'cop-detention', 'cop-general'],
            'Op Soteria-NOM': ['op soteria-nom', 'op soteria', 'opsoteria', 'operation soteria', 'soteria'],
            'NPCC': ['npcc-', 'npcc ', 'national police chiefs', 'gravity-matrix', 'oocr-'],
            'GovUK-CPS': ['govuk-cps-', 'govuk cps', 'cps.gov.uk', 'crown prosecution service', 'cps guidance'],
            'GovUK-Legislation': ['govuk-legislation', 'legislation.gov.uk'],
            'GovUK-HO': ['govuk-ho-', 'govuk ho', 'home office guidance', 'notifiable-offence'],
            'GovUK-MoJ': ['govuk-moj-', 'govuk moj', 'ministry of justice', 'cautions-guidance'],
            'RCJ': ['rcj-', 'royal courts of justice'],
            'VKPP': ['vkpp-', 'victims\' commissioner', 'victims commissioner'],
            'Sentencing Council': ['sent-coun-', 'sentencing council', 'sentencing guidelines'],
            'BTP-Policy': ['btp-pol', 'btp-policy', 'btp policy', 'btp-', 'british transport police'],
            'Stop & Search': ['stop and search', 'stop & search', 'stop search'],
            'PACE': ['pace-', 'police and criminal evidence act'],
            'SCRS': ['scrs ', 'scrs crime manual', 'scotland'],
            'Other Documents': [],  # Catch-all for unmatched citations
        }
        
        # Citation click tracking
        citation_clicks = set()  # Track unique conversations with citation clicks
        total_citation_clicks = 0
        conversations_with_citations = set()
        
        # Conversation metrics
        conversation_message_counts = defaultdict(int)
        user_conversation_count = defaultdict(int)
        returning_users = set()
        user_first_seen = {}
        conversations_with_responses = set()

        for item in items:
            item_type = item.get('type')
            
            # Track citation clicks
            if item_type == 'citation_click':
                conv_id = item.get('conversationId')
                if conv_id:
                    citation_clicks.add(conv_id)
                    total_citation_clicks += 1
            
            # Track conversation message counts
            if item_type == 'message':
                conv_id = item.get('conversationId')
                if conv_id:
                    conversation_message_counts[conv_id] += 1
            
            # Track returning users
            user_id = item.get('userId')
            if user_id:
                unique_users.add(user_id)
                ts = item.get('createdAt') or item.get('timestamp')
                if ts:
                    try:
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        if user_id not in user_first_seen:
                            user_first_seen[user_id] = dt
                        else:
                            # If we've seen this user before in a different period, they're returning
                            time_diff = (dt - user_first_seen[user_id]).days
                            if time_diff > 0:
                                returning_users.add(user_id)
                    except Exception:
                        pass
            
            # Count conversations per user
            if item_type == 'conversation':
                if user_id:
                    user_conversation_count[user_id] += 1
            
            # Category
            cat = item.get('category') or item_type
            if cat:
                categories[cat] += 1
            
            # Hourly distribution
            ts = item.get('createdAt') or item.get('timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    hourly_distribution[dt.hour] += 1
                except Exception:
                    pass
            
            # Extract citations from tool messages
            if item.get('role') == 'tool':
                conv_id = item.get('conversationId')
                if conv_id:
                    conversations_with_responses.add(conv_id)
                try:
                    content = item.get('content', '')
                    tool_data = json.loads(content) if isinstance(content, str) else content
                    citations = tool_data.get('citations') if isinstance(tool_data, dict) else None
                    if citations and isinstance(citations, list):
                        # Track conversations that have citations
                        if conv_id:
                            conversations_with_citations.add(conv_id)
                        
                        # Track total citations processed for logging
                        total_citations_processed = sum(src['count'] for src in citation_sources.values())
                        
                        for citation in citations:
                            title = citation.get('title', '').lower()
                            # Log first 50 citation titles for debugging to understand patterns
                            if total_citations_processed < 50:
                                logging.info(f"Citation title: {title}")
                            
                            # Categorize citation by source
                            matched = False
                            for source_name, keywords in citation_categories.items():
                                if source_name == 'Other Documents':
                                    continue  # Skip "Other Documents" in the loop
                                if keywords and any(keyword in title for keyword in keywords):
                                    citation_sources[source_name]['count'] += 1
                                    if conv_id:
                                        citation_sources[source_name]['questions'].add(conv_id)
                                    matched = True
                                    break
                            # If no category matched, categorize as "Other Documents"
                            if not matched:
                                citation_sources['Other Documents']['count'] += 1
                                if conv_id:
                                    citation_sources['Other Documents']['questions'].add(conv_id)
                                # Log unmatched citations to help identify new patterns
                                if total_citations_processed < 50:
                                    logging.warning(f"Unmatched citation: {title}")
                                # Store first 20 unmatched samples for API response
                                if len(unmatched_samples) < 20:
                                    unmatched_samples.append(title)
                                
                            total_citations_processed += 1
                except Exception as e:
                    logging.warning(f"Error parsing citations: {e}")
                    pass
            
            # Questions (user questions)
            if item.get('type') == 'conversation' and (item.get('title') or item.get('question')):
                total_questions += 1
                qid = item.get('id')
                # Find first AI response for this question
                resp_time = None
                if qid and qid in responses_by_conversation:
                    # Sort responses by createdAt
                    responses = sorted(responses_by_conversation[qid], key=lambda r: r.get('createdAt') or '')
                    if responses:
                        try:
                            dt_q = datetime.fromisoformat(item['createdAt'].replace('Z', '+00:00'))
                            dt_r = datetime.fromisoformat(responses[0]['createdAt'].replace('Z', '+00:00'))
                            delta = (dt_r - dt_q).total_seconds()
                            if delta >= 0:
                                response_times.append(delta)
                                resp_time = delta
                        except Exception:
                            pass
                # Theme extraction from title
                title = (item.get('title') or '').lower()
                found_themes = [kw for kw in theme_keywords if kw in title]
                for theme in found_themes:
                    themes[theme] += 1
                recent_questions.append({
                    'title': item.get('title') or item.get('question'),
                    'category': cat,
                    'userId': user_id,
                    'createdAt': item.get('createdAt'),
                    'updatedAt': item.get('updatedAt'),
                    'type': item.get('type'),
                    'id': item.get('id'),
                    'themes': found_themes,
                    'responseTimeSeconds': resp_time,
                })

        # Sort recent questions by createdAt desc
        recent_questions = sorted(recent_questions, key=lambda x: x.get('createdAt') or '', reverse=True)[:20]


        # Conversation themes breakdown (group conversations by theme)
        # Only consider 'conversation' type items
        conversation_theme_counter = Counter()
        for item in items:
            if item.get('type') == 'conversation':
                conv_themes = item.get('themes', [])
                # If themes not present, try to extract from title
                if not conv_themes:
                    title = (item.get('title') or '').lower()
                    conv_themes = [kw for kw in theme_keywords if kw in title]
                for theme in conv_themes:
                    conversation_theme_counter[theme] += 1

        conversation_themes_breakdown = [
            {"theme": theme, "count": count}
            for theme, count in conversation_theme_counter.most_common()
        ]

        # Top themes (by category/type)
        top_themes = [{'theme': k, 'count': v} for k, v in themes.most_common(5)]

        # Peak usage hour
        peak_hour = hourly_distribution.index(max(hourly_distribution)) if any(hourly_distribution) else None

        # Calculate additional metrics
        avg_response_time = round(sum(response_times)/len(response_times), 2) if response_times else None
        
        # Citation engagement metrics
        conversations_with_citations_count = len(conversations_with_citations)
        conversations_with_clicks_count = len(citation_clicks)
        citation_engagement_rate = round((conversations_with_clicks_count / conversations_with_citations_count * 100), 1) if conversations_with_citations_count > 0 else 0
        
        # Conversation length metrics
        avg_messages_per_conversation = round(sum(conversation_message_counts.values()) / len(conversation_message_counts), 1) if conversation_message_counts else 0
        
        # User engagement metrics
        avg_conversations_per_user = round(sum(user_conversation_count.values()) / len(user_conversation_count), 1) if user_conversation_count else 0
        returning_user_rate = round((len(returning_users) / len(unique_users) * 100), 1) if len(unique_users) > 0 else 0
        
        # Response quality metrics
        responses_with_citations_rate = round((conversations_with_citations_count / len(conversations_with_responses) * 100), 1) if conversations_with_responses else 0
        
        # Format citations data for response
        total_citations = sum(data['count'] for data in citation_sources.values())
        citations_breakdown = [
            {
                "source": source_name,
                "totalCitations": data['count'],
                "questionsCount": len(data['questions']),
                "percentage": round((data['count'] / total_citations * 100), 1) if total_citations > 0 else 0,
                "avgPerQuestion": round(data['count'] / len(data['questions']), 1) if len(data['questions']) > 0 else 0
            }
            for source_name, data in sorted(citation_sources.items(), key=lambda x: x[1]['count'], reverse=True)
        ]
        
        data = {
            "summary": {
                "totalInteractions": total_interactions,
                "uniqueUsers": len(unique_users),
                "totalQuestions": total_questions,
                "totalUserQuestions": total_user_questions,
                "peakUsageHour": peak_hour,
                "avgResponseTimeSeconds": avg_response_time,
                "avgMessagesPerConversation": avg_messages_per_conversation,
                "avgConversationsPerUser": avg_conversations_per_user,
                "returningUserRate": returning_user_rate
            },
            "categories": {k: {"count": v} for k, v in categories.items()},
            "themes": {"top_themes": top_themes},
            "conversationThemesBreakdown": conversation_themes_breakdown,
            "conversationTitleBreakdown": conversation_title_breakdown,
            "trends": {"hourly_distribution": hourly_distribution},
            "questions": {"recent": recent_questions},
            "citations": {
                "breakdown": citations_breakdown,
                "totalCitations": sum(c['totalCitations'] for c in citations_breakdown),
                "totalQuestionsWithCitations": len(set().union(*[data['questions'] for data in citation_sources.values()])) if citation_sources else 0,
                "unmatchedSamples": unmatched_samples,  # Debug: show sample unmatched citations
                "conversationsWithCitations": conversations_with_citations_count,
                "conversationsWithClicks": conversations_with_clicks_count,
                "citationEngagementRate": citation_engagement_rate,
                "totalCitationClicks": total_citation_clicks,
                "responsesWithCitationsRate": responses_with_citations_rate
            },
            # --- Engagement metrics ---
            "engagement": {
                "avgMessagesPerConversation": avg_messages_per_conversation,
                "avgConversationsPerUser": avg_conversations_per_user,
                "returningUserRate": returning_user_rate,
                "totalReturningUsers": len(returning_users),
                "citationCheckRate": citation_engagement_rate
            },
            # --- NEW FIELD: allTime ---
            "allTime": {
                "totalQuestions": all_time_total_questions,
                "uniqueUsers": all_time_unique_users
            }
        }
        return func.HttpResponse(
            json.dumps(data),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"GetAnalytics error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
