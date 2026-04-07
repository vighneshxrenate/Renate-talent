#!/bin/bash
# deploy/setup.sh — Fresh Hetzner Ubuntu 22.04 server setup
# Run once as root: bash setup.sh
set -euo pipefail

DOMAIN="${DOMAIN:-renate.in}"
REPO="${REPO:-https://github.com/vighneshxrenate/Renate-talent.git}"
APP_DIR="/opt/renate-talent"

echo "==> Installing Docker..."
apt-get update -qq
apt-get install -y -qq curl git openssl

curl -fsSL https://get.docker.com | sh
systemctl enable --now docker

echo "==> Cloning repo..."
git clone "$REPO" "$APP_DIR" || (cd "$APP_DIR" && git pull)
cd "$APP_DIR"

echo "==> Setting up .env..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    # Generate a random admin key
    ADMIN_KEY=$(openssl rand -hex 32)
    DB_PASS=$(openssl rand -hex 24)
    sed -i "s/ADMIN_API_KEY=.*/ADMIN_API_KEY=$ADMIN_KEY/" backend/.env
    sed -i "s|ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=https://$DOMAIN|" backend/.env
    cat >> .env.prod <<EOF
POSTGRES_USER=renate
POSTGRES_PASSWORD=$DB_PASS
POSTGRES_DB=renate_talent
NEXT_PUBLIC_API_URL=https://$DOMAIN/talent/api
EOF
    echo ""
    echo "!!! Generated credentials — save these now !!!"
    echo "  ADMIN_API_KEY=$ADMIN_KEY"
    echo "  DB_PASS=$DB_PASS"
    echo ""
    # Also patch the backend .env DATABASE_URL
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://renate:$DB_PASS@db:5432/renate_talent|" backend/.env
fi

echo "==> Getting SSL certificate (Let's Encrypt)..."
mkdir -p nginx/ssl
apt-get install -y -qq certbot
certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos -m "admin@$DOMAIN" || true

if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" nginx/ssl/fullchain.pem
    cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem"   nginx/ssl/privkey.pem
else
    echo "WARNING: Could not obtain SSL cert — generating self-signed for now"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/privkey.pem \
        -out    nginx/ssl/fullchain.pem \
        -subj "/CN=$DOMAIN"
fi

echo "==> Running database migrations..."
docker compose run --rm backend alembic upgrade head

echo "==> Starting stack..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

echo "==> Setting up backup cron..."
cp deploy/backup.sh /usr/local/bin/renate-backup
chmod +x /usr/local/bin/renate-backup
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/renate-backup >> /var/log/renate-backup.log 2>&1") | crontab -

echo ""
echo "==> Done! App is live at https://$DOMAIN/talent"
