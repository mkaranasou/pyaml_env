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
        self.__dict__ = self.__handle_inner_structures()

    def __handle_inner_structures(self):
        for k, v in self.__dict__.items():
            if isinstance(v, dict):
                self.__dict__[k] = BaseConfig(v)
        return self.__dict__

    @property
    def errors(self):
        return self._errors

    def validate(self):
        raise NotImplementedError()