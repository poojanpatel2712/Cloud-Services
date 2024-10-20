from flask import Flask, request, jsonify, render_template, make_response
from minio import Minio 
from flask_httpauth import HTTPBasicAuth
import os
import logging
auth = HTTPBasicAuth()
app = Flask(__name__)


# user Authentication 

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    files = db.relationship('File', backref='owner', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<File {self.filename}>"


# Create the database
with app.app_context():
    db.create_all()



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    
    return render_template('login.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))






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


# @app.route('/test')
# def test():
#     return "Test route working!"



# Default route for the root URL
@app.route('/')
def index():
    print("Rendering index.html")
    response = make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-store'
    return response

UPLOAD_FOLDER = 'D:\\Cloud_Services\\files'


# Enable logging to file
logging.basicConfig(filename='file_upload.log', level=logging.INFO)


# Upload functionality
@app.route('/upload', methods=['POST'])
@request_time.time()
@login_required
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
        user_id = current_user.id  # Get the logged-in user's ID

        try:
            logging.info(f"Uploading {filename} to bucket {bucket_name}")
            
            # Upload the file to MinIO
            client.put_object(bucket_name, filename, file.stream, length=-1, part_size=10*1024*1024)
            
            # Log successful upload
            logging.info(f"Successfully uploaded {filename}")
            
            # Increment the upload counter
            upload_counter.inc()

            # Save file info in the database (associate with the current user)
            new_file = File(filename=filename, user_id=user_id)
            db.session.add(new_file)
            db.session.commit()

            return jsonify({"message": f"File '{filename}' uploaded successfully"}), 200
        except Exception as e:
            logging.error(f"Error uploading file: {str(e)}")
            return jsonify({"error": str(e)}), 500



# List of the uploaded files
@app.route('/files', methods=['GET'])
@login_required
def list_files():
    try:
        # Fetch files associated with the logged-in user
        user_files = File.query.filter_by(user_id=current_user.id).all()

        # Extract filenames
        files = [file.filename for file in user_files]

        # Log the files for debugging purposes
        logging.info(f"Files for user {current_user.username}: {files}")

        return jsonify(files), 200
    except Exception as e:
        # Log and return the error if something goes wrong
        logging.error(f"Error fetching files: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Download functionality for the uploaded files
@app.route('/download/<filename>', methods=['GET'])
@login_required
def download_file(filename):
    try:
        # Check if the file belongs to the current user
        user_file = File.query.filter_by(filename=filename, user_id=current_user.id).first()

        if not user_file:
            logging.warning(f"User {current_user.username} attempted to download a file they don't own.")
            return jsonify({"error": "File not found or you don't have permission to access it"}), 403

        # Download the file from MinIO
        bucket_name = 'your-bucket'
        response = client.get_object(bucket_name, filename)

        # Return the file data with appropriate headers for download
        return response.read(), 200, {
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'application/octet-stream'
        }
    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Delete functionality for the uploaded files
@app.route('/delete/<filename>', methods=['DELETE'])
@login_required
def delete_file(filename):
    try:
        # Check if the file exists and belongs to the current user
        file_to_delete = File.query.filter_by(filename=filename, user_id=current_user.id).first()

        if not file_to_delete:
            logging.warning(f"User {current_user.username} attempted to delete a file they don't own.")
            return jsonify({"error": "File not found or you don't have permission to delete it"}), 403

        # Delete the file from MinIO
        bucket_name = 'your-bucket'
        client.remove_object(bucket_name, filename)

        # Remove the file from the database
        db.session.delete(file_to_delete)
        db.session.commit()

        logging.info(f"File '{filename}' deleted by user {current_user.username}")
        return jsonify({"message": f"File '{filename}' deleted successfully"}), 200
    except Exception as e:
        logging.error(f"Error deleting file: {str(e)}")
        return jsonify({"error": str(e)}), 500




# Optional: Handle favicon request (to avoid the 404 error)
@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == "__main__":
    app.run(debug=True)
