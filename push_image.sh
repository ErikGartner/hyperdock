docker build -t erikgartner/hyperdock-worker:latest -f docker/Dockerfile.worker .
docker build -t erikgartner/hyperdock-supervisor:latest -f docker/Dockerfile.supervisor .
docker push erikgartner/hyperdock-supervisor
docker push erikgartner/hyperdock-worker
