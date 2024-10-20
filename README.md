# Cloud-Services

This project is a **cloud storage service** that allows users to securely upload, view, download, and delete their own files through a user-friendly interface. All files are stored using **MinIO**, a scalable S3-compatible object storage service. Each user can access only their own uploaded files, while the administrator can monitor and manage all the files via the MinIO console.

## Features

- **User Authentication**: Users can sign up, log in, and manage their own files.
- **File Management**: Users can upload, view, download, and delete files.
- **User-Specific File Visibility**: Each user can only access their own files. User data is isolated.
- **Admin View via MinIO Console**: Admins can view all files uploaded by users through the MinIO console.
- **MinIO Integration**: Files are securely stored using MinIO, providing S3-compatible object storage.

## Significance of the Project

This project is a robust example of a **cloud storage solution** with user authentication and file isolation. It demonstrates how to implement secure, user-specific file storage using **Flask** for the backend and **MinIO** for file storage. The project highlights:
- Scalable object storage using **MinIO**.
- Building a web application with **Flask** that handles user data securely.

---

## Installation Instructions

### Prerequisites
Make sure you have the following installed:
- **Python 3.7+**
- **MinIO** (for object storage)
- **Docker** (Optional, for running MinIO in a container)

### Steps to Clone and Run the Project

1. **Clone the Repository**

```bash
git clone https://github.com/poojanpatel2712/Cloud-Services.git
cd Cloud-Services
```


2. **Create a Virtual Environment and Install Dependencies**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set Up MinIO**

```bash
docker run -p 9000:9000 --name minio -e "MINIO_ACCESS_KEY=minioadmin" -e "MINIO_SECRET_KEY=minioadmin" minio/minio server /data
```

MinIO will now be accessible at **http://localhost:9000**. Log in with:
Access Key: minioadmin
Secret Key: minioadmin

4. **Set Up the Database**

Run the following command to create the SQLite database for user and file management:

```bash
python -c "from app import db; db.create_all()"
```

5. **Run the Flask Application**

```bash
python app.py
```

The application will run at **http://localhost:5000**.

Future Enhancements:
- File Versioning: Implement file versioning to allow users to access older versions of their files.
- OAuth Integration: Add social login options (e.g., Google, GitHub) to simplify user authentication.
- File Encryption: Encrypt uploaded files for additional security.
