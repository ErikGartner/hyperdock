class Search:
    """
    The super class for the parameter search methods
    Implemented:
        - Grid search

    Planned:
        - Random sampling
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
    def _expand_spec(specs, **kwargs):
        raise NotImplementedError
