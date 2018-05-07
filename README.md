# Hyperdock

![Hyperdock logo](extra/banner.png)

Hyperdock is a software that runs makes trying out different hyper parameters simple. All you need to do is make sure the software you want to optimize can be started from a docker image.

## Philosophy

The main idea for Hyperdock is universal hyperparameter with the only dependency being that the optimization target runs in a Docker image.

![Hyperdock diagram](extra/diagram.png)

The **Hyperdock supervisor** reads a configuration module that declares which parameters to optimize and their ranges.
It then samples from the parameter space and creates a set of parameter combination to be evaluated. These trials are stored in a **mongo database**.

The **Hyperdock workers** fetches parameter combinations from the database and then executes the **target image** with these parameters as to evaluate the combination. This is repeated a number of time and then **Hyperdock** returns the best parameter combination. Since the workers talk connect directly with the database they can be distributed as long as they can access any data needed by the **target image**.

The **target image** receives parameter in the json file `/hyperdock/params.json` as well as data and a folder to write result to. Once the image has evaluated the parameters it simply writes the loss to file `/hyperdock/loss.json`. See the [Dockfile template](docker/Dockerfile.template) for an example.

## Running
To start a Mongo database you can use this simple Docker command or use any normal Mongo instance.

```bash
# Starts mongo db, add --bind_ip_all to listen on all interfaces.
docker run --name hyperdock-mongo -p 27017:27017 -d mongo
```

Then to start the **Hyperdock supervisor** run the following command.
```bash
# Supervisor
docker run -it --rm -v /folderwithconfig/:/app/hyperdock/config:ro erikgartner/hyperdock-supervisor:latest --name trial1 --image erikgartner/hyperdock-test --config_module example --trials 5 --mongo mongo://172.17.0.1:27017/hyperdock/jobs
```

The following important settings exists:

- `-v /folderwithconfig/:/app/hyperdock/config:ro` points to the folder containing the Hyperdock configuration modules
- `--name trial1` sets the name of the trial. Each trial should have a unique name
- `--image erikgartner/hyperdock-test` sets the _target image_
- `--config_module example` sets which configuration module to use
- ` --mongo mongo://172.17.0.1:27017/hyperdock/jobs` sets which Mongo database to connect to
- `--trials 5` sets the number of retries incase of errors in the target image container.

To start the **Hyperdock worker** run the folling command.
```bash
# Worker
docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock -v $(pwd)/results:/results -e HYPERDOCK_RESULT_DIR=$(pwd)/results -e HYPERDOCK_DATA_DIR=$(pwd)/data -e MONGO_URL=mongo://172.17.0.1:27017/hyperdock -e HYPERDOCK_RUNTIME="" -e HYPERDOCK_ENV="[]" erikgartner/hyperdock-worker:latest
```

## Building

The latest version should be available from Docker Hub but you can also build it yourself.

```bash
docker build -t erikgartner/hyperdock-worker:latest -f docker/Dockerfile.worker .
docker build -t erikgartner/hyperdock-supervisor:latest -f docker/Dockerfile.supervisor .
```
