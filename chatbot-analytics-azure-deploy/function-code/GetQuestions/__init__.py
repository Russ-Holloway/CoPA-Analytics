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
    
    # Get Cosmos DB configuration
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
    
    # Query all documents, order by createdAt (matches your Cosmos DB schema)
    query = """
    SELECT TOP @limit * FROM c
    ORDER BY c.createdAt DESC
    """
    parameters = [
        {"name": "@limit", "value": limit}
    ]
    # Execute query
    items = list(container.query_items(
        query=query,
        parameters=parameters,
        enable_cross_partition_query=True
    ))
    # Process and format the questions to match actual Cosmos DB fields
    questions = []
    for item in items:
        question_data = {
            "id": item.get('id'),
            "timestamp": item.get('createdAt', item.get('timestamp', '')),
            "question": item.get('title', 'No question recorded'),
            "category": item.get('type', 'general_enquiry'),
            "theme": item.get('theme', 'unclassified'),
            "userId": item.get('userId', 'anonymous'),
            "satisfaction": item.get('satisfaction', None),
            "resolved": item.get('resolved', False),
            "response_time": item.get('response_time', 0),
            "duration": item.get('duration', 0),
            "session_id": item.get('session_id', None)
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
    }
