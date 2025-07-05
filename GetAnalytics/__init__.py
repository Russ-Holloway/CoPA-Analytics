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
        # Cosmos DB connection from environment variable
        COSMOS_CONN_STR = os.environ.get('CosmosDbConnectionString')
        DATABASE_NAME = os.environ.get('CosmosDbDatabaseName', 'coppa-db')
        CONTAINER_NAME = os.environ.get('CosmosDbContainerName', 'questions')
        if not COSMOS_CONN_STR:
            raise Exception('CosmosDbConnectionString environment variable not set')

        client = CosmosClient.from_connection_string(COSMOS_CONN_STR)
        db = client.get_database_client(DATABASE_NAME)
        container = db.get_container_client(CONTAINER_NAME)

        # Query all questions/interactions (customize as needed)
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

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
