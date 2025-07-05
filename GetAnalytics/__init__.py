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
        if category_filter and category_filter != 'all':
            filtered_items = [item for item in filtered_items if (item.get('category') or item.get('type')) == category_filter]
            logging.info(f"GetAnalytics: {len(filtered_items)} items after category filter.")
        items = filtered_items

        total_interactions = len(items)
        unique_users = set()
        total_questions = 0
        categories = Counter()
        themes = Counter()
        hourly_distribution = [0]*24
        recent_questions = []
        response_times = []

        for item in items:
            # Unique users
            user_id = item.get('userId')
            if user_id:
                unique_users.add(user_id)
            # Category
            cat = item.get('category') or item.get('type')
            if cat:
                categories[cat] += 1
                # Themes: use category/type as theme, or add more logic here
                themes[cat] += 1
            # Hourly distribution
            ts = item.get('createdAt') or item.get('timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    hourly_distribution[dt.hour] += 1
                except Exception:
                    pass
            # Average response time (requires both createdAt and respondedAt fields)
            created_at = item.get('createdAt')
            responded_at = item.get('respondedAt')
            if created_at and responded_at:
                try:
                    dt_created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    dt_responded = datetime.fromisoformat(responded_at.replace('Z', '+00:00'))
                    delta = (dt_responded - dt_created).total_seconds()
                    if delta >= 0:
                        response_times.append(delta)
                except Exception:
                    pass
            # Questions
            if item.get('title') or item.get('question'):
                total_questions += 1
                recent_questions.append({
                    'title': item.get('title') or item.get('question'),
                    'category': cat,
                    'userId': user_id,
                    'createdAt': item.get('createdAt'),
                    'updatedAt': item.get('updatedAt'),
                    'type': item.get('type'),
                    'id': item.get('id'),
                })

        # Sort recent questions by createdAt desc
        recent_questions = sorted(recent_questions, key=lambda x: x.get('createdAt') or '', reverse=True)[:20]

        # Top themes (by category/type)
        top_themes = [{'theme': k, 'count': v} for k, v in themes.most_common(5)]

        # Peak usage hour
        peak_hour = hourly_distribution.index(max(hourly_distribution)) if any(hourly_distribution) else None

        # Prepare response
        avg_response_time = round(sum(response_times)/len(response_times), 2) if response_times else None
        data = {
            "summary": {
                "totalInteractions": total_interactions,
                "uniqueUsers": len(unique_users),
                "totalQuestions": total_questions,
                "peakUsageHour": peak_hour,
                "avgResponseTimeSeconds": avg_response_time
            },
            "categories": {k: {"count": v} for k, v in categories.items()},
            "themes": {"top_themes": top_themes},
            "trends": {"hourly_distribution": hourly_distribution},
            "questions": {"recent": recent_questions}
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
