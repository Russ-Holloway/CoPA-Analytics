import os
import azure.functions as func
import requests

def main(req: func.HttpRequest) -> func.HttpResponse:
    logo_url = os.environ.get('FORCE_LOGO_URL')
    if not logo_url:
        return func.HttpResponse(
            "Logo not configured.",
            status_code=404,
            headers={"Content-Type": "text/plain"}
        )
    try:
        resp = requests.get(logo_url, timeout=10)
        if resp.status_code != 200:
            return func.HttpResponse(
                f"Failed to fetch logo: {resp.status_code}",
                status_code=502,
                headers={"Content-Type": "text/plain"}
            )
        content_type = resp.headers.get('Content-Type', 'image/png')
        return func.HttpResponse(
            resp.content,
            status_code=200,
            headers={"Content-Type": content_type}
        )
    except Exception as e:
        return func.HttpResponse(
            f"Error fetching logo: {str(e)}",
            status_code=500,
            headers={"Content-Type": "text/plain"}
        )
