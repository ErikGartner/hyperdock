docker build -t erikgartner/hyperdock-webui:latest -f docker/Dockerfile.webui web/
docker build -t erikgartner/hyperdock-supervisor:latest -f docker/Dockerfile.supervisor .
docker build -t erikgartner/hyperdock-worker:latest -f docker/Dockerfile.worker .
docker push erikgartner/hyperdock-supervisor
docker push erikgartner/hyperdock-worker
docker push erikgartner/hyperdock-webui
