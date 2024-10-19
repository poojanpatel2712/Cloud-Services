from flask import Flask, request, jsonify
from minio import Minio 
from flask_httpauth import HTTPBasicAuth
import os
import logging
auth = HTTPBasicAuth()
app = Flask(__name__)


# Define valid users
users = {
    "admin": "password123"
}

# Verify username and password
@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username
    return None

# Initialize MinIO client
client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)


# Prometheus configuration for implementing metrix monitoring
from prometheus_client import Counter, generate_latest, Summary
from flask import Response

# Create a Counter to track total file uploads
upload_counter = Counter('file_uploads_total', 'Total number of file uploads')

# Create a Summary to track the duration of requests
request_time = Summary('request_processing_seconds', 'Time spent processing request')

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')




# Upload functionality 
@app.route('/upload', methods=['POST'])
@auth.login_required
@request_time.time()
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file', 400
    
    bucket_name = 'your-bucket'
    
    # Ensure the bucket exists
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
    
    if file:
        filename = file.filename
        try:
            logging.info(f"Uploading {filename} to bucket {bucket_name}")
            client.put_object(bucket_name, filename, file.stream, length=-1, part_size=10*1024*1024)
            logging.info(f"Successfully uploaded {filename}")
            upload_counter.inc()
            return jsonify({"message": f"File '{filename}' uploaded successfully"}), 200
        except Exception as e:
            logging.error(f"Error uploading file: {str(e)}")
            return jsonify({"error": str(e)}), 500




# Default route for the root URL
@app.route('/')
def index():
    return "Welcome to the Local Cloud Storage API"


UPLOAD_FOLDER = 'D:\\Cloud_Services\\files'


# Enable logging to file
logging.basicConfig(filename='file_upload.log', level=logging.INFO)




# List of the uploaded files
@app.route('/files', methods=['GET'])
@auth.login_required
def list_files():
    bucket_name = 'your-bucket'  # Ensure the bucket name matches
    try:
        # Fetch the list of objects in the bucket
        objects = client.list_objects(bucket_name)
        
        # Extract filenames and return them as JSON
        files = [obj.object_name for obj in objects]
        
        # Log the files for debugging purposes
        print(f"Files in bucket: {files}")
        
        return jsonify(files), 200
    except Exception as e:
        # Log and return the error if something goes wrong
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Download functionality for the uploaded files
@app.route('/download/<filename>', methods=['GET'])
@auth.login_required
def download_file(filename):
    bucket_name = 'your-bucket'  # Ensure the bucket name matches

    try:
        # Download the file from MinIO
        response = client.get_object(bucket_name, filename)

        # Return the file data with appropriate headers for download
        return response.read(), 200, {
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'application/octet-stream'
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Delete functionality for the uploaded files
@app.route('/delete/<filename>', methods=['DELETE'])
@auth.login_required
def delete_file(filename):
    bucket_name = 'your-bucket'  # Ensure the bucket name matches
    
    try:
        # Delete the file from MinIO
        client.remove_object(bucket_name, filename)
        return jsonify({"message": f"File '{filename}' deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500





# Optional: Handle favicon request (to avoid the 404 error)
@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == "__main__":
    app.run(debug=True)
