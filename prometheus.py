from prometheus_client import Counter, generate_latest, Summary
import app
from flask import Response

# Create a Counter to track total file uploads
upload_counter = Counter('file_uploads_total', 'Total number of file uploads')

# Create a Summary to track the duration of requests
request_time = Summary('request_processing_seconds', 'Time spent processing request')

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')