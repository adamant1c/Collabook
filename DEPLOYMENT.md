# Collabook Production Deployment Guide

**Complete Step-by-Step Instructions for Hetzner Cloud**

Total Cost: €5-6/month | Time: ~45 minutes

---

## 📋 Prerequisites

Before starting, you need:
1. Credit/debit card for Hetzner (€4.15/month)
2. Google account (for free Gemini API)
3. Basic terminal knowledge
4. (Optional) Domain name

---

## Part 1: Get Your Google Gemini API Key (10 minutes)

### Step 1.1: Create Google Cloud Project

1. Go to https://aistudio.google.com/
2. Click **"Get API key"** in the top right
3. Sign in with your Google account
4. Click **"Create API key"**
5. Select **"Create API key in new project"**
6. Copy the API key and **save it somewhere safe** (you'll need it later)

✅ **Done!** The API key looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

> **Note**: This is completely FREE for up to 1 million tokens per minute!

---

## Part 2: Create Hetzner Server (15 minutes)

### Step 2.1: Sign Up for Hetzner

1. Go to https://www.hetzner.com/cloud
2. Click **"Sign Up"**
3. Fill in your details
4. Verify your email
5. Add payment method (card required, but only charged €4.15/month)

### Step 2.2: Create SSH Key (if you don't have one)

**On your local computer**, open terminal and run:

```bash
ssh-keygen -t ed25519 -C "collabook-server"
```

Press Enter 3 times (accept defaults, no passphrase needed for this demo)

Then display your public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

**Copy the entire output** (starts with `ssh-ed25519 ...`)

### Step 2.3: Create the Server

1. Log into Hetzner Cloud Console: https://console.hetzner.cloud/
2. Click **"New Project"** → Name it "Collabook"
3. Click **"Add Server"**
4. **Location**: Nuremberg (or Helsinki)
5. **Image**: Ubuntu 22.04
6. **Type**: Shared vCPU → **CPX11** (2 vCPU, 2GB RAM) - €4.15/month
7. **SSH Key**: Click "Add SSH Key" → Paste your public key from Step 2.2
8. **Name**: collabook-prod
9. Click **"Create & Buy Now"**

Wait 1-2 minutes for server to be created.

### Step 2.4: Note Your Server IP

Once created, you'll see your server's **IPv4 address** (e.g., `65.109.123.45`)

**Save this IP address!**

---

## Part 3: Connect to Your Server (5 minutes)

### Step 3.1: SSH Into Server

Open terminal on your local computer and run:

```bash
ssh root@YOUR_SERVER_IP
```

Replace `YOUR_SERVER_IP` with the IP from Step 2.4

Type `yes` when asked about fingerprint.

You should now see a prompt like: `root@collabook-prod:~#`

✅ **You're in!**

---

## Part 4: Install Docker on Server (10 minutes)

### Step 4.1: Update System

Run these commands **on the server**:

```bash
apt update && apt upgrade -y
```

Wait for it to complete (~2 minutes)

### Step 4.2: Install Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

Wait for installation (~3 minutes)

### Step 4.3: Install Docker Compose

```bash
apt install docker-compose-plugin -y
```

### Step 4.4: Verify Installation

```bash
docker --version
docker compose version
```

You should see version numbers. ✅

---

## Part 5: Deploy Collabook (15 minutes)

### Step 5.1: Clone the Repository

**On the server**, run:

```bash
cd /opt
git clone https://github.com/YOUR_USERNAME/Collabook.git
cd Collabook
```

> **Note**: Replace `YOUR_USERNAME/Collabook` with your actual GitHub repository path. If you haven't pushed to GitHub yet, see Alternative Method below.

**Alternative Method** (if code is only on your local machine):

From your **local computer**, copy files to server:

```bash
cd /home/alessandro/Project/Collabook
rsync -avz --exclude '.git' --exclude '__pycache__' . root@YOUR_SERVER_IP:/opt/Collabook/
```

Replace `YOUR_SERVER_IP` with your server's IP.

Then SSH back into server:
```bash
ssh root@YOUR_SERVER_IP
cd /opt/Collabook
```

### Step 5.2: Create Environment File

**On the server**, create the `.env` file:

```bash
nano .env
```

Paste this content, **replacing the placeholders**:

```bash
# Google Gemini API Key (from Part 1)
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE

# Database Password (choose a strong password)
DB_PASSWORD=change_this_to_random_password_123

# Redis Password (choose a strong password)
REDIS_PASSWORD=change_this_to_another_random_password_456

# OpenAI (optional, leave empty if not using)
OPENAI_API_KEY=
```

**Important**: Replace:
- `YOUR_GEMINI_API_KEY_HERE` with your API key from Part 1
- `change_this_to_random_password_123` with a random password
- `change_this_to_another_random_password_456` with another random password

Save and exit:
- Press `Ctrl + O` (to save)
- Press `Enter`
- Press `Ctrl + X` (to exit)

### Step 5.3: Start the Application

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

This will:
- Build the Docker images (~5 minutes first time)
- Download PostgreSQL and Redis images
- Start all services

Watch the logs to confirm everything started:

```bash
docker compose -f docker-compose.prod.yml logs -f
```

Look for:
- `✓ Using Google Gemini Flash (FREE)` ← This means LLM is working!
- `Application startup complete` ← Backend is ready
- Streamlit URL messages ← Frontend is ready

Press `Ctrl + C` to stop watching logs (services keep running)

### Step 5.4: Verify Services Are Running

```bash
docker compose -f docker-compose.prod.yml ps
```

You should see 6 services running:
- `db` (PostgreSQL)
- `redis`
- `backend`
- `frontend`
- `nginx`
- `certbot`

All should show "Up" status. ✅

---

## Part 6: Configure Firewall (5 minutes)

### Step 6.1: Enable UFW Firewall

**On the server**:

```bash
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
```

Type `y` when asked to proceed.

### Step 6.2: Verify Firewall

```bash
ufw status
```

Should show ports 22, 80, 443 as ALLOW. ✅

---

## Part 7: Access Your Application

### Step 7.1: Test HTTP Access

Open your web browser and go to:

```
http://YOUR_SERVER_IP:8501
```

Replace `YOUR_SERVER_IP` with your server IP.

You should see the **Collabook** homepage! 🎉

### Step 7.2: Test Backend API

Go to:

```
http://YOUR_SERVER_IP:8000/docs
```

You should see the **FastAPI documentation** page.

---

## Part 8: Set Up SSL (Optional but Recommended)

> **Note**: Skip this if you don't have a domain name. The app works fine over HTTP for testing.

### Step 8.1: Point Domain to Server

In your domain registrar (e.g., Namecheap, GoDaddy):

1. Create an **A record**:
   - Name: `@` (or `collabook`)
   - Type: A
   - Value: YOUR_SERVER_IP
   - TTL: Automatic

Wait 5-10 minutes for DNS propagation.

Verify with:
```bash
ping yourdomain.com
```

### Step 8.2: Update Nginx Config

**On the server**:

```bash
nano /opt/Collabook/nginx/nginx.conf
```

Find this line (appears twice):
```
ssl_certificate /etc/letsencrypt/live/DOMAIN/fullchain.pem;
```

Replace `DOMAIN` with your actual domain (e.g., `collabook.com`)

Save with `Ctrl + O`, `Enter`, `Ctrl + X`

### Step 8.3: Get SSL Certificate

```bash
cd /opt/Collabook
docker compose -f docker-compose.prod.yml exec certbot certbot certonly --webroot -w /var/www/certbot -d yourdomain.com --email your@email.com --agree-tos --no-eff-email
```

Replace:
- `yourdomain.com` with your domain
- `your@email.com` with your email

### Step 8.4: Restart Nginx

```bash
docker compose -f docker-compose.prod.yml restart nginx
```

### Step 8.5: Access Via HTTPS

Go to:
```
https://yourdomain.com
```

You should see a secure connection! 🔒

---

## Part 9: Monitor Your Application

### View Logs

```bash
cd /opt/Collabook

# All services
docker compose -f docker-compose.prod.yml logs -f

# Just backend
docker compose -f docker-compose.prod.yml logs -f backend

# Just frontend
docker compose -f docker-compose.prod.yml logs -f frontend
```

Press `Ctrl + C` to exit.

### Check Resource Usage

```bash
docker stats
```

Shows CPU, memory, network usage for each container.

### Restart Services

```bash
cd /opt/Collabook
docker compose -f docker-compose.prod.yml restart
```

### Stop Services

```bash
docker compose -f docker-compose.prod.yml down
```

### Start Services Again

```bash
docker compose -f docker-compose.prod.yml up -d
```

---

## Part 10: Test the Application

### Step 10.1: Create a Character

1. Go to `http://YOUR_SERVER_IP:8501`
2. Fill in character details:
   - Name: Elara
   - Profession: Wandering Mage
   - Description: A curious mage seeking ancient knowledge
   - Avatar: Tall with silver hair and blue robes
3. Click **"Create Character"**

### Step 10.2: Create a Story

1. Click **"Create New Story"** tab
2. Fill in:
   - Title: The Forgotten Temple
   - Genre: Fantasy
   - World: An ancient world where magic is fading and forgotten temples hold lost secrets
3. Click **"Create Story"**

### Step 10.3: Play!

1. You'll see your insertion message
2. Type an action: "I examine the temple entrance for any markings or clues"
3. Click **"🎭 Act"**
4. Wait for the AI to generate narration (~3-5 seconds)
5. Read the story response!

✅ **It works!** The AI is generating your story!

---

## Troubleshooting

### Problem: Can't access the site

**Check if services are running:**
```bash
docker compose -f docker-compose.prod.yml ps
```

**Restart everything:**
```bash
docker compose -f docker-compose.prod.yml restart
```

### Problem: "No LLM provider configured" error

**Check logs:**
```bash
docker compose -f docker-compose.prod.yml logs backend
```

**Verify .env file:**
```bash
cat .env
```

Make sure `GEMINI_API_KEY` is set correctly.

**Restart backend:**
```bash
docker compose -f docker-compose.prod.yml restart backend
```

### Problem: Database connection errors

**Reset database:**
```bash
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml up -d
```

**Warning**: This deletes all data!

### Problem: Out of memory

**Check memory usage:**
```bash
free -h
```

**Reduce resource limits** in `docker-compose.prod.yml` if needed.

### Problem: Slow responses

This is normal for the first request (cold start). Subsequent requests are faster.

If still slow, check:
```bash
docker stats
```

Look for high CPU or memory usage.

---

## Updating the Application

### Step 1: SSH into server

```bash
ssh root@YOUR_SERVER_IP
cd /opt/Collabook
```

### Step 2: Pull latest changes

```bash
git pull origin main
```

Or copy new files from local:
```bash
# From your local computer:
rsync -avz --exclude '.git' . root@YOUR_SERVER_IP:/opt/Collabook/
```

### Step 3: Rebuild and restart

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Monitoring Costs

### Hetzner: €4.15/month (automatic billing)

Check your bill: https://console.hetzner.cloud/

### Gemini API: FREE

Monitor usage: https://aistudio.google.com/

Check quota limits (should be well below for 50 users).

### Total: €5-6/month ✅

---

## Security Best Practices

### Change Default Passwords

The `.env` file has passwords. Make sure they're strong and unique!

### Enable Automatic Updates

```bash
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades
```

Select "Yes"

### Regular Backups

**Backup database:**
```bash
docker compose -f docker-compose.prod.yml exec db pg_dump -U collabook collabook_db > backup.sql
```

**Restore database:**
```bash
docker compose -f docker-compose.prod.yml exec -T db psql -U collabook collabook_db < backup.sql
```

Store backups safely!

---

## Next Steps

### Add More Features

- Modify code locally
- Test with `docker-compose up`
- Deploy to production (see Updating section)

### Monitor Usage

- Watch server logs
- Check Gemini API quota
- Monitor server resources

### Scale Up

When >100 users:
- Upgrade to larger Hetzner instance
- Consider paid LLM tier (DeepSeek ~€10/month)
- Add caching optimizations

---

## Quick Reference Commands

```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Go to app directory
cd /opt/Collabook

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Restart services
docker compose -f docker-compose.prod.yml restart

# Stop everything
docker compose -f docker-compose.prod.yml down

# Start everything
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps

# Check resources
docker stats
```

---

## Success! 🎉

Your Collabook application is now running in production!

- **URL**: `http://YOUR_SERVER_IP:8501`
- **API Docs**: `http://YOUR_SERVER_IP:8000/docs`
- **Cost**: €5-6/month
- **Capacity**: 50 concurrent users
- **LLM**: Google Gemini Flash (FREE)

Enjoy your collaborative storytelling platform!

---

## Support

If you encounter issues:

1. Check the Troubleshooting section above
2. Review logs: `docker compose -f docker-compose.prod.yml logs`
3. Verify all services are running: `docker compose -f docker-compose.prod.yml ps`
4. Check Gemini API key is correct
5. Ensure server has internet access

For Hetzner support: https://docs.hetzner.com/
For Gemini API: https://ai.google.dev/docs
