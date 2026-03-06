# ShowGo — Backend Deployment & Setup Guide

This document covers the setup, configuration, and deployment of the ShowGo FastAPI backend, including AWS (EC2 & RDS) and database initialization.

---

## 🚀 Quick Start (Local Development)

### 1. Environment Configuration
Create a `.env` file in the `backend/` directory:
```env
# Database (RDS Endpoint)
DATABASE_URL="postgresql://postgres:PASSWORD@RDS_ENDPOINT:5432/moviedb"

# Auth & Secrets
JWT_SECRET_KEY="your-random-secret-key"
JWT_EXPIRE_MINUTES=525600

# Email Delivery (SMTP)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASS="your-app-password"
SMTP_FROM="noreply@showgo.com"

# AWS (for S3 and SNS Notifications)
AWS_ACCESS_KEY_ID="AKIA..."
AWS_SECRET_ACCESS_KEY="TZc4..."
AWS_S3_BUCKET="showgo-images"
AWS_REGION="us-east-2"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Server
```bash
uvicorn main:app --host 0.0.0.0 --reload
```

---

## 🏗️ AWS Infrastructure Setup

### 1. EC2 Instance (Web Server)
1. Launch an **Ubuntu 24.04 LTS** instance (`t2.micro` or `t2.small`).
2. **Security Group Rules**:
   - **SSH (22)**: Access for your IP Or Allow for all (Optional).
   - **Custom TCP (8000)**: Port for the FastAPI backend.
   - **PostgreSQL (5432)**: Ensure this is allowed if connecting locally (usually restricted to EC2 SG).

### 2. RDS Instance (PostgreSQL)
1. Create a **PostgreSQL 15+** database on AWS RDS.
2. **Connectivity**: Choose the same VPC as your EC2.
3. **Public Access**: No (Security Best Practice) Or Yes (For Testing).
4. **RDS Security Group**: Add an inbound rule for **PostgreSQL (5432)** allowing the **EC2 Security Group** as the source.
5. **Database Name**: `moviedb`.

---

## 🚀 Deployment on EC2

### 1. Connect and Install Environment
```bash
ssh -i key.pem ubuntu@YOUR_EC2_IP
sudo apt update
sudo apt install -y python3-pip python3-venv redis-server postgresql-client
```

### 2. Initialize the Database
Before running the app, connect to your RDS endpoint and create the database:
```bash
psql -h YOUR_RDS_ENDPOINT -U postgres -p 5432
# Type password
CREATE DATABASE moviedb;
\q
```

### 3. Setup App & Run
```bash
git clone YOUR_REPO_URL
cd <To Repo Folder>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## ⚙️ Service Management (systemd)

To run the backend as a background service on EC2, use `systemd`.

### 1. Management Commands
Manage the `movieapp.service` with these commands:
- **Restart**: `sudo systemctl restart movieapp.service`
- **Start**: `sudo systemctl start movieapp.service`
- **Stop**: `sudo systemctl stop movieapp.service`
- **Status**: `sudo systemctl status movieapp.service`
- **View Logs**: `journalctl -u movieapp.service -f`

### 2. Sample Service File
Create a file at `/etc/systemd/system/movieapp.service`:
```ini
[Unit]
Description=ShowGo FastAPI Backend
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Movie-app/backend
Environment="PATH=/home/ubuntu/Movie-app/backend/venv/bin"
ExecStart=/home/ubuntu/Movie-app/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

---

## 🏗️ Database Initialization & Seeding

Run these scripts in order to set up your tables and initial data:

### 0. Reset Database (DANGEROUS)
If you need to wipe all existing tables and data for a clean start:
```bash
python -m scripts.reset_db
```

### 1. Create Tables & Seed Core Users
This script creates the schema and adds the initial Admin (`admin@test.com`) and Merchant (`merchant@test.com`) accounts.
```bash
python -m scripts.init_db
```

### 2. Populate App Data
Run these to seed the movie catalog and theatre locations:
```bash
python -m scripts.populate_locations
python -m scripts.populate_movies
python -m scripts.populate_shows
python -m scripts.populate_seats
```

---

## 🛠️ Backend Features
- **Email Authentication**: Secure OTP-based login via SMTP.
- **Seat Locking**: Redis-backed temporary reservations (TTL: 10s).
- **PDF Tickets**: Automatic ticket generation and email delivery.
- **S3 Image Hosting**: Dynamic uploads for movie posters and user avatars.
