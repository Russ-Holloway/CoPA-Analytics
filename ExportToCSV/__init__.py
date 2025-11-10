import azure.functions as func
import logging
import os
import csv
import io
from datetime import datetime, timedelta
from azure.cosmos import CosmosClient
import requests
import msal

def get_user_details(user_ids, access_token):
    """
    Fetch user details from Microsoft Graph API for a list of user IDs.
    Returns a dictionary mapping user ID to user details.
    """
    user_cache = {}
    
    if not user_ids or not access_token:
        return user_cache
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Batch lookup users (Graph API supports batch requests)
    for user_id in user_ids:
        if not user_id or user_id in user_cache:
            continue
            
        try:
            # Query Graph API for user details
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                user_data = response.json()
                user_cache[user_id] = {
                    'displayName': user_data.get('displayName', 'Unknown'),
                    'email': user_data.get('userPrincipalName', ''),
                    'jobTitle': user_data.get('jobTitle', ''),
                    'department': user_data.get('department', '')
                }
                logging.info(f"Retrieved user details for: {user_id}")
            else:
                logging.warning(f"Could not fetch user {user_id}: {response.status_code}")
                user_cache[user_id] = {
                    'displayName': 'Unknown',
                    'email': '',
                    'jobTitle': '',
                    'department': ''
                }
        except Exception as e:
            logging.error(f"Error fetching user {user_id}: {str(e)}")
            user_cache[user_id] = {
                'displayName': 'Unknown',
                'email': '',
                'jobTitle': '',
                'department': ''
            }
    
    return user_cache

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Export conversation data from Cosmos DB to CSV format.
    Includes automatic user name lookup from Microsoft Entra ID via Graph API.
    
    Query Parameters:
    - days: Number of days to look back (default: 30)
    - startDate: Start date in ISO format (YYYY-MM-DD)
    - endDate: End date in ISO format (YYYY-MM-DD)
    - format: 'conversations' or 'messages' (default: 'conversations')
    """
    try:
        logging.info('ExportToCSV function processed a request.')
        
        # Get parameters
        days_param = req.params.get('days', '30')
        start_date = req.params.get('startDate')
        end_date = req.params.get('endDate')
        export_format = req.params.get('format', 'conversations')
        
        # Validate format
        if export_format not in ['conversations', 'messages']:
            return func.HttpResponse(
                "Invalid format parameter. Use 'conversations' or 'messages'.",
                status_code=400
            )
        
        # Connect to Cosmos DB
        endpoint = os.environ.get('COSMOS_DB_ENDPOINT')
        key = os.environ.get('COSMOS_DB_KEY')
        database_name = os.environ.get('COSMOS_DB_DATABASE', 'coppa-db')
        container_name = os.environ.get('COSMOS_DB_CONTAINER', 'questions')
        
        if not endpoint or not key:
            return func.HttpResponse(
                "COSMOS_DB_ENDPOINT or COSMOS_DB_KEY environment variable not set",
                status_code=500
            )
        
        logging.info(f"Connecting to Cosmos DB: {database_name}/{container_name}")
        client = CosmosClient(endpoint, key)
        db = client.get_database_client(database_name)
        container = db.get_container_client(container_name)
        
        # Calculate date range
        if start_date and end_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                end_dt = datetime.fromisoformat(end_date)
            except ValueError:
                return func.HttpResponse(
                    "Invalid date format. Use YYYY-MM-DD format.",
                    status_code=400
                )
        else:
            try:
                days = int(days_param)
                end_dt = datetime.utcnow()
                start_dt = end_dt - timedelta(days=days)
            except ValueError:
                return func.HttpResponse(
                    "Invalid days parameter. Must be an integer.",
                    status_code=400
                )
        
        # Query all items
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        logging.info(f"Retrieved {len(items)} total items from Cosmos DB.")
        
        # Filter by date range
        def in_range(item):
            ts = item.get('createdAt') or item.get('timestamp')
            if not ts:
                return False
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                return start_dt <= dt <= end_dt
            except Exception:
                return False
        
        filtered_items = [item for item in items if in_range(item)]
        logging.info(f"Filtered to {len(filtered_items)} items in date range.")
        
        # Get Microsoft Graph API access token for user lookup
        graph_client_id = os.environ.get('GRAPH_CLIENT_ID')
        graph_tenant_id = os.environ.get('GRAPH_TENANT_ID')
        graph_client_secret = os.environ.get('GRAPH_CLIENT_SECRET')
        
        access_token = None
        user_lookup_enabled = False
        
        if graph_client_id and graph_tenant_id and graph_client_secret:
            try:
                authority = f"https://login.microsoftonline.com/{graph_tenant_id}"
                app = msal.ConfidentialClientApplication(
                    graph_client_id,
                    authority=authority,
                    client_credential=graph_client_secret
                )
                scopes = ["https://graph.microsoft.com/.default"]
                result = app.acquire_token_for_client(scopes=scopes)
                
                if "access_token" in result:
                    access_token = result["access_token"]
                    user_lookup_enabled = True
                    logging.info("Successfully obtained Graph API token for user lookup.")
                else:
                    logging.warning(f"Failed to obtain Graph API token: {result.get('error_description')}")
            except Exception as e:
                logging.warning(f"Graph API authentication failed: {str(e)}. Proceeding without user lookup.")
        else:
            logging.info("Graph API credentials not configured. User lookup disabled.")
        
        # Collect unique user IDs for lookup
        unique_user_ids = set()
        for item in filtered_items:
            user_id = item.get('userId')
            if user_id:
                unique_user_ids.add(user_id)
        
        # Fetch user details if enabled
        user_details = {}
        if user_lookup_enabled and unique_user_ids:
            logging.info(f"Looking up {len(unique_user_ids)} unique users from Entra ID...")
            user_details = get_user_details(unique_user_ids, access_token)
            logging.info(f"Successfully retrieved details for {len(user_details)} users.")
        
        # Create CSV in memory
        output = io.StringIO()
        
        if export_format == 'conversations':
            # Export conversation-level data
            csv_writer = csv.writer(output)
            csv_writer.writerow([
                'ID',
                'Title',
                'Type',
                'Category',
                'User ID',
                'User Name',
                'User Email',
                'User Job Title',
                'User Department',
                'Created At',
                'Updated At',
                'Message Count',
                'Themes'
            ])
            
            # Group by conversation
            conversations = {}
            for item in filtered_items:
                if item.get('type') == 'conversation':
                    conv_id = item.get('id')
                    conversations[conv_id] = {
                        'id': conv_id,
                        'title': item.get('title', ''),
                        'type': item.get('type', ''),
                        'category': item.get('category', ''),
                        'userId': item.get('userId', ''),
                        'createdAt': item.get('createdAt', ''),
                        'updatedAt': item.get('updatedAt', ''),
                        'messageCount': 0,
                        'themes': ', '.join(item.get('themes', []))
                    }
                
                # Count messages per conversation
                conv_id = item.get('conversationId')
                if conv_id and conv_id in conversations:
                    conversations[conv_id]['messageCount'] += 1
            
            for conv in conversations.values():
                user_id = conv['userId']
                user_info = user_details.get(user_id, {})
                
                csv_writer.writerow([
                    conv['id'],
                    conv['title'],
                    conv['type'],
                    conv['category'],
                    user_id,
                    user_info.get('displayName', ''),
                    user_info.get('email', ''),
                    user_info.get('jobTitle', ''),
                    user_info.get('department', ''),
                    conv['createdAt'],
                    conv['updatedAt'],
                    conv['messageCount'],
                    conv['themes']
                ])
            
            logging.info(f"Exported {len(conversations)} conversations to CSV.")
        
        else:  # messages format
            # Export message-level data
            csv_writer = csv.writer(output)
            csv_writer.writerow([
                'ID',
                'Conversation ID',
                'Type',
                'Role',
                'Content Preview',
                'User ID',
                'User Name',
                'User Email',
                'Created At',
                'Has Citations'
            ])
            
            message_count = 0
            for item in filtered_items:
                if item.get('type') == 'message':
                    content = item.get('content', '')
                    # Preview first 100 chars
                    content_preview = content[:100] + '...' if len(content) > 100 else content
                    
                    # Check for citations
                    has_citations = 'No'
                    if item.get('role') == 'tool':
                        try:
                            import json
                            tool_data = json.loads(content) if isinstance(content, str) else content
                            if isinstance(tool_data, dict) and tool_data.get('citations'):
                                has_citations = 'Yes'
                        except:
                            pass
                    
                    user_id = item.get('userId', '')
                    user_info = user_details.get(user_id, {})
                    
                    csv_writer.writerow([
                        item.get('id', ''),
                        item.get('conversationId', ''),
                        item.get('type', ''),
                        item.get('role', ''),
                        content_preview,
                        user_id,
                        user_info.get('displayName', ''),
                        user_info.get('email', ''),
                        item.get('createdAt', ''),
                        has_citations
                    ])
                    message_count += 1
            
            logging.info(f"Exported {message_count} messages to CSV.")
        
        # Get CSV content
        csv_content = output.getvalue()
        output.close()
        
        # Generate filename
        force_id = os.environ.get('FORCE_IDENTIFIER', 'unknown')
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"copa_analytics_{force_id}_{export_format}_{timestamp}.csv"
        
        # Return CSV file
        return func.HttpResponse(
            body=csv_content,
            status_code=200,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )
    
    except Exception as e:
        logging.error(f"ExportToCSV error: {str(e)}")
        return func.HttpResponse(
            f"Error exporting data: {str(e)}",
            status_code=500
        )
