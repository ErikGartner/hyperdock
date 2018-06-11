VERSION=$(python hyperdock/version.py)
echo "Building images and pushing for version $VERSION"

docker build -t erikgartner/hyperdock-webui:$VERSION -f docker/Dockerfile.webui web/
docker build -t erikgartner/hyperdock-supervisor:$VERSION -f docker/Dockerfile.supervisor .
docker build -t erikgartner/hyperdock-worker:$VERSION -f docker/Dockerfile.worker .
docker tag erikgartner/hyperdock-supervisor:$VERSION erikgartner/hyperdock-supervisor:latest
docker tag erikgartner/hyperdock-worker:$VERSION erikgartner/hyperdock-worker:latest
docker tag erikgartner/hyperdock-webui:$VERSION erikgartner/hyperdock-webui:latest
docker push erikgartner/hyperdock-supervisor:$VERSION
docker push erikgartner/hyperdock-worker:$VERSION
docker push erikgartner/hyperdock-webui:$VERSION
docker push erikgartner/hyperdock-supervisor:latest
docker push erikgartner/hyperdock-worker:latest
docker push erikgartner/hyperdock-webui:latest
