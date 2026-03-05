# ShowGo — Complete Project Setup Guide

> **This guide explains how to set up the entire ShowGo project (Backend + Frontend + Merchant) from scratch on a new account.** It covers AWS, Firebase, EAS, RDS, and everything you need.

> ⚠️ **IMPORTANT: This project uses AWS RDS for the database, NOT a local PostgreSQL install.** Never use `localhost` in `DATABASE_URL`. Always use your RDS endpoint (e.g. `showgo-db.abc123.us-east-2.rds.amazonaws.com`).

---

## 📂 Project Structure

```
Movie-app/
├── backend/           ← FastAPI backend (Python)
├── frontend/          ← ShowGo User App (React Native / Expo)
└── merchant/          ← ShowGo Merchant App (React Native / Expo)
```

---

## 📋 Files You Need to Change (Quick Reference)

| File | What to Change |
|------|---------------|
| `backend/.env` | Database URL, AWS keys, JWT secret, Firebase project ID |
| `backend/firebase-service-account.json` | Replace with new Firebase service account key |
| `frontend/.env` | Backend API URL (your EC2 IP) |
| `merchant/.env` | Backend API URL (your EC2 IP) |
| `frontend/app.json` | `package`, `owner`, EAS `projectId` |
| `merchant/app.json` | `package`, `owner`, EAS `projectId` |
| `frontend/google-services.json` | Replace with new Firebase config |
| `merchant/google-services.json` | Replace with new Firebase config |

---

# PART 1: AWS Setup (EC2 + RDS)

## 1.1 — Create an EC2 Instance

1. Go to [AWS Console](https://console.aws.amazon.com/) → **EC2** → **Launch Instance**
2. Choose these settings:
   - **Name:** `showgo-server`
   - **AMI:** Ubuntu Server 24.04 LTS
   - **Instance type:** `t2.small` (or `t2.micro` for free tier)
   - **Key pair:** Create a new key pair → download the `.pem` file (keep it safe!)
   - **Security Group:** Create a new one with these rules:

| Type | Port | Source | Purpose |
|------|------|--------|---------|
| SSH | 22 | My IP | SSH access |
| Custom TCP | 8000 | 0.0.0.0/0 | Backend API |
| PostgreSQL | 5432 | (Security Group of EC2) | Only for RDS |

3. Click **Launch Instance**
4. Note down the **Public IP** (e.g. `3.15.100.200`)

## 1.2 — Create an RDS PostgreSQL Database

> ⚠️ **RDS = a managed database in the cloud. We do NOT use a local PostgreSQL install.**
> Your backend will connect to this RDS instance instead of `localhost`.

1. Go to [AWS Console](https://console.aws.amazon.com/) → **RDS** → **Create Database**
2. Choose these settings:
   - **Engine:** PostgreSQL
   - **Version:** PostgreSQL 15+
   - **Template:** Free tier (if available) or Dev/Test
   - **DB Instance Identifier:** `showgo-db`
   - **Master username:** `postgres`
   - **Master password:** Choose a strong password (e.g. `MyStr0ngPassw0rd!`) — **write this down!**
   - **Instance class:** `db.t3.micro` (free tier eligible)
   - **Storage:** 20 GB (General Purpose SSD)
   - **VPC:** Same VPC as your EC2 instance
   - **Public access:** **No** (keep it private, only EC2 can access)
   - **Security Group:** See section 1.2.1 below

3. Click **Create Database** and wait 5-10 minutes
4. Once created, click on it and copy the **Endpoint** (e.g. `showgo-db.abc123.us-east-2.rds.amazonaws.com`)

### 1.2.1 — Configure RDS Security Group

The RDS database must allow connections from your EC2 instance:

1. Go to **EC2** → **Security Groups**
2. Find the security group attached to your **RDS** instance
3. Click **Edit inbound rules** → **Add rule**:

   | Type | Port | Source | Purpose |
   |------|------|--------|---------|
   | PostgreSQL | 5432 | EC2's Security Group ID (e.g. `sg-0abc123`) | Allow EC2 to connect to RDS |

4. Click **Save rules**

> 💡 **Tip:** Setting the source to your EC2's security group (instead of an IP) means any EC2 instance in that group can connect — even if the IP changes.

### 1.2.2 — Your DATABASE_URL Format

After creating RDS, your `DATABASE_URL` should look like this:

```
postgresql://postgres:YOUR_PASSWORD@YOUR_RDS_ENDPOINT:5432/moviedb
```

**Example:**
```
postgresql://postgres:MyStr0ngPassw0rd!@showgo-db.abc123.us-east-2.rds.amazonaws.com:5432/moviedb
```

> ❌ **NEVER use:** `postgresql://postgres:password@localhost:5432/moviedb`
> ✅ **ALWAYS use:** `postgresql://postgres:password@YOUR_RDS_ENDPOINT:5432/moviedb`

## 1.3 — Create the Database

SSH into your EC2 instance and create the database:

```bash
# Connect to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Install PostgreSQL client
sudo apt update
sudo apt install -y postgresql-client

# Connect to RDS and create the database
psql -h YOUR_RDS_ENDPOINT -U postgres -p 5432
# Enter the password you set during RDS creation

# Inside psql:
CREATE DATABASE moviedb;
\q
```

## 1.4 — Create an S3 Bucket (for Image Storage)

1. Go to [AWS Console](https://console.aws.amazon.com/) → **S3** → **Create Bucket**
2. Settings:
   - **Bucket name:** `your-showgo-images` (must be globally unique)
   - **Region:** Same as your EC2 (e.g. `us-east-2`)
   - **Uncheck** "Block all public access" (images need to be publicly readable)
3. After creation, go to **Permissions** → **Bucket Policy** → Add:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-showgo-images/*"
        }
    ]
}
```

## 1.5 — Create an IAM User (for AWS Keys)

1. Go to [AWS Console](https://console.aws.amazon.com/) → **IAM** → **Users** → **Create User**
2. **User name:** `showgo-backend`
3. **Permissions:** Attach these policies:
   - `AmazonS3FullAccess`
4. After creation → **Security credentials** → **Create access key**
5. Choose "Application running outside AWS" → **Create**
6. **Save** the `Access Key ID` and `Secret Access Key` (you'll need them in `.env`)

---

# PART 2: Firebase Setup

## 2.1 — Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. **Project name:** `ShowGo` (or any name you want)
4. **Disable Google Analytics** (optional, saves time)
5. Click **Create Project**

## 2.2 — Upgrade to Blaze Plan

**This is required for SMS OTP to work!**

1. In your Firebase project → Click the ⚙️ icon → **Usage and billing**
2. Click **Modify plan** → Select **Blaze (pay-as-you-go)**
3. Link a billing account

## 2.3 — Enable Phone Authentication

1. Go to **Authentication** → **Sign-in method**
2. Click **Phone** → **Enable** → **Save**

## 2.4 — Add Android Apps to Firebase

You need to add **two Android apps** (one for User, one for Merchant):

### User App (frontend)
1. Click **Add app** → **Android**
2. **Package name:** `com.youraccount.frontend`
   > ⚠️ This MUST match the `package` field in `frontend/app.json`
3. **App nickname:** `ShowGo User`
4. Click **Register app**
5. **Download `google-services.json`** → Save it to `frontend/google-services.json`

### Merchant App
1. Click **Add app** → **Android**
2. **Package name:** `com.youraccount.showgomerchant`
   > ⚠️ This MUST match the `package` field in `merchant/app.json`
3. **App nickname:** `ShowGo Merchant`
4. Click **Register app**
5. **Download `google-services.json`** → Save it to `merchant/google-services.json`

## 2.5 — Add SHA Fingerprints

After your first EAS build, you'll get SHA-1 and SHA-256 fingerprints. Add them to Firebase:

1. Run: `eas credentials -p android` (in each app folder)
2. Copy the SHA-1 and SHA-256 values
3. In Firebase Console → ⚙️ **Project Settings** → Your App → **Add fingerprint**
4. Paste SHA-1 → Save
5. Paste SHA-256 → Save

> This is needed so that OTP sending works seamlessly without redirecting to a browser.

## 2.6 — Enable Identity Toolkit API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your Firebase project from the top dropdown
3. Go to **APIs & Services** → **Library**
4. Search for **"Identity Toolkit API"** → Click **Enable**

## 2.7 — Enable Play Integrity API

1. In the same Google Cloud Console
2. Go to **APIs & Services** → **Library**
3. Search for **"Play Integrity API"** → Click **Enable**

## 2.8 — Generate Service Account Key (for Backend)

1. In Firebase Console → ⚙️ **Project Settings** → **Service accounts**
2. Click **"Generate new private key"**
3. A JSON file will download
4. **Rename** it to `firebase-service-account.json`
5. Place it in the `backend/` folder (or upload directly to your server)

> ⚠️ **Do NOT commit this file to GitHub!** Add it to `.gitignore`.

## 2.9 — Add Test Phone Numbers (Optional)

To test OTP without using real SMS:

1. In Firebase Console → **Authentication** → **Settings** → **Phone**
2. Under "Phone numbers for testing", add:
   - Phone: `+91 1234567890` → Code: `123456`
   - Add more as needed

---

# PART 3: Backend Deployment on EC2

## 3.1 — SSH into EC2

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

## 3.2 — Install Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git redis-server nginx

# Start Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

## 3.3 — Clone Your Project

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git showgo
cd showgo/backend
```

## 3.4 — Set Up Python Environment

```bash
pip install -r requirements.txt
```

### 3. Run the Server
```bash
uvicorn main:app --host 0.0.0.0 --reload
```

---

## 🏗️ Database Initialization

Run these scripts in order to set up your tables and initial data:

### 1. Create Tables & Admin User
```bash
python -m scripts.init_db
```

### 2. Populate Data (Movies, Theatres, Shows, Seats)
```bash
python -m scripts.populate_locations
python -m scripts.populate_movies
python -m scripts.populate_shows
python -m scripts.populate_seats
```

---

## 🛠️ Features
- **OTP Auth**: Email & SMS based login.
- **Role-Based Access**: Separate flows for Users and Merchants.
- **Seat Locking**: Redis-backed temporary seat reservation.
- **PDF Tickets**: Automated ticket generation and email delivery.
- **Push Notifications**: Expo Push SDK integration.
