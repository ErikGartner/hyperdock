#!/bin/bash
#
# This automatically pushes the latest release to DockerHub on Travis.
#
set -e

# Login to DockerHub
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

VERSION=$TRAVIS_TAG
echo "Releasing version $TRAVIS_TAG to Docker"

echo "Building Docker images"
docker build -t erikgartner/hyperdock-webui:$VERSION -f "docker/Dockerfile.webui" web/
docker build -t erikgartner/hyperdock-supervisor:$VERSION -f "docker/Dockerfile.supervisor" .
docker build -t erikgartner/hyperdock-worker:$VERSION -f "docker/Dockerfile.worker" .
docker build -t erikgartner/hyperdock-demo:$VERSION -f "docker/Dockerfile.template" .

echo "Tagging Docker images"
docker tag erikgartner/hyperdock-supervisor:$VERSION erikgartner/hyperdock-supervisor:latest
docker tag erikgartner/hyperdock-worker:$VERSION erikgartner/hyperdock-worker:latest
docker tag erikgartner/hyperdock-webui:$VERSION erikgartner/hyperdock-webui:latest
docker tag erikgartner/hyperdock-demo:$VERSION erikgartner/hyperdock-demo:latest

echo "Pushing Docker images"
docker push erikgartner/hyperdock-supervisor:$VERSION
docker push erikgartner/hyperdock-worker:$VERSION
docker push erikgartner/hyperdock-webui:$VERSION
docker push erikgartner/hyperdock-demo:$VERSION
docker push erikgartner/hyperdock-supervisor:latest
docker push erikgartner/hyperdock-worker:latest
docker push erikgartner/hyperdock-webui:latest
docker push erikgartner/hyperdock-demo:latest
