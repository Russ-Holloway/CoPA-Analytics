import azure.functions as func
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'Dashboard', 'logo.png')
    logo_path = os.path.abspath(logo_path)
    try:
        with open(logo_path, 'rb') as f:
            logo_bytes = f.read()
        return func.HttpResponse(logo_bytes, mimetype="image/png")
    except Exception as e:
        return func.HttpResponse(f"Logo not found: {e}", status_code=404)
