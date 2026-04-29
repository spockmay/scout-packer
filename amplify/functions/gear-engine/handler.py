import json


def handler(event, context):
    # Just return a simple response with a single header
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # Single wildcard
        },
        "body": json.dumps(
            {
                "message": "Handshake Successful!",
                "note": "If you see this, the CORS double-header issue is resolved.",
            }
        ),
    }
