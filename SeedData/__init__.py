import logging
import json
import os
from datetime import datetime, timedelta
import azure.functions as func
import uuid
import random


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('SeedData function processed a request.')

    try:
        force_id = os.environ.get('FORCE_IDENTIFIER', 'btp')
        
        # Try to connect to Cosmos DB and seed sample data
        try:
            result = seed_cosmos_db(force_id)
            return func.HttpResponse(
                json.dumps(result, indent=2),
                status_code=200,
                headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            logging.error(f"Failed to seed Cosmos DB: {str(e)}")
            return func.HttpResponse(
                json.dumps({
                    "error": "Failed to seed database", 
                    "message": str(e),
                    "cosmos_config": {
                        "endpoint": os.environ.get('COSMOS_DB_ENDPOINT', 'Not configured'),
                        "database": os.environ.get('COSMOS_DB_DATABASE', 'Not configured'),
                        "container": os.environ.get('COSMOS_DB_CONTAINER', 'Not configured')
                    }
                }),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )

    except Exception as e:
        logging.error(f"Error in SeedData function: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "message": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


def seed_cosmos_db(force_id):
    """Seed Cosmos DB with sample chatbot interaction data"""
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
    
    # Generate sample data for the last 30 days
    sample_data = generate_sample_interactions(force_id, days=30)
    
    # Insert sample data
    inserted_count = 0
    for item in sample_data:
        try:
            container.create_item(body=item)
            inserted_count += 1
        except Exception as e:
            logging.warning(f"Failed to insert item: {str(e)}")
    
    return {
        "message": "Database seeding completed",
        "forceId": force_id,
        "items_generated": len(sample_data),
        "items_inserted": inserted_count,
        "database": database_name,
        "container": container_name
    }


def generate_sample_interactions(force_id, days=30):
    """Generate sample chatbot interaction data"""
    interactions = []
    categories = ['crime_reporting', 'traffic_incidents', 'general_enquiry', 'lost_property', 'noise_complaints']
    satisfaction_scores = [3, 4, 4, 4, 5, 5, 5]  # Weighted towards higher scores
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Generate 50-100 interactions per day
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        daily_interactions = random.randint(50, 100)
        
        for _ in range(daily_interactions):
            interaction_id = str(uuid.uuid4())
            user_id = f"user_{random.randint(1, 500)}"  # 500 potential users
            category = random.choice(categories)
            
            # Create realistic timestamps during business hours (8 AM - 6 PM)
            hour = random.randint(8, 18)
            minute = random.randint(0, 59)
            timestamp = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            interaction = {
                "id": interaction_id,
                "forceId": force_id,
                "userId": user_id,
                "category": category,
                "timestamp": timestamp.isoformat(),
                "duration": random.randint(30, 600),  # 30 seconds to 10 minutes
                "satisfaction": random.choice(satisfaction_scores),
                "resolved": random.choice([True, True, True, False]),  # 75% resolution rate
                "query_type": get_query_type_for_category(category),
                "response_time": round(random.uniform(0.5, 3.0), 1),  # 0.5-3 seconds
                "session_id": f"session_{random.randint(1, 1000)}",
                "created_at": timestamp.isoformat()
            }
            
            interactions.append(interaction)
    
    return interactions


def get_query_type_for_category(category):
    """Get realistic query types for each category"""
    query_types = {
        'crime_reporting': ['theft', 'assault', 'vandalism', 'fraud', 'burglary'],
        'traffic_incidents': ['accident', 'speeding', 'parking', 'roadworks', 'breakdown'],
        'general_enquiry': ['hours', 'contact', 'services', 'directions', 'information'],
        'lost_property': ['wallet', 'phone', 'bag', 'keys', 'documents'],
        'noise_complaints': ['music', 'construction', 'traffic', 'neighbors', 'events']
    }
    
    return random.choice(query_types.get(category, ['general']))
