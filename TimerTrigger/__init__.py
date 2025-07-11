import datetime
import logging
import os
import json
import azure.functions as func
from azure.cosmos import CosmosClient, exceptions

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    logging.info('TimerTrigger function ran at %s', mytimer.schedule_status.last)

    force_id = os.environ.get('FORCE_IDENTIFIER', 'unknown')
    
    try:
        # Simulate analytics processing (as before)
        processed_data = {
            "timestamp": utc_timestamp,
            "forceId": force_id,
            "processedRecords": 1250,
            "summary": {
                "newInteractions": 85,
                "updatedMetrics": True,
                "trendsCalculated": True
            },
            "status": "completed"
        }
        logging.info(f'Analytics processing completed for force: {force_id}')
        logging.info(f'Processed data: {json.dumps(processed_data, indent=2)}')

        # Send daily analytics email using Microsoft Graph API
        import requests
        import msal

        graph_client_id = os.environ.get('GRAPH_CLIENT_ID')
        graph_client_secret = os.environ.get('GRAPH_CLIENT_SECRET')
        graph_tenant_id = os.environ.get('GRAPH_TENANT_ID')
        email_from = os.environ.get('EMAIL_FROM')
        email_to = os.environ.get('EMAIL_TO') or os.environ.get('ADMIN_EMAIL')

        if not all([graph_client_id, graph_client_secret, graph_tenant_id, email_from, email_to]):
            logging.error('Missing Graph API or email environment variables. Email not sent.')
            return

        subject = f"CoPPA Analytics Daily Report - {force_id} - {utc_timestamp[:10]}"
        body = f"""
Hello,

This is your automated CoPPA Analytics daily report for {force_id}.

Summary:
- New Interactions: {processed_data['summary']['newInteractions']}
- Metrics Updated: {processed_data['summary']['updatedMetrics']}
- Trends Calculated: {processed_data['summary']['trendsCalculated']}
- Processed Records: {processed_data['processedRecords']}
- Timestamp: {processed_data['timestamp']}

Status: {processed_data['status']}

This is an automated message. Please do not reply.
"""

        # Authenticate with Microsoft Graph
        authority = f"https://login.microsoftonline.com/{graph_tenant_id}"
        app = msal.ConfidentialClientApplication(
            graph_client_id,
            authority=authority,
            client_credential=graph_client_secret
        )
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" not in result:
            logging.error(f"Could not obtain access token: {result}")
            return
        access_token = result['access_token']

        # Prepare Graph API message
        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": [
                    {"emailAddress": {"address": r.strip()}} for r in email_to.split(',') if r.strip()
                ],
                "from": {"emailAddress": {"address": email_from}}
            },
            "saveToSentItems": "false"
        }

        # Send email via Graph API
        graph_url = f"https://graph.microsoft.com/v1.0/users/{email_from}/sendMail"
        response = requests.post(
            graph_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=message
        )
        if response.status_code >= 400:
            logging.error(f"Graph API error: {response.status_code} {response.text}")
        else:
            logging.info(f"Daily analytics email sent to {email_to} via Microsoft Graph API.")

    except Exception as e:
        logging.error(f'Error in timer trigger: {str(e)}')
        raise

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function completed successfully')
