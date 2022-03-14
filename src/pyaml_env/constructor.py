import os
import re
import yaml


class PyamlEnvConstructor:
    """The `env constructor` for PyYAML Loaders

    Call :meth:`add_to_loader_class` or :meth:`yaml.Loader.add_constructor` to
    add it into loader.

    In YAML files, use ``!ENV`` to load other YAML files as below::

        !ENV ${DB_USER:paws}

    or::

        !ENV 'http://${DB_BASE_URL:straight_to_production}:${DB_PORT:12345}'

    """

    DEFAULT_TAG_NAME = '!ENV'

    @classmethod
    def add_to_loader_class(cls,
                            loader_class=None,
                            tag=DEFAULT_TAG_NAME,
                            default_sep=':',
                            **kwargs):
        instance = cls(default_sep, **kwargs)
        yaml.add_implicit_resolver(tag, instance.pattern, None, loader_class)
        yaml.add_constructor(tag, instance, loader_class)
        return instance

    @property
    def pattern(self):
        default_sep_pattern = r'(' + self.default_sep + '[^}]+)?' if self.default_sep else ''
        return re.compile(r'.*?\$\{([^}{' + self.default_sep + r']+)' + default_sep_pattern + r'\}.*?')

    def __init__(self, default_sep=':', default_value='N/A', raise_if_na=False):
        self.default_sep = default_sep
        self.default_value = default_value
        self.raise_if_na = raise_if_na

    def __call__(self, loader, node):
        """
        Extracts the environment variable from the yaml node's value
        :param yaml.Loader loader: the yaml loader (as defined above)
        :param node: the current node (key-value) in the yaml
        :return: the parsed string that contains the value of the environment
        variable or the default value if defined for the variable. If no value
        for the variable can be found, then the value is replaced by
        default_value='N/A'
        """
        value = loader.construct_scalar(node)
        match = self.pattern.findall(value)  # to find all env variables in line
        if match:
            full_value = value
            for g in match:
                curr_default_value = self.default_value
                env_var_name = g
                env_var_name_with_default = g
                if self.default_sep and isinstance(g, tuple) and len(g) > 1:
                    env_var_name = g[0]
                    env_var_name_with_default = ''.join(g)
                    found = False
                    for each in g:
                        if self.default_sep in each:
                            _, curr_default_value = each.split(self.default_sep, 1)
                            found = True
                            break
                    if not found and self.raise_if_na:
                        raise ValueError(
                            f'Could not find default value for {env_var_name}'
                        )
                full_value = full_value.replace(
                    f'${{{env_var_name_with_default}}}',
                    os.environ.get(env_var_name, curr_default_value)
                )
            return full_value
        return value
