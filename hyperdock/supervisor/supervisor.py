import pprint

import hyperopt
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, Domain
from hyperopt.pyll.base import scope
from hyperopt.mongoexp import MongoTrials

from ..worker import objective


def create_dockerized_experiment(name, mongo_url, docker_image, docker_cmd,
                                 space, max_trials):
    """
    Creates a dockerized experiment that is supervised by this processed
    but expectes works to connect to and do the actual work.
    """

    # Create trials in Mongodb
    trials = MongoTrials(mongo_url, exp_key=name)

    # Add static docker params to hyper params
    space = {
        'docker_params': {
            'image': docker_image,
            'cmd': docker_cmd,
        },
        'hyperparams': space,
    }

    print('Starting evaluation...')
    best = fmin(objective.docker_objective,
                space=space,
                algo=tpe.suggest,
                max_evals=max_trials,
                trials=trials)

    print('Best parameters was:')
    pprint.pprint(best)
