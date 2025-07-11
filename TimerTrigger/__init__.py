import datetime
import logging
import os
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    logging.info('HTTP-triggered analytics email function called at %s', utc_timestamp)
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
        graph_tenant_id = os.environ.get('GRAPH_TENANT_ID')
        email_from = os.environ.get('EMAIL_FROM')
        email_to = os.environ.get('EMAIL_TO') or os.environ.get('ADMIN_EMAIL')

        if not all([graph_client_id, graph_tenant_id, email_from, email_to]):
            logging.error('Missing Graph API or email environment variables. Email not sent.')
            return func.HttpResponse('Missing Graph API or email environment variables.', status_code=500)

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

        # Authenticate with Microsoft Graph using Device Code flow (delegated)
        authority = f"https://login.microsoftonline.com/{graph_tenant_id}"
        app = msal.PublicClientApplication(
            graph_client_id,
            authority=authority
        )
        scopes = ["Mail.Send"]
        accounts = app.get_accounts()
        if accounts:
            result = app.acquire_token_silent(scopes, account=accounts[0])
        else:
            result = None
        if not result or "access_token" not in result:
            logging.info("Initiating device code flow for delegated Graph API access...")
            flow = app.initiate_device_flow(scopes=scopes)
            if "user_code" not in flow:
                return func.HttpResponse("Device code flow failed to start.", status_code=500)
            logging.info(f"Please authenticate: {flow['message']}")
            result = app.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            logging.error(f"Failed to obtain access token: {result.get('error_description')}")
            return func.HttpResponse(f"Failed to obtain access token: {result.get('error_description')}", status_code=500)

        access_token = result["access_token"]
        graph_url = f"https://graph.microsoft.com/v1.0/users/{email_from}/sendMail"
        email_payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": [
                    {"emailAddress": {"address": email_to}}
                ]
            },
            "saveToSentItems": "true"
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(graph_url, headers=headers, json=email_payload)
        if response.status_code == 202:
            logging.info(f"Analytics email sent to {email_to} via Microsoft Graph API.")
            return func.HttpResponse(f"Analytics email sent to {email_to} via Microsoft Graph API.", status_code=200)
        else:
            logging.error(f"Failed to send email: {response.text}")
            return func.HttpResponse(f"Failed to send email: {response.text}", status_code=500)
    except Exception as e:
        logging.error(f"Error in analytics email function: {str(e)}")
        return func.HttpResponse(f"Error in analytics email function: {str(e)}", status_code=500)
