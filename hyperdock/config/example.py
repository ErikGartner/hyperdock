"""
This contains an example of an space config file.
"""

# Import hyperopt to build the space
from hyperopt import hp

# Declare a variable called SPACE containing the parameter space.
SPACE = {
    'max_epochs': 50,
    'dropout': hp.quniform('dropout', 0, 0.5, 0.25),
}


if __name__ == '__main__':
    # Loads the space and samples from it as a test.
    print(hyperopt.pyll.stochastic.sample(SPACE))
