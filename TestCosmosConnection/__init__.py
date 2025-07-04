import logging
import json
import os
import azure.functions as func
from datetime import datetime


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('CosmosDB Connection Test function processed a request.')

    try:
        # Get Cosmos DB configuration from environment variables
        endpoint = os.environ.get('COSMOS_DB_ENDPOINT')
        key = os.environ.get('COSMOS_DB_KEY')
        database_name = os.environ.get('COSMOS_DB_DATABASE', 'db_conversation_history')
        container_name = os.environ.get('COSMOS_DB_CONTAINER', 'conversations')
        force_id = os.environ.get('FORCE_IDENTIFIER', 'unknown')

        # Create test response
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "force_id": force_id,
            "cosmos_config": {
                "endpoint": endpoint if endpoint else "❌ NOT SET",
                "key": "✅ SET" if key else "❌ NOT SET",
                "database": database_name,
                "container": container_name
            },
            "connection_test": "pending",
            "data_count": 0,
            "sample_data": None,
            "error": None
        }

        # Test 1: Check if configuration is present
        if not endpoint or not key:
            test_results["connection_test"] = "❌ FAILED - Missing configuration"
            test_results["error"] = "Cosmos DB endpoint or key not configured"
            return func.HttpResponse(
                json.dumps(test_results, indent=2),
                status_code=200,
                headers={"Content-Type": "application/json"}
            )

        # Test 2: Try to connect to Cosmos DB
        try:
            from azure.cosmos import CosmosClient
            
            client = CosmosClient(endpoint, key)
            database = client.get_database_client(database_name)
            container = database.get_container_client(container_name)
            
            # Test 3: Try to query data
            query = "SELECT TOP 5 * FROM c ORDER BY c._ts DESC"
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            test_results["connection_test"] = "✅ SUCCESS"
            test_results["data_count"] = len(items)
            test_results["sample_data"] = items if items else "No data found"
            
            # Test 4: Check if data exists for this force
            if items:
                force_query = "SELECT COUNT(1) as count FROM c WHERE c.forceId = @force_id"
                force_params = [{"name": "@force_id", "value": force_id}]
                force_count = list(container.query_items(
                    query=force_query,
                    parameters=force_params,
                    enable_cross_partition_query=True
                ))
                test_results["force_data_count"] = force_count[0]["count"] if force_count else 0
            
        except Exception as e:
            test_results["connection_test"] = "❌ FAILED - Connection error"
            test_results["error"] = str(e)
            logging.error(f"Cosmos DB connection error: {str(e)}")

        return func.HttpResponse(
            json.dumps(test_results, indent=2),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        logging.error(f"Error in Cosmos DB test: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Test function error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )
