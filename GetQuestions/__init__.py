import logging
import json
import os
from datetime import datetime, timedelta
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('GetQuestions function processed a request.')

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

        # Get detailed questions from Cosmos DB
        try:
            questions_data = get_detailed_questions(force_id, start_date, end_date, category, limit)
            
            return func.HttpResponse(
                json.dumps(questions_data, indent=2),
                status_code=200,
                headers={"Content-Type": "application/json"}
            )
            
        except Exception as e:
            logging.error(f"Error retrieving questions: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Failed to retrieve questions", "message": str(e)}),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )

    except Exception as e:
        logging.error(f"Error processing questions request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "message": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


def get_detailed_questions(force_id, start_date, end_date, category, limit):
    """Retrieve detailed questions from Cosmos DB"""
    from azure.cosmos import CosmosClient
    import logging

    endpoint = os.environ.get('COSMOS_DB_ENDPOINT')
    key = os.environ.get('COSMOS_DB_KEY')
    database_name = os.environ.get('COSMOS_DB_DATABASE', 'chatbot-analytics')
    container_name = os.environ.get('COSMOS_DB_CONTAINER', 'conversations')

    if not endpoint or not key:
        raise Exception("Cosmos DB configuration not found")

    client = CosmosClient(endpoint, key)
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    # Query for Conversation type documents (matches your data)
    query = """
    SELECT TOP @limit * FROM c 
    WHERE c.createdAt >= @start_date 
    AND c.createdAt <= @end_date
    AND c.type = 'Conversation'
    ORDER BY c.createdAt DESC
    """
    parameters = [
        {"name": "@start_date", "value": start_date.isoformat()},
        {"name": "@end_date", "value": end_date.isoformat()},
        {"name": "@limit", "value": limit}
    ]

    items = list(container.query_items(
        query=query,
        parameters=parameters,
        enable_cross_partition_query=True
    ))

    questions = []
    for item in items:
        question_data = {
            "id": item.get('id'),
            "timestamp": item.get('createdAt'),
            "question": item.get('title', 'No question recorded'),
            "userId": item.get('userId', 'anonymous'),
            "type": item.get('type', 'Conversation'),
            # "category": item.get('category', 'general_enquiry'),  # Not present in your data
            # "attachments": item.get('attachments', []),           # Not present in your data
            "self": item.get('_self'),
            "etag": item.get('_etag')
        }
        questions.append(question_data)

    return {
        "forceId": force_id,
        "period": {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat()
        },
        "filter": {
            "category": category,
            "limit": limit
        },
        "questions": questions,
        "count": len(questions),
        "metadata": {
            "data_source": "cosmos_db",
            "generated_at": datetime.now().isoformat(),
            "version": "1.0"
        }
    }
    }
