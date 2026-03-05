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
After that need to seed the data
source venv/bin/activate
python3 -m scripts.init_db
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

## 1.5 — Create an IAM User or use Root acc (for AWS Keys)

1. Go to [AWS Console](https://console.aws.amazon.com/) → **IAM** → **Users** → **Create User** ( Optional )
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
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3.5 — Configure the `.env` File

Create/edit the `.env` file in the `backend/` folder:

```bash
nano .env
```

Paste this (replace values with YOUR actual values):

```env
APP_NAME="Movie Ticket Backend"
DEBUG=True

# ⬇️ REPLACE with your RDS endpoint, username, password, and database name
DATABASE_URL="postgresql://postgres:YOUR_RDS_PASSWORD@YOUR_RDS_ENDPOINT:5432/moviedb"

# Redis (runs locally on EC2)
REDIS_URL="redis://localhost:6379/0"

# ⬇️ CREATE A STRONG RANDOM STRING for JWT signing
JWT_SECRET_KEY="generate-a-long-random-secret-string-here"
JWT_EXPIRE_MINUTES=525600
OTP_EXPIRE_SECONDS=300
SEAT_LOCK_TTL=10

# ⬇️ REPLACE with your IAM user's keys
AWS_ACCESS_KEY_ID="YOUR_AWS_ACCESS_KEY"
AWS_SECRET_ACCESS_KEY="YOUR_AWS_SECRET_KEY"
AWS_S3_BUCKET="your-showgo-images"
AWS_REGION="us-east-2"

# ⬇️ REPLACE with your Firebase project ID
FIREBASE_PROJECT_ID="your-firebase-project-id"
```

### Important Notes:
- `DATABASE_URL` — Use your **RDS endpoint**, NOT `localhost`
- `JWT_SECRET_KEY` — Use a random string (e.g. generate with `openssl rand -hex 32`)
- `FIREBASE_PROJECT_ID` — Find this in Firebase Console → ⚙️ Project Settings → General

## 3.6 — Upload Firebase Service Account Key

Upload the `firebase-service-account.json` file to the backend folder on the server:

```bash
# From your LOCAL machine:
scp -i your-key.pem /path/to/firebase-service-account.json ubuntu@YOUR_EC2_IP:~/showgo/backend/
```

## 3.7 — Run Database Migrations

```bash
cd ~/showgo/backend
source venv/bin/activate
alembic upgrade head
```

## 3.8 — Test the Backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open `http://YOUR_EC2_IP:8000/docs` in your browser — you should see the API docs.

## 3.9 — Create a Systemd Service (Auto-start)

```bash
sudo nano /etc/systemd/system/showgo.service
```

Paste:

```ini
[Unit]
Description=ShowGo Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/showgo/backend
ExecStart=/home/ubuntu/showgo/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
Environment=PATH=/home/ubuntu/showgo/backend/venv/bin:/usr/bin

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable showgo.service
sudo systemctl start showgo.service

# Check status:
sudo systemctl status showgo.service

# View logs:
sudo journalctl -u showgo.service -f
```

---

# PART 4: Frontend & Merchant App Setup

## 4.1 — Install EAS CLI

On your **local machine** (Mac):

```bash
npm install -g eas-cli
```

## 4.2 — Login to EAS

```bash
eas login
# Enter your Expo account username and password
```

## 4.3 — Configure Frontend App

### Update `frontend/app.json`:

Change these fields:

```json
{
  "expo": {
    "name": "ShowGo",
    "slug": "frontend",
    "android": {
      "package": "com.YOURACCOUNT.frontend"
    },
    "extra": {
      "eas": {
        "projectId": "← will be auto-generated by eas init"
      }
    }
  }
}
```

### Update `frontend/.env`:

```env
EXPO_PUBLIC_API_URL=http://YOUR_EC2_PUBLIC_IP:8000
```

### Link to EAS:

```bash
cd frontend
eas init
# This will create/update the projectId in app.json
```

## 4.4 — Configure Merchant App

### Update `merchant/app.json`:

```json
{
  "expo": {
    "name": "ShowGo Merchant",
    "slug": "merchant",
    "owner": "YOUR_EAS_USERNAME",
    "android": {
      "package": "com.YOURACCOUNT.showgomerchant"
    },
    "extra": {
      "eas": {
        "projectId": "← will be auto-generated by eas init"
      }
    }
  }
}
```

### Update `merchant/.env`:

```env
EXPO_PUBLIC_API_URL=http://YOUR_EC2_PUBLIC_IP:8000
```

### Link to EAS:

```bash
cd merchant
eas init
```

## 4.5 — Replace `google-services.json`

1. Download the `google-services.json` from Firebase for each app (see Part 2.4)
2. Replace `frontend/google-services.json` with the User App config
3. Replace `merchant/google-services.json` with the Merchant App config

> ⚠️ The `package_name` inside `google-services.json` MUST match the `android.package` in `app.json`!

---

# PART 5: Building the Apps

## 5.1 — Build Frontend App (User)

```bash
cd frontend

# Install dependencies
npm install

# Build APK for testing
eas build --profile preview --platform android
```

Wait for the build to complete (10-30 minutes). Once done, download the APK from the link provided.

## 5.2 — Build Merchant App

```bash
cd merchant

# Install dependencies
npm install

# Build APK for testing
eas build --profile preview --platform android
```

## 5.3 — After First Build: Add SHA Fingerprints

After the first build for each app, add the fingerprints to Firebase:

```bash
# Get fingerprints
cd frontend
eas credentials -p android
# Note the SHA1 and SHA256 values

cd ../merchant
eas credentials -p android
# Note the SHA1 and SHA256 values
```

Add both SHA-1 and SHA-256 to Firebase Console for each app (see Part 2.5).

## 5.4 — Rebuild After Adding Fingerprints

After adding fingerprints, rebuild both apps (no need to do this every time, only the first time):

```bash
cd frontend
eas build --profile preview --platform android

cd ../merchant
eas build --profile preview --platform android
```

---

# PART 6: EAS Build Profiles

The `eas.json` files control how builds are configured. Here's what a typical `eas.json` looks like:

```json
{
  "build": {
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "distribution": "store"
    }
  }
}
```

- **`preview`** → Creates an APK for testing (install directly on phones)
- **`production`** → Creates an AAB for Google Play Store submission

---

# PART 7: Testing the Flow

## 7.1 — Backend Test

```
Open: http://YOUR_EC2_IP:8000/docs
```

This should display the Swagger API documentation.

## 7.2 — Install APKs

1. Download the APK links from EAS build output
2. Install them on your Android phone
3. Open the app

## 7.3 — Test OTP Login

1. Enter your phone number
2. Tap "Get OTP"
3. Enter the OTP received via SMS
4. You should be logged in!

> If using test phone numbers (Part 2.9), use the test number and code.

---

# PART 8: Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| **`auth/missing-client-identifier`** | Add SHA-1 fingerprint to Firebase |
| **OTP redirects to browser page** | Add SHA-256 fingerprint + Enable Play Integrity API |
| **`too-many-requests`** | Wait 30 min or use test phone numbers |
| **Backend can't connect to RDS** | Check security group allows port 5432 from EC2 |
| **GitHub blocks push (secret detected)** | Don't commit `firebase-service-account.json` — add to `.gitignore` |
| **`google-services.json` error during build** | Ensure `googleServicesFile` is set in `app.json` and file exists |
| **App shows "Network Error"** | Check `EXPO_PUBLIC_API_URL` in `.env` matches your EC2 IP |

---

# PART 9: Updating After Deployment

## When you make code changes:

### Backend:
```bash
# On EC2:
cd ~/showgo/backend
git pull origin main
source venv/bin/activate
pip install -r requirements.txt     # if new dependencies
alembic upgrade head                # if new migrations
sudo systemctl restart showgo.service
```

### Frontend / Merchant:
```bash
# On your Mac:
cd frontend   # or cd merchant
eas build --profile preview --platform android
# Download and install the new APK
```

---

# PART 10: Quick Start Checklist

```
□ AWS Account
  ├── □ EC2 Instance running
  ├── □ RDS PostgreSQL database created
  ├── □ S3 Bucket created with public read policy
  ├── □ IAM User with access keys
  └── □ Security groups configured

□ Firebase
  ├── □ Project created
  ├── □ Upgraded to Blaze plan
  ├── □ Phone Auth enabled
  ├── □ Identity Toolkit API enabled
  ├── □ Play Integrity API enabled
  ├── □ User Android app added (package matches app.json)
  ├── □ Merchant Android app added (package matches app.json)
  ├── □ google-services.json downloaded for both apps
  ├── □ Service account key generated
  └── □ SHA-1 and SHA-256 fingerprints added (after first build)

□ Backend (.env configured)
  ├── □ DATABASE_URL points to RDS (NOT localhost)
  ├── □ AWS credentials set
  ├── □ FIREBASE_PROJECT_ID set
  ├── □ firebase-service-account.json uploaded
  ├── □ alembic upgrade head run
  └── □ systemd service running

□ Apps
  ├── □ EAS account logged in
  ├── □ eas init run in both frontend/ and merchant/
  ├── □ .env has correct API URL
  ├── □ google-services.json in place
  ├── □ app.json package names match Firebase
  └── □ APKs built and tested
```

---

> **That's it!** Follow this guide step by step and you'll have the entire ShowGo project running on a new account. If you get stuck on any step, feel free to ask!
