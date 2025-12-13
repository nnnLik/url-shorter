#!/bin/bash
set -e

echo "🔨 Building dev image..."
docker build -t url-shorter:dev --target dev .

echo "📦 Minifying with DockerSlim..."
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/workspace \
  dslim/slim build \
  --target url-shorter:dev \
  --expose 6749 \
  --http-probe=false \
  --continue-after=30 \
  --include-path '/opt/pysetup' \
  --include-path '/opt/app' \
  --include-exe 'python' \
  --include-exe 'uv' \
  --include-exe 'curl' \
  --include-exe 'vim' \
  --include-exe 'htop' \
  url-shorter:dev

echo "🏷️  Tagging slim image..."
docker tag url-shorter.slim:latest url-shorter.slim:dev 2>/dev/null || true
docker tag url-shorter.slim:latest url-shorter:dev 2>/dev/null || true

echo "✅ Done! Minified image ready: url-shorter.slim:dev"
echo "📊 Check sizes with: docker images | grep url-shorter"
