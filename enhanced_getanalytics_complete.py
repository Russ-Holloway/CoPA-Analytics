import logging
import json
import os
from datetime import datetime, timedelta
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('GetAnalytics function processed a request.')

    try:
        # Get query parameters
        start_date = req.params.get('startDate')
        end_date = req.params.get('endDate')
        category = req.params.get('category', 'all')
        force_id = os.environ.get('FORCE_IDENTIFIER', 'unknown')

        # Default to last 7 days if no dates provided
        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
        else:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        # Try to connect to Cosmos DB
        cosmos_data = None
        data_source = "mock_data"
        
        try:
            cosmos_data = get_cosmos_analytics(force_id, start_date, end_date, category)
            data_source = "cosmos_db"
        except Exception as e:
            logging.warning(f"Cosmos DB connection failed: {str(e)}")
            data_source = "cosmos_db_error"

        # Use Cosmos DB data if available, otherwise fall back to mock data
        if cosmos_data:
            analytics_data = cosmos_data
        else:
            # Mock analytics data (fallback when Cosmos DB is not available)
            analytics_data = get_mock_analytics_data(force_id, start_date, end_date)

        # Add metadata about data source
        analytics_data["metadata"] = {
            "data_source": data_source,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0"
        }

        # Filter by category if specified
        if category != 'all' and category in analytics_data.get("categories", {}):
            filtered_data = {
                "forceId": analytics_data["forceId"],
                "period": analytics_data["period"],
                "category": category,
                "data": analytics_data["categories"][category],
                "metadata": analytics_data["metadata"]
            }
            return func.HttpResponse(
                json.dumps(filtered_data, indent=2),
                status_code=200,
                headers={"Content-Type": "application/json"}
            )

        return func.HttpResponse(
            json.dumps(analytics_data, indent=2),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        logging.error(f"Error processing analytics request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "message": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


def get_cosmos_analytics(force_id, start_date, end_date, category):
    """Retrieve analytics data from Cosmos DB"""
    from azure.cosmos import CosmosClient
    
    # Get Cosmos DB configuration from environment variables
    endpoint = os.environ.get('COSMOS_DB_ENDPOINT')
    key = os.environ.get('COSMOS_DB_KEY')
    database_name = os.environ.get('COSMOS_DB_DATABASE', 'chatbot-analytics')
    container_name = os.environ.get('COSMOS_DB_CONTAINER', 'interactions')
    
    if not endpoint or not key:
        raise Exception("Cosmos DB configuration not found")
    
    # Initialize Cosmos client
    client = CosmosClient(endpoint, key)
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    
    # Enhanced query to get detailed data
    query = """
    SELECT * FROM c 
    WHERE c.forceId = @force_id 
    AND c.timestamp >= @start_date 
    AND c.timestamp <= @end_date
    ORDER BY c.timestamp DESC
    """
    
    parameters = [
        {"name": "@force_id", "value": force_id},
        {"name": "@start_date", "value": start_date.isoformat()},
        {"name": "@end_date", "value": end_date.isoformat()}
    ]
    
    # Execute query
    items = list(container.query_items(
        query=query,
        parameters=parameters,
        enable_cross_partition_query=True
    ))
    
    # Process results into enhanced analytics format
    return process_cosmos_data_to_enhanced_analytics(items, force_id, start_date, end_date)


def process_cosmos_data_to_enhanced_analytics(items, force_id, start_date, end_date):
    """Process raw Cosmos DB data into enhanced analytics format with detailed insights"""
    from collections import Counter
    import re
    
    total_interactions = len(items)
    unique_users = len(set(item.get('userId', 'anonymous') for item in items))
    
    # Extract detailed question content and themes
    questions = []
    themes = []
    categories = {}
    satisfaction_scores = []
    response_times = []
    resolution_status = []
    hourly_distribution = [0] * 24
    daily_distribution = {}
    
    for item in items:
        # Extract questions/content
        question_text = item.get('question', item.get('query', item.get('content', '')))
        if question_text:
            questions.append({
                "id": item.get('id'),
                "question": question_text,
                "category": item.get('category', 'general_enquiry'),
                "timestamp": item.get('timestamp'),
                "satisfaction": item.get('satisfaction'),
                "resolved": item.get('resolved', False),
                "response_time": item.get('response_time', 0)
            })
        
        # Extract themes/topics
        query_type = item.get('query_type', item.get('topic', ''))
        if query_type:
            themes.append(query_type)
        
        # Category analysis
        cat = item.get('category', 'general_enquiry')
        if cat not in categories:
            categories[cat] = {
                "count": 0,
                "avgResolutionTime": 0,
                "satisfaction": 0.0,
                "resolutionRate": 0.0,
                "questions": []
            }
        categories[cat]["count"] += 1
        categories[cat]["questions"].append(question_text or "No question recorded")
        
        # Satisfaction analysis
        satisfaction = item.get('satisfaction')
        if satisfaction:
            satisfaction_scores.append(satisfaction)
        
        # Response time analysis
        response_time = item.get('response_time', item.get('duration', 0))
        if response_time:
            response_times.append(response_time)
        
        # Resolution analysis
        resolved = item.get('resolved', False)
        resolution_status.append(resolved)
        
        # Time distribution analysis
        timestamp = item.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = dt.hour
                hourly_distribution[hour] += 1
                
                date_key = dt.strftime('%Y-%m-%d')
                daily_distribution[date_key] = daily_distribution.get(date_key, 0) + 1
            except:
                pass
    
    # Calculate advanced metrics
    avg_satisfaction = round(sum(satisfaction_scores) / len(satisfaction_scores), 2) if satisfaction_scores else 0
    avg_response_time = round(sum(response_times) / len(response_times), 2) if response_times else 0
    resolution_rate = round((sum(resolution_status) / len(resolution_status)) * 100, 1) if resolution_status else 0
    
    # Theme analysis
    theme_counts = Counter(themes)
    top_themes = theme_counts.most_common(10)
    
    # Peak hours
    peak_hours = sorted(range(24), key=lambda x: hourly_distribution[x], reverse=True)[:3]
    peak_hours_formatted = [f"{hour:02d}:00" for hour in peak_hours if hourly_distribution[hour] > 0]
    
    # Category processing
    for cat in categories:
        cat_items = [item for item in items if item.get('category') == cat]
        if cat_items:
            cat_satisfaction = [item.get('satisfaction', 0) for item in cat_items if item.get('satisfaction')]
            cat_response_times = [item.get('response_time', 0) for item in cat_items if item.get('response_time')]
            cat_resolved = [item.get('resolved', False) for item in cat_items]
            
            categories[cat]["satisfaction"] = round(sum(cat_satisfaction) / len(cat_satisfaction), 1) if cat_satisfaction else 0
            categories[cat]["avgResolutionTime"] = f"{round(sum(cat_response_times) / len(cat_response_times), 1)} seconds" if cat_response_times else "0 seconds"
            categories[cat]["resolutionRate"] = round((sum(cat_resolved) / len(cat_resolved)) * 100, 1) if cat_resolved else 0
    
    return {
        "forceId": force_id,
        "period": {
            "startDate": start_date.isoformat() if isinstance(start_date, datetime) else start_date,
            "endDate": end_date.isoformat() if isinstance(end_date, datetime) else end_date
        },
        "summary": {
            "totalInteractions": total_interactions,
            "uniqueUsers": unique_users,
            "avgSatisfactionScore": avg_satisfaction,
            "avgResponseTime": f"{avg_response_time} seconds",
            "resolutionRate": f"{resolution_rate}%"
        },
        "categories": categories,
        "questions": {
            "recent": questions[:10],  # Last 10 questions
            "total_count": len(questions)
        },
        "themes": {
            "top_themes": [{"theme": theme, "count": count} for theme, count in top_themes],
            "all_themes": dict(theme_counts)
        },
        "trends": {
            "hourly_distribution": hourly_distribution,
            "daily_distribution": daily_distribution,
            "peak_hours": peak_hours_formatted
        },
        "insights": {
            "busiest_hour": f"{peak_hours[0]:02d}:00" if peak_hours and hourly_distribution[peak_hours[0]] > 0 else "No data",
            "most_common_theme": top_themes[0][0] if top_themes else "No themes found",
            "satisfaction_trend": "High" if avg_satisfaction >= 4 else "Medium" if avg_satisfaction >= 3 else "Low",
            "resolution_performance": "Excellent" if resolution_rate >= 90 else "Good" if resolution_rate >= 70 else "Needs Improvement"
        },
        "performance": {
            "avgResponseTime": f"{avg_response_time} seconds",
            "satisfactionScore": avg_satisfaction,
            "resolutionRate": f"{resolution_rate}%"
        }
    }


def get_mock_analytics_data(force_id, start_date, end_date):
    """Generate mock analytics data as fallback"""
    return {
        "forceId": force_id,
        "period": {
            "startDate": start_date.isoformat() if isinstance(start_date, datetime) else start_date,
            "endDate": end_date.isoformat() if isinstance(end_date, datetime) else end_date
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
            },
            "traffic_incidents": {
                "count": 380,
                "avgResolutionTime": "1.8 minutes",
                "satisfaction": 4.0
            },
            "general_enquiry": {
                "count": 420,
                "avgResolutionTime": "3.2 minutes",
                "satisfaction": 3.9
            }
        },
        "trends": {
            "dailyVolume": [45, 52, 48, 65, 71, 58, 43],
            "peakHours": ["10:00", "14:00", "16:00"],
            "commonTopics": ["lost property", "noise complaints", "parking violations"]
        },
        "performance": {
            "responseTime": "1.2 seconds",
            "uptime": "99.8%",
            "errorRate": "0.2%"
        }
    }
