#!/bin/bash
set -e

IMAGE_NAME="url-shorter:dev"
SLIM_IMAGE="url-shorter.slim:dev"

if command -v md5sum >/dev/null 2>&1; then
    DOCKERFILE_HASH=$(md5sum Dockerfile pyproject.toml 2>/dev/null | md5sum | cut -d' ' -f1)
elif command -v md5 >/dev/null 2>&1; then
    DOCKERFILE_HASH=$(md5 -q Dockerfile pyproject.toml 2>/dev/null | md5 -q)
else
    echo "⚠️  md5/md5sum not found, skipping hash check"
    DOCKERFILE_HASH=""
fi
HASH_FILE=".slim-build-hash"

if [ -n "$DOCKERFILE_HASH" ] && [ -f "$HASH_FILE" ]; then
    OLD_HASH=$(cat "$HASH_FILE")
    if [ "$DOCKERFILE_HASH" = "$OLD_HASH" ]; then
        if docker images "$SLIM_IMAGE" --format "{{.Repository}}:{{.Tag}}" 2>/dev/null | grep -q "$SLIM_IMAGE"; then
            echo "✅ Slim image is up to date"
            exit 0
        fi
    fi
fi

echo "🔨 Building and minifying image..."
make slim-build

if [ -n "$DOCKERFILE_HASH" ]; then
    echo "$DOCKERFILE_HASH" > "$HASH_FILE"
fi
echo "✅ Slim image ready!"
