import azure.functions as func
import logging
import os
import csv
import io
from datetime import datetime, timedelta
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Export conversation data from Cosmos DB to CSV format.
    
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
                csv_writer.writerow([
                    conv['id'],
                    conv['title'],
                    conv['type'],
                    conv['category'],
                    conv['userId'],
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
                    
                    csv_writer.writerow([
                        item.get('id', ''),
                        item.get('conversationId', ''),
                        item.get('type', ''),
                        item.get('role', ''),
                        content_preview,
                        item.get('userId', ''),
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
