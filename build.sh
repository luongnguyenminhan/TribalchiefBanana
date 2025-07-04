#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Image name
IMAGE_NAME="vihatet5-api"
VERSION="${1:-latest}"

echo -e "${BLUE}🚀 Building ViHateT5 Docker Image${NC}"
echo -e "${YELLOW}Image: ${IMAGE_NAME}:${VERSION}${NC}"

# Build with progress
echo -e "${BLUE}📦 Building Docker image...${NC}"
docker build \
  -t "${IMAGE_NAME}:${VERSION}" \
  -t "${IMAGE_NAME}:latest" \
  --progress=plain \
  .

echo -e "${GREEN}✅ Build completed successfully!${NC}"

# Show image info
echo -e "${BLUE}📊 Image Information:${NC}"
docker images "${IMAGE_NAME}:${VERSION}"

# Test if image works
echo -e "${BLUE}🧪 Testing image...${NC}"
if docker run --rm "${IMAGE_NAME}:${VERSION}" python -c "import main; print('✅ Import test passed')"; then
    echo -e "${GREEN}✅ Image test successful!${NC}"
else
    echo -e "${RED}❌ Image test failed!${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Docker image ${IMAGE_NAME}:${VERSION} ready!${NC}"
echo -e "${YELLOW}Run with: docker run -p 8000:8000 ${IMAGE_NAME}:${VERSION}${NC}" 