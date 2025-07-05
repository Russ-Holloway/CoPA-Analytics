import logging
import json
import os
from datetime import datetime, timedelta
import azure.functions as func

try:
    from azure.cosmos import CosmosClient
    cosmos_available = True
except ImportError as e:
    cosmos_available = False
    cosmos_import_error = str(e)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('GetQuestions function processed a request.')

    if not cosmos_available:
        logging.error(f"ImportError: {cosmos_import_error}")
        return func.HttpResponse(
            json.dumps({"error": "azure-cosmos module not installed", "details": cosmos_import_error}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

    try:
        # Get query parameters
        start_date = req.params.get('startDate')
        end_date = req.params.get('endDate')
        category = req.params.get('category', 'all')
        limit = int(req.params.get('limit', 50))  # Default to 50 questions
        force_id = os.environ.get('FORCE_IDENTIFIER', 'unknown')

        # Default to last 7 days if no dates provided
        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
        else:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        # Try to connect to Cosmos DB for real data
        try:
            questions_data = get_detailed_questions(force_id, start_date, end_date, category, limit)
            return func.HttpResponse(
                json.dumps(questions_data, indent=2),
                status_code=200,
                headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            logging.warning(f"Cosmos DB connection failed, returning error: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to query Cosmos DB", "message": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )

    except Exception as e:
        logging.error(f"Error processing GetQuestions request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "message": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

def get_detailed_questions(force_id, start_date, end_date, category, limit):
    from azure.cosmos import CosmosClient

    # Get Cosmos DB configuration
    endpoint = os.environ.get('COSMOS_DB_ENDPOINT')
    key = os.environ.get('COSMOS_DB_KEY')
    database_name = os.environ.get('COSMOS_DB_DATABASE', 'chatbot-analytics')
    container_name = os.environ.get('COSMOS_DB_CONTAINER', 'interactions')

    # Debug logging for diagnostics (do not log key value)
    logging.info(f"Cosmos DB endpoint: {endpoint}")
    logging.info(f"Cosmos DB key length: {len(key) if key else 'None'}")
    logging.info(f"Cosmos DB database: {database_name}")
    logging.info(f"Cosmos DB container: {container_name}")

    if not endpoint or not key:
        raise Exception("Cosmos DB configuration not found")

    # Initialize Cosmos client
    client = CosmosClient(endpoint, key)
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    # Build query based on category filter
    if category != 'all':
        query = """
        SELECT TOP @limit * FROM c 
        WHERE c.forceId = @force_id 
        AND c.timestamp >= @start_date 
        AND c.timestamp <= @end_date
        AND c.category = @category
        ORDER BY c.timestamp DESC
        """
        parameters = [
            {"name": "@force_id", "value": force_id},
            {"name": "@start_date", "value": start_date.isoformat()},
            {"name": "@end_date", "value": end_date.isoformat()},
            {"name": "@category", "value": category},
            {"name": "@limit", "value": limit}
        ]
    else:
        query = """
        SELECT TOP @limit * FROM c 
        WHERE c.forceId = @force_id 
        AND c.timestamp >= @start_date 
        AND c.timestamp <= @end_date
        ORDER BY c.timestamp DESC
        """
        parameters = [
            {"name": "@force_id", "value": force_id},
            {"name": "@start_date", "value": start_date.isoformat()},
            {"name": "@end_date", "value": end_date.isoformat()},
            {"name": "@limit", "value": limit}
        ]

    # Execute query
    items = list(container.query_items(
        query=query,
        parameters=parameters,
        enable_cross_partition_query=True
    ))

    # Process and format the questions to match the real Cosmos DB schema
    questions = []
    for item in items:
        question_data = {
            "id": item.get("id"),
            "type": item.get("type"),
            "createdAt": item.get("createdAt"),
            "updatedAt": item.get("updatedAt"),
            "userId": item.get("userId"),
            "title": item.get("title")
        }
        questions.append(question_data)

    return {
        "questions": questions,
        "count": len(questions)
    }
