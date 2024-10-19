from flask import Flask, request, jsonify
from minio import Minio 
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

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






app = Flask(__name__)

# Initialize MinIO client
client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Default route for the root URL
@app.route('/')
def index():
    return "Welcome to the Local Cloud Storage API"

import os

UPLOAD_FOLDER = 'D:\\Cloud_Services\\files'

import logging

# Enable logging to file
logging.basicConfig(filename='file_upload.log', level=logging.INFO)


# Optional: Handle favicon request (to avoid the 404 error)
@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == "__main__":
    app.run(debug=True)
