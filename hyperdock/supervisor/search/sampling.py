import logging

import schema
from sklearn.model_selection import ParameterSampler

logger = logging.getLogger("sampling")


SCHEMA_SAMPLING = schema.Schema(
    {
        "hdock_distr": schema.Or(
            schema.And(str, lambda s: get_distribution(s) is not None)
        ),
        "hdock_samples": schema.And(int, lambda n: n >= 0),
        schema.Optional("hdock_seed", default=0): int,
        schema.Optional("hdock_distr_kwargs", default={}): dict,
    },
    ignore_extra_keys=True,
)


def sample_values(value):
    """
    A random sampling search.

    Using the special keys for distributions.
    {
        "parameter": {
            "hdock_distr": <str> (From scipy.stats.distributions),
            "hdock_distr_kwargs": {
                "some_distribution_parameter": ...
            }
            "hdock_samples": <int>,
            "hdock_seed": <int>,
        }
    }

    Takes the value dict above and returns a list of the samples values.
    """
    if not SCHEMA_SAMPLING.is_valid(value):
        return None

    # Clean input
    value = SCHEMA_SAMPLING.validate(value)

    # Get dist
    dist_cls = get_distribution(value["hdock_distr"])
    try:
        dist = dist_cls(**value["hdock_distr_kwargs"])
    except:
        logger.error(
            "Invalid distribution kwargs: {}".format(value["hdock_distr_kwargs"])
        )
        return None
    param_grid = {"key": dist}
    result = ParameterSampler(
        param_grid, n_iter=value["hdock_samples"], random_state=value["hdock_seed"]
    )

    # Convert into list format
    output_values = [r["key"] for r in result]
    return output_values


def get_distribution(dist_name):
    """Fetches a scipy distribution class by name"""
    from scipy import stats as dists

    if dist_name not in dists.__all__:
        return None
    cls = getattr(dists, dist_name)
    return cls
