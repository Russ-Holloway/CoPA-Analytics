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
    # Force HTTPS if not already
    if logo_url.startswith('http://'):
        logo_url = 'https://' + logo_url[len('http://'):]
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        resp = requests.get(logo_url, timeout=10, headers=headers)
        if resp.status_code != 200:
            return func.HttpResponse(
                f"Failed to fetch logo: {resp.status_code}\nURL: {logo_url}\nResponse text: {resp.text}",
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
        import traceback
        tb = traceback.format_exc()
        return func.HttpResponse(
            f"Error fetching logo: {str(e)}\nURL: {logo_url}\nTraceback:\n{tb}",
            status_code=500,
            headers={"Content-Type": "text/plain"}
        )
