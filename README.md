# Hyperdock
![Hyperdock logo](extra/banner.png)

*A simple framework for distributed hyperparameter optimization in Docker. All you need to do is make sure the software you want to optimize can be run in a Docker container.*

## Philosophy

The main idea of Hyperdock is universal hyperparameter optimization with minimal dependencies (i.e. Docker).

![Hyperdock diagram](extra/diagram.png)

The **Hyperdock supervisor** reads a configuration module that declares which parameters to optimize and their ranges.
It then samples from the parameter space and creates a set of parameter combination to be evaluated. These trials are stored in a **mongo database**.

The **Hyperdock workers** fetches parameter combinations from the database and then executes the **target image** with these parameters as to evaluate the combination. This is repeated a specified number of time and then **Hyperdock** returns the best parameter combination. Since the workers talk connect directly with the database they can be distributed as long as they can access any data needed by the **target image**.

The **target image** receives the parameters from the json file `/hyperdock/params.json`. Once the target image has evaluated the parameters it simply writes the loss to file `/hyperdock/loss.json`.

## Running
Setting up the Hyperdock system can seem a bit complicated but once it is up it quite easy to use.

#### Mongo database
To start a Mongo database you can use this simple Docker command or use any normal Mongo instance.
```bash
# Starts mongo db, add --bind_ip_all to listen on all interfaces.
docker run --name hyperdock-mongo -p 27017:27017 -d mongo
```

#### Supervisor
Then to start the **Hyperdock supervisor** run the following command:
```bash
# Supervisor
docker run -it --rm \
  -v /folderwithconfig/:/app/hyperdock/config:ro \
  erikgartner/hyperdock-supervisor:latest \
  --name trial1 \
  --image erikgartner/hyperdock-test \
  --config_module example \
  --trials 5 \
  --mongo mongo://172.17.0.1:27017/hyperdock/jobs
```

Options:

- `-v /folderwithconfig/:/app/hyperdock/config:ro` points to the folder containing the Hyperdock configuration modules
- `--name trial1` sets the name of the trial. Each trial should have a unique name
- `--image erikgartner/hyperdock-test` sets the _target image_
- `--config_module example` sets which configuration module to use
- ` --mongo mongo://172.17.0.1:27017/hyperdock/jobs` sets which Mongo database to connect to
- `--trials 5` sets the maximum number of parameter combination to try out.

#### Worker
To start the **Hyperdock worker** run the following command.
```bash
# Worker
docker run -it --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd)/results:/results -e \
  HYPERDOCK_RESULT_DIR=$(pwd)/results \
  -e HYPERDOCK_DATA_DIR=$(pwd)/data \
  -e MONGO_URL=mongo://172.17.0.1:27017/hyperdock \
  -e HYPERDOCK_RUNTIME="" \
  -e HYPERDOCK_ENV="[]" \
  erikgartner/hyperdock-worker:latest
```

Options:

- `-v $(pwd)/results:/results` sets folder to store the results from target image
- `-e HYPERDOCK_RESULT_DIR=$(pwd)/results` should be the same as the above
- `-e HYPERDOCK_DATA_DIR=$(pwd)/data ` the data directory for the target image
- `-e MONGO_URL=mongo://172.17.0.1:27017/hyperdock` sets the URI to the Mongo database
- `-e HYPERDOCK_RUNTIME=""` sets the runtime of the target image, e.g. `nvidia`
- `-e HYPERDOCK_ENV="[]"` sets the environment variables for the target image in Docker argument list format

#### Target Image
For the **Target Image** the following volumes are mounted:

- `/hyperdock/`
  - `loss.json` write the final loss here
  - `params.json` contains the parameters for this run
  - `out/` use this to write any other files to the result folder
- `/data` a read only folder that contains any external data needed

See the [Dockfile template](docker/Dockerfile.template) for an example.

#### Hyperdock Configuration Module
The Hyperdock configuration module is a simple Python 3 module that exposes a
`SPACE` variable containing a [Hyperopt](http://hyperopt.github.io/hyperopt/) parameter space.

See [example.py](hyperdock/config/example.py) for an example.

## Building

The latest version should be available from Docker Hub just use the pull command:
```bash
docker pull erikgartner/hyperdock-worker:latest
docker pull erikgartner/hyperdock-supervisor:latest
```

However if you like you can also build the images yourself:
```bash
docker build -t erikgartner/hyperdock-worker:latest -f docker/Dockerfile.worker .
docker build -t erikgartner/hyperdock-supervisor:latest -f docker/Dockerfile.supervisor .
```

## License
Copyright 2018 Erik Gärtner

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

