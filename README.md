# HyperDock (aka DeepDock)

![HyperDock logo](extra/banner.png)


## Building

```bash
docker build -t erikgartner/hyperdock-worker:latest -f docker/Dockerfile.worker .
docker build -t erikgartner/hyperdock-supervisor:latest -f docker/Dockerfile.supervisor .
```

## Running
```bash
# Mongodb
docker run --name hyperdock-mongo -p 27017:27017 -d mongo # --bind_ip_all

# Supervisor
docker run -it --rm erikgartner/hyperdock-supervisor:latest --name test --image erikgartner/hyperdock-test --config_module example --trials 5 --mongo mongo://172.17.0.1:27017/hyperdock/jobs

# Worker
docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd)/results:/results -e HYPERDOCK_RESULT_DIR=$(pwd)/results -e HYPERDOCK_DATA_DIR=$(pwd)/data -e MONGO_URL=mongo://172.17.0.1:27017/hyperdock erikgartner/hyperdock-worker:latest
```
