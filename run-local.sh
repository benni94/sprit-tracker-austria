#!/bin/bash

# Sprit-Tracker Local Docker Runner
# Opens the app in Brave browser after starting the container
#
# Usage:
#   ./run-local.sh         # Normal mode (build image, run container)
#   ./run-local.sh --dev   # Dev mode (hot-reload on file save)

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTAINER_NAME="sprit-test"
PORT="8085"
URL="http://localhost:${PORT}"
DEV_MODE=false

# Parse arguments
if [ "$1" = "--dev" ]; then
    DEV_MODE=true
fi

echo "🚀 Sprit-Tracker Local Runner"

if [ "$DEV_MODE" = true ]; then
    echo "🔥 DEV MODE: Hot-reload enabled (changes apply on file save)"
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Stop and remove existing container if it exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "🛑 Stopping existing container..."
    docker stop "${CONTAINER_NAME}" >/dev/null 2>&1
    docker rm "${CONTAINER_NAME}" >/dev/null 2>&1
    echo "✅ Existing container removed"
fi

if [ "$DEV_MODE" = false ]; then
    # Build the image (only in normal mode)
    echo "🔨 Building Docker image..."
    cd "${PROJECT_DIR}" || exit 1
    docker build -t sprit-tracker . >/dev/null 2>&1

    if [ $? -ne 0 ]; then
        echo "❌ Docker build failed"
        exit 1
    fi
    echo "✅ Image built"
fi

# Run the container
echo "🏃 Starting container on port ${PORT}..."

if [ "$DEV_MODE" = true ]; then
    # Dev mode: mount local files and enable Flask debug
    docker run -d \
        --name "${CONTAINER_NAME}" \
        -p "${PORT}:5000" \
        -v "${PROJECT_DIR}:/app" \
        -e FLASK_DEBUG=true \
        sprit-tracker >/dev/null 2>&1
else
    # Normal mode: use built image
    docker run -d \
        --name "${CONTAINER_NAME}" \
        -p "${PORT}:5000" \
        sprit-tracker >/dev/null 2>&1
fi

if [ $? -ne 0 ]; then
    echo "❌ Failed to start container"
    exit 1
fi
echo "✅ Container running"

# Wait a moment for Flask to start
echo "⏳ Waiting for app to start..."
sleep 2

# Check if app is responding
if curl -s "${URL}" >/dev/null 2>&1; then
    echo "🌐 Opening ${URL} in Brave..."
    open -a "Brave Browser" "${URL}"
else
    echo "⚠️ App might not be ready yet. Opening ${URL} anyway..."
    open -a "Brave Browser" "${URL}"
fi

echo ""
echo "✨ Done! The app should be open in Brave."

if [ "$DEV_MODE" = true ]; then
    echo ""
    echo "📝 Dev mode active: Edit app.py or templates/index.html and save."
    echo "   Flask will auto-reload. Just refresh your browser to see changes."
fi

echo ""
echo "To stop the container later, run:"
echo "  docker stop ${CONTAINER_NAME} && docker rm ${CONTAINER_NAME}"
