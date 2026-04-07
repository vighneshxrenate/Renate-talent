#!/bin/bash
set -e

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_DIR"

echo "=== Renate Talent Deployment ==="
echo "Directory: $PROJECT_DIR"
echo ""

# Check env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: $ENV_FILE not found."
    echo "Copy .env.production.example to .env.production and fill in your values."
    exit 1
fi

# Check SSL certs exist (skip on first deploy)
if [ ! -d "/etc/letsencrypt/live/renate.in" ] && ! docker volume inspect "$(basename "$PROJECT_DIR")_certbot-conf" >/dev/null 2>&1; then
    echo "WARNING: No SSL certificates found."
    echo "Run the initial SSL setup first (see DEPLOYMENT.md Step 5)."
    echo ""
fi

echo "1/4 Pulling latest code..."
git pull origin main

echo ""
echo "2/4 Building Docker images..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build

echo ""
echo "3/4 Starting services..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

echo ""
echo "4/4 Waiting for health checks..."
sleep 10

# Check service health
HEALTHY=true
for SERVICE in db backend frontend nginx; do
    STATUS=$(docker compose -f "$COMPOSE_FILE" ps --format json "$SERVICE" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('Health','unknown'))" 2>/dev/null || echo "unknown")
    if [ "$STATUS" = "healthy" ] || [ "$SERVICE" = "nginx" ]; then
        echo "  $SERVICE: OK"
    else
        echo "  $SERVICE: $STATUS (may still be starting)"
        HEALTHY=false
    fi
done

echo ""
if [ "$HEALTHY" = true ]; then
    echo "=== Deployment successful ==="
else
    echo "=== Some services still starting. Check again in 30s: ==="
    echo "  docker compose -f $COMPOSE_FILE ps"
fi

echo ""
echo "Useful commands:"
echo "  Logs:    docker compose -f $COMPOSE_FILE logs -f"
echo "  Status:  docker compose -f $COMPOSE_FILE ps"
echo "  Restart: docker compose -f $COMPOSE_FILE restart"
echo "  Stop:    docker compose -f $COMPOSE_FILE down"
