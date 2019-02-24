from sklearn.model_selection import ParameterGrid

from .search import Search


class Grid(Search):
    """The super class for the parameter search methods"""

    @staticmethod
    def _expand_spec(spec, **kwargs):
        """
        Expands a single parameter specification.
        """
        fixed_params = {}
        variable_params = {}
        for k, v in spec.items():
            if isinstance(v, list):
                variable_params[k] = v
            else:
                fixed_params[k] = v

        params = list(ParameterGrid(variable_params))
        [p.update(fixed_params) for p in params]
        return params
