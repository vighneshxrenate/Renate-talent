# Deploying Renate Talent to DigitalOcean

Target: DigitalOcean Droplet (2 vCPU, 2GB RAM, $12/mo). Domain: renate.in

## Step 1: Create the Droplet

1. Sign up at [digitalocean.com](https://www.digitalocean.com) (credit card, instant)
2. Create a new Droplet:
   - **Region**: Choose closest to your users (e.g., Bangalore, Singapore, Frankfurt)
   - **Image**: Ubuntu 24.04 LTS
   - **Size**: Basic → Regular → **$12/mo** (2 vCPU, 2GB RAM, 60GB SSD)
   - **Authentication**: SSH Key (add your public key)
   - **Hostname**: `renate-talent`
3. Note the Droplet's public IP address

## Step 2: Initial Server Setup

SSH into the server:

```bash
ssh root@YOUR_DROPLET_IP
```

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose plugin
apt install -y docker-compose-plugin

# Verify
docker --version
docker compose version

# Configure firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Add swap (important for 2GB RAM)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Create deploy user
adduser deploy
usermod -aG docker deploy
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
```

## Step 3: Point Domain to Droplet

In your DNS provider (wherever renate.in is registered):

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | YOUR_DROPLET_IP | 300 |
| A | www | YOUR_DROPLET_IP | 300 |

Wait for DNS propagation (check: `dig renate.in`).

## Step 4: Clone and Configure

```bash
ssh deploy@YOUR_DROPLET_IP

git clone https://github.com/YOUR_ORG/Renate-talent.git
cd Renate-talent

cp .env.production.example .env.production
nano .env.production
```

Fill in real values:

```
POSTGRES_PASSWORD=<generate: openssl rand -base64 32>
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=<your supabase service role key>
ALLOWED_ORIGINS=https://renate.in
NEXT_PUBLIC_API_URL=https://renate.in/api
ENVIRONMENT=production
MAX_UPLOAD_SIZE_MB=5
```

## Step 5: SSL Certificate Setup

Get your initial SSL certificate before starting nginx:

```bash
# Get certificate using standalone mode
docker run --rm -it \
  -v "$(pwd)/certbot-conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot-www:/var/www/certbot" \
  -p 80:80 \
  certbot/certbot certonly \
  --standalone \
  -d renate.in \
  -d www.renate.in \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email

# Copy certs into Docker volume
docker volume create renate-talent_certbot-conf 2>/dev/null || true
docker run --rm \
  -v "$(pwd)/certbot-conf:/source:ro" \
  -v "renate-talent_certbot-conf:/dest" \
  alpine sh -c "cp -a /source/. /dest/"

# Clean up temp directory
rm -rf certbot-conf certbot-www
```

## Step 6: Deploy

```bash
./scripts/deploy.sh
```

This builds all images, starts services, runs migrations, and verifies health checks.

## Step 7: Verify

```bash
# All services running
docker compose -f docker-compose.prod.yml ps

# Redirect works
curl -I http://renate.in/
# Expected: 301 -> https://renate.in/talent

# API health
curl https://renate.in/api/health
# Expected: {"status": "ok", "database": "connected"}

# Frontend loads
curl -I https://renate.in/talent
# Expected: 200 OK

# SSL valid
curl -vI https://renate.in 2>&1 | grep "subject:"

# Logs clean
docker compose -f docker-compose.prod.yml logs backend --tail 20

# Backup running
docker compose -f docker-compose.prod.yml exec backup ls /backups/
```

## Ongoing Operations

### View logs
```bash
docker compose -f docker-compose.prod.yml logs -f              # All
docker compose -f docker-compose.prod.yml logs -f backend      # Backend only
```

### Redeploy after code changes
```bash
cd Renate-talent && ./scripts/deploy.sh
```

### Manual database backup
```bash
docker compose -f docker-compose.prod.yml exec backup /usr/local/bin/backup-db.sh
```

### Restore from backup
```bash
docker compose -f docker-compose.prod.yml exec backup ls -la /backups/
docker compose -f docker-compose.prod.yml exec backup sh -c "gunzip -c /backups/FILENAME.sql.gz | psql"
```

### Renew SSL manually
```bash
docker compose -f docker-compose.prod.yml exec certbot certbot renew
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### Resize droplet (if needed later)
1. Go to DigitalOcean console → Droplet → Resize
2. Choose new plan (e.g., $24/mo for 4 vCPU / 4GB)
3. Power cycle — done, no data loss

### Check resources
```bash
free -h          # Memory usage
df -h            # Disk usage
docker stats     # Per-container resource usage
```
