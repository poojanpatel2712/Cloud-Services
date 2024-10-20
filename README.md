# Cloud-Services

# Cloud Storage Service with User Authentication

This project is a **cloud storage service** that allows users to securely upload, view, download, and delete their own files through a user-friendly interface. All files are stored using **MinIO**, a scalable S3-compatible object storage service. Each user can access only their own uploaded files, while the administrator can monitor and manage all the files via the MinIO console.

## Features

- **User Authentication**: Users can sign up, log in, and manage their own files.
- **File Management**: Users can upload, view, download, and delete files.
- **User-Specific File Visibility**: Each user can only access their own files. User data is isolated.
- **Admin View via MinIO Console**: Admins can view all files uploaded by users through the MinIO console.
- **MinIO Integration**: Files are securely stored using MinIO, providing S3-compatible object storage.

## Significance of the Project

This project is a robust example of a **cloud storage solution** with user authentication and file isolation. It demonstrates how to implement secure, user-specific file storage using **Flask** for the backend and **MinIO** for file storage. The project highlights:
- **Role-based access control (RBAC)** for user-specific data visibility.
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

