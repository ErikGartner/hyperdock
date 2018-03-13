# HyperDock (aka DeepDock)

![HyperDock logo](extra/banner.png)

HyperDock is a software that runs makes trying out different hyper parameters simple.

All you need to do is make sure the software you want to optimize can be started from a
docker image.




## Running
```bash
# Mongodb
docker run --name hyperdock-mongo -p 27017:27017 -d mongo # --bind_ip_all

# Supervisor
docker run -it --rm erikgartner/hyperdock-supervisor:latest --name trial1 --image erikgartner/hyperdock-test --config_module example --trials 5 --mongo mongo://172.17.0.1:27017/hyperdock/jobs # -v /folderwithconfig/:/app/hyperdock/config:ro

# Worker
docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd)/results:/results -e HYPERDOCK_RESULT_DIR=$(pwd)/results -e HYPERDOCK_DATA_DIR=$(pwd)/data -e MONGO_URL=mongo://172.17.0.1:27017/hyperdock -e HYPERDOCK_RUNTIME="" -e HYPERDOCK_ENV="[]" erikgartner/hyperdock-worker:latest
```

## Building

The latest version should be available from Docker Hub but you can also buiild
it yourself.

```bash
docker build -t erikgartner/hyperdock-worker:latest -f docker/Dockerfile.worker .
docker build -t erikgartner/hyperdock-supervisor:latest -f docker/Dockerfile.supervisor .
```
