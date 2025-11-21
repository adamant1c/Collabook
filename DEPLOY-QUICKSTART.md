# Production Deployment - Quick Start

## Created Files

### Production Configuration
- [docker-compose.prod.yml](file:///home/alessandro/Project/Collabook/docker-compose.prod.yml) - Production compose with SSL, health checks, resource limits
- [nginx/nginx.conf](file:///home/alessandro/Project/Collabook/nginx/nginx.conf) - Reverse proxy with rate limiting and security
- [DEPLOYMENT.md](file:///home/alessandro/Project/Collabook/DEPLOYMENT.md) - Complete deployment guide (10 parts)

### Modified for Gemini Support
- [backend/app/core/llm_client.py](file:///home/alessandro/Project/Collabook/backend/app/core/llm_client.py#L1-L103) - Dual LLM support (Gemini + OpenAI)
- [backend/requirements.txt](file:///home/alessandro/Project/Collabook/backend/requirements.txt) - Added google-generativeai

## Budget Solution: €5-6/month

✅ **Server**: Hetzner CPX11 (€4.15/month)
✅ **LLM**: Google Gemini Flash (FREE)
✅ **SSL**: Let's Encrypt (FREE)
✅ **Total**: €5-6/month for 50 users

## Quick Deploy Summary

1. **Get Gemini API Key** (10 min)
   - Visit https://aistudio.google.com/
   - Create API key
   
2. **Create Hetzner Server** (15 min)
   - Sign up at https://www.hetzner.com/cloud
   - Create CPX11 server (€4.15/month)
   
3. **Install Docker** (10 min)
   - SSH into server
   - Run Docker install script
   
4. **Deploy Application** (15 min)
   - Clone/copy repository
   - Create `.env` with Gemini key
   - Run `docker compose -f docker-compose.prod.yml up -d`
   
5. **Access** 
   - Frontend: `http://SERVER_IP:8501`
   - API: `http://SERVER_IP:8000/docs`

## Full Guide

See [DEPLOYMENT.md](file:///home/alessandro/Project/Collabook/DEPLOYMENT.md) for complete step-by-step instructions including:
- Screenshot-level detail for each step
- Troubleshooting section
- SSL setup with Let's Encrypt
- Monitoring and maintenance
- Security best practices
