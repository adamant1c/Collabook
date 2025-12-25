---
description: How to test locally and deploy the Django frontend
---

# 🚀 Django Frontend Deployment Guide

## 💻 Local Testing (Manual)

Follow these steps to test the new Django frontend on your local machine without Docker.

1. **Prepare Environment**
   ```bash
   # Create a virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   # Run Django migrations (creates local sqlite db)
   python manage.py migrate
   ```

3. **Run the Server**
   ```bash
   # Start the development server
   python manage.py runserver
   ```

4. **Verify**
   - Open [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - Ensure the backend is running (locally or via Docker) for full functionality.

---

## ☁️ Production Deployment (Remote VM)

Follow these steps after you have pushed your changes to the repository.

1. **Access Remote VM**
   ```bash
   ssh username@your-vm-ip
   ```

2. **Update Code**
   ```bash
   cd /path/to/Collabook
   git pull origin main
   ```

3. **Rebuild Containers**
   ```bash
   # Stop and remove old containers
   docker compose down
   
   # Build and start with the new Django frontend
   docker compose up --build -d
   ```

4. **Post-Deployment Checks**
   ```bash
   # Check container status
   docker compose ps
   
   # Check frontend logs if issues occur
   docker compose logs frontend
   ```

5. **Access**
   - The application will be available on the port configured in `docker-compose.yml` (default: 3000).
