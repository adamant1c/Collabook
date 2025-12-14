#!/bin/bash
# Generate self-signed SSL certificate for Collabook HTTPS

set -e

echo "🔐 Generating self-signed SSL certificate for Collabook..."

# Create ssl directory if it doesn't exist
mkdir -p ssl

# Generate private key and certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/selfsigned.key \
  -out ssl/selfsigned.crt \
  -subj "/C=IT/ST=Italy/L=City/O=Collabook/OU=Development/CN=collabook.local" \
  -addext "subjectAltName=DNS:localhost,DNS:collabook.local,IP:127.0.0.1"

# Set proper permissions
chmod 600 ssl/selfsigned.key
chmod 644 ssl/selfsigned.crt

echo "✅ Certificate generated successfully!"
echo ""
echo "📁 Files created:"
echo "  - ssl/selfsigned.key (private key)"
echo "  - ssl/selfsigned.crt (certificate)"
echo ""
echo "⚠️  Note: This is a self-signed certificate. Browsers will show a security warning."
echo "    You'll need to accept the warning to access the site via HTTPS."
echo ""
echo "🔄 Next steps:"
echo "  1. Update nginx/nginx.conf to use these certificates"
echo "  2. Restart nginx: docker-compose restart nginx"
echo "  3. Access your site via https://localhost or https://<your-server-ip>"
