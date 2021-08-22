import os
import re

import yaml


def parse_config(
        path=None,
        data=None,
        tag='!ENV',
        default_sep=':',
        default_value='N/A',
        raise_if_na=False
):
    """
        Load yaml configuration from path or from the contents of a file (data)
        and resolve any environment variables. The environment variables
        must have the tag e.g. !ENV *before* them and be in this format to be
        parsed: ${VAR_NAME}
        E.g.:
        databse:
          name: test_db
          username: !ENV ${DB_USER:paws}
          password: !ENV ${DB_PASS:meaw2}
          url: !ENV 'http://${DB_BASE_URL:straight_to_production}:${DB_PORT:12345}'

        :param str path: the path to the yaml file
        :param str data: the yaml data itself as a stream
        :param str tag: the tag to look for
        :param str default_sep: if any default values are set, use this field
        to separate them from the enironment variable name. E.g. ':' can be
        used.
        :param str default_value: the tag to look for
        :return: the dict configuration
        :rtype: dict[str, T]
        """
    default_sep = default_sep or ''
    default_sep_pattern = r'(' + default_sep + '[^}^{]+)?' if default_sep else ''
    pattern = re.compile(
        r'.*?\$\{([^}{' + default_sep + r']+)' + default_sep_pattern + r'\}.*?')
    loader = yaml.SafeLoader

    # the tag will be used to mark where to start searching for the pattern
    # e.g. a_key: !ENV somestring${ENV_VAR}other_stuff_follows
    loader.add_implicit_resolver(tag, pattern, None)

    def constructor_env_variables(loader, node):
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
        match = pattern.findall(value)  # to find all env variables in line
        if match:
            full_value = value
            for g in match:
                curr_default_value = default_value
                env_var_name = g
                env_var_name_with_default = g
                if default_sep and  isinstance(g, tuple) and len(g) > 1:
                    env_var_name = g[0]
                    env_var_name_with_default = ''.join(g)
                    found = False
                    for each in g:
                        if default_sep in each:
                            _, curr_default_value = each.split(default_sep, 1)
                            found = True
                            break
                    if not found and raise_if_na:
                        raise ValueError(
                            f'Could not find default value for {env_var_name}'
                        )
                full_value = full_value.replace(
                    f'${{{env_var_name_with_default}}}',
                    os.environ.get(env_var_name, curr_default_value)
                )
            return full_value
        return value

    loader.add_constructor(tag, constructor_env_variables)

    if path:
        with open(path) as conf_data:
            return yaml.load(conf_data, Loader=loader)
    elif data:
        return yaml.load(data, Loader=loader)
    else:
        raise ValueError('Either a path or data should be defined as input')
