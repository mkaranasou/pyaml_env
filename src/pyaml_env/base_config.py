class BaseConfig:
    """
    A base Config class to get
    """

    def __init__(self, config_dict):
        if config_dict:
            self.__dict__.update(**{
                k: v for k, v in self.__class__.__dict__.items()
                if '__' not in k and not callable(v)
            })
            self.__dict__.update(**config_dict)
        self._is_validated = False
        self._is_valid = False
        self._errors = []

    @property
    def errors(self):
        return self._errors

    def validate(self):
        raise NotImplementedError()