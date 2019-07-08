from sklearn.model_selection import ParameterGrid

from .sampling import sample_values


class Search:
    """
    The class for the parameter search methods

    Implemented:
        - Grid search
        - Sampling from distributions
    """

    @classmethod
    def expand(cls, specs, **kwargs):
        """
        Takes a (list of) parameter specification and returns a list
        of combination to try.
        """
        specs = Search.list_wrap(specs)

        params = []
        for spec in specs:
            params.extend(cls._expand_spec(spec, **kwargs))
        return params

    @staticmethod
    def list_wrap(spec):
        """
        If not a list, wraps the spec in a list.
        """
        if not isinstance(spec, list):
            spec = [spec]
        return spec

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
            elif isinstance(v, dict):
                # Try handling as distribution
                res = sample_values(v)
                if res is not None:
                    variable_params[k] = res
                else:
                    fixed_params[k] = v
            else:
                fixed_params[k] = v

        params = list(ParameterGrid(variable_params))
        [p.update(fixed_params) for p in params]
        return params
