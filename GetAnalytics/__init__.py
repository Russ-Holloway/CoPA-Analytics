import azure.functions as func
import json
import logging

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Example mock analytics data
        data = {
            "summary": {
                "totalInteractions": 1234,
                "uniqueUsers": 456,
                "avgSatisfactionScore": 4.2,
                "resolutionRate": "87%"
            },
            "categories": {
                "crime_reporting": {"count": 300},
                "traffic_incidents": {"count": 200},
                "general_enquiry": {"count": 400},
                "lost_property": {"count": 150},
                "noise_complaints": {"count": 184}
            },
            "themes": {
                "top_themes": [
                    {"theme": "Speeding", "count": 120},
                    {"theme": "Noise", "count": 90},
                    {"theme": "Lost Items", "count": 70}
                ]
            },
            "trends": {
                "hourly_distribution": [
                    5, 8, 12, 15, 20, 25, 30, 40, 50, 60, 70, 80,
                    90, 100, 110, 120, 130, 140, 100, 80, 60, 40, 20, 10
                ]
            },
            "questions": {
                "recent": [
                    {
                        "question": "How do I report a lost item?",
                        "category": "lost_property",
                        "satisfaction": 5,
                        "timestamp": "2025-07-05T10:00:00Z"
                    },
                    {
                        "question": "What is the penalty for speeding?",
                        "category": "traffic_incidents",
                        "satisfaction": 4,
                        "timestamp": "2025-07-05T09:00:00Z"
                    }
                ]
            }
        }
        return func.HttpResponse(
            json.dumps(data),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"GetAnalytics error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
