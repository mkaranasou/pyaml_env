import yaml
from .constructor import PyamlEnvConstructor


def parse_config(
        path=None,
        data=None,
        tag=PyamlEnvConstructor.DEFAULT_TAG_NAME,
        add_implicit_resolver=PyamlEnvConstructor.DEFAULT_ADD_IMPLICIT_RESOLVER,
        default_sep=PyamlEnvConstructor.DEFAULT_SEP,
        default_value=PyamlEnvConstructor.DEFAULT_VALUE,
        raise_if_na=PyamlEnvConstructor.DEFAULT_RAISE_IF_NA,
        loader=yaml.SafeLoader,
        encoding='utf-8'
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
        :param str tag: the tag to look for, if None, all env variables will be
        resolved.
        :param str add_implicit_resolver: add implicit resolver. All env variables
        will be resolved.
        :param str default_sep: if any default values are set, use this field
        to separate them from the enironment variable name. E.g. ':' can be
        used.
        :param str default_value: the tag to look for
        :param bool raise_if_na: raise an exception if there is no default
        value set for the env variable.
        :param Type[yaml.loader] loader: Specify which loader to use. Defaults to
        yaml.SafeLoader
        :param str encoding: the encoding of the data if a path is specified,
        defaults to utf-8
        :return: the dict configuration
        :rtype: dict[str, T]
        """
    default_sep = default_sep or ''
    default_value = default_value or ''
    loader = loader or yaml.SafeLoader
    add_implicit_resolver = True if tag is None else add_implicit_resolver

    PyamlEnvConstructor.add_to_loader_class(
        loader_class=loader,
        tag=tag,
        add_implicit_resolver=add_implicit_resolver,
        sep=default_sep,
        default_value=default_value,
        raise_if_na=raise_if_na
    )

    if path:
        with open(path, encoding=encoding) as conf_data:
            return yaml.load(conf_data, Loader=loader)
    elif data:
        return yaml.load(data, Loader=loader)
    else:
        raise ValueError('Either a path or data should be defined as input')
