#!/bin/bash

# Setup Let's Encrypt for Collabook
# This script automates the process of obtaining a Let's Encrypt certificate
# and configuring Nginx to use it.

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Collabook Let's Encrypt Setup ===${NC}"
echo "This script will guide you through setting up a free SSL certificate."
echo ""

# 1. Gather Information
read -p "Enter your domain name (e.g., collabook.example.com): " DOMAIN
read -p "Enter your email address (for renewal notices): " EMAIL

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo -e "${RED}Error: Domain and Email are required.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Configuring for domain: $DOMAIN${NC}"
echo -e "${YELLOW}Email: $EMAIL${NC}"
echo ""

# 2. Stop Nginx to free up port 80
echo -e "${YELLOW}Stopping Nginx...${NC}"
docker compose -f docker-compose.prod.yml stop nginx

# 3. Run Certbot
echo -e "${YELLOW}Requesting certificate from Let's Encrypt...${NC}"
echo "This may take a minute."

docker compose -f docker-compose.prod.yml run --rm --entrypoint certbot -p 80:80 certbot certonly \
    --standalone \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --non-interactive

if [ $? -ne 0 ]; then
    echo -e "${RED}Certbot failed to obtain a certificate.${NC}"
    echo "Please check your domain DNS settings and try again."
    echo "Restarting Nginx..."
    docker compose -f docker-compose.prod.yml start nginx
    exit 1
fi

echo -e "${GREEN}Certificate obtained successfully!${NC}"

# 4. Update Nginx Configuration
echo -e "${YELLOW}Updating Nginx configuration...${NC}"

NGINX_CONF="./nginx/nginx.conf"
BACKUP_CONF="./nginx/nginx.conf.bak"

# Backup existing config
cp "$NGINX_CONF" "$BACKUP_CONF"

# Replace placeholders
# 1. Comment out self-signed certs
sed -i 's|ssl_certificate /etc/nginx/ssl/selfsigned.crt;|# ssl_certificate /etc/nginx/ssl/selfsigned.crt;|g' "$NGINX_CONF"
sed -i 's|ssl_certificate_key /etc/nginx/ssl/selfsigned.key;|# ssl_certificate_key /etc/nginx/ssl/selfsigned.key;|g' "$NGINX_CONF"

# 2. Uncomment and update Let's Encrypt paths
# We use a temporary placeholder replacement to handle the commented out lines
sed -i "s|# ssl_certificate /etc/letsencrypt/live/DOMAIN/fullchain.pem;|ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;|g" "$NGINX_CONF"
sed -i "s|# ssl_certificate_key /etc/letsencrypt/live/DOMAIN/privkey.pem;|ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;|g" "$NGINX_CONF"

# 5. Restart Nginx
echo -e "${YELLOW}Restarting Nginx...${NC}"
docker compose -f docker-compose.prod.yml start nginx

echo ""
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo "Your site should now be accessible via HTTPS."
echo "Test it here: https://$DOMAIN"
echo ""
echo "To verify locally:"
echo "curl -I https://$DOMAIN"
