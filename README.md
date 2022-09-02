[![Downloads](https://static.pepy.tech/personalized-badge/pyaml-env?period=total&units=none&left_color=black&right_color=green&left_text=Downloads)](https://pepy.tech/project/pyaml-env)
[![Tests and linting](https://github.com/mkaranasou/pyaml_env/actions/workflows/python-app.yml/badge.svg)](https://github.com/mkaranasou/pyaml_env/actions/workflows/python-app.yml)
[![CodeQL](https://github.com/mkaranasou/pyaml_env/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/mkaranasou/pyaml_env/actions/workflows/codeql-analysis.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Upload Python Package](https://github.com/mkaranasou/pyaml_env/actions/workflows/python-publish.yml/badge.svg)](https://github.com/mkaranasou/pyaml_env/actions/workflows/python-publish.yml)

# Python YAML configuration with environment variables parsing

## TL;DR
A very small library that parses a yaml configuration file and it resolves the environment variables,
so that no secrets are kept in text.

### Install
```bash
pip install pyaml-env
```
### How to use:

---

#### Basic Usage: Environment variable parsing
This yaml file:
```yaml
databse:
  name: test_db
  username: !ENV ${DB_USER}
  password: !ENV ${DB_PASS}
  url: !ENV 'http://${DB_BASE_URL}:${DB_PORT}'
```
given that we've set these:
```bash
export $DB_USER=super_secret_user
export $DB_PASS=extra_super_secret_password
export $DB_BASE_URL=localhost
export $DB_PORT=5432
```

becomes this:
```python
from pyaml_env import parse_config
config = parse_config('path/to/config.yaml')

print(config)
# outputs the following, with the environment variables resolved
{
    'database': {
        'name': 'test_db',
        'username': 'super_secret_user',
        'password': 'extra_super_secret_password',
        'url': 'http://localhost:5432',
    }
}

```


---

#### Attribute Access using `BaseConfig`
Which can also become this:
```python
from pyaml_env import parse_config, BaseConfig
config = BaseConfig(parse_config('path/to/config.yaml'))
# you can then access the config properties as atrributes
# I'll explain why this might be useful in a bit.
print(config.database.url)
```
---


#### Default Values with `:`
You can also set default values for when the environment variables are not set for some reason,
using the `default_sep` kwarg (**which is `:` by default**) like this:
```yaml
databse:
  name: test_db
  username: !ENV ${DB_USER:paws}
  password: !ENV ${DB_PASS:meaw2}
  url: !ENV 'http://${DB_BASE_URL:straight_to_production}:${DB_PORT}'
```

And if no environment variables are found then we get:
```python
from pyaml_env import parse_config
config = parse_config('path/to/config.yaml')

print(config)
{
    'database': {
        'name': 'test_db',
        'username': 'paws',
        'password': 'meaw2',
        'url': 'http://straight_to_production:N/A',
    }
}
```
**NOTE 0**: Special characters like `*`, `{` etc. are not currently supported as separators. Let me know if you'd like them handled also.

**NOTE 1**: If you set `tag` to `None`, then, the current behavior is that environment variables in all places in the yaml will be resolved (if set).

---

#### If nothing matches: `N/A` as `default_value`:

If no defaults are found and no environment variables, the `default_value` (**which is `N/A` by default**)  is used:
```python
{
    'database': {
        'name': 'test_db',
        'username': 'N/A',
        'password': 'N/A',
        'url': 'http://N/A:N/A',
    }
}
```
Which, of course, means something went wrong and we need to set the correct environment variables.
If you want this process to fail if a *default value* is not found, you can set the `raise_if_na` flag to `True`.
For example:

```yaml
test1:
    data0: !TEST ${ENV_TAG1:has_default}/somethingelse/${ENV_TAG2:also_has_default}
    data1:  !TEST ${ENV_TAG2}
```
will raise a `ValueError` because `data1:  !TEST ${ENV_TAG2}` there is no default value for `ENV_TAG2` in this line.

---


#### Using a different loader:

The default yaml loader is `yaml.SafeLoader`. If you need to work with serialized Python objects,
you can specify a different loader.

So given a class:
```python
class OtherLoadTest:
    def __init__(self):
        self.data0 = 'it works!'
        self.data1 = 'this works too!'

```

Which has become a yaml output like the following using `yaml.dump(OtherLoadTest())`:
```yaml
!!python/object:__main__.OtherLoadTest
data0: it works!
data1: this works too!
```

You can use `parse_config` to load the object like this:
```python
import yaml
from pyaml_env import parse_config

other_load_test = parse_config(path='path/to/config.yaml', loader=yaml.UnsafeLoader)
print(other_load_test)
<__main__.OtherLoadTest object at 0x7fc38ccd5470>
```

---

#### Using PyamlEnvConstructor:

Simple way to add !ENV constructor to a pyyaml loader.

```python
from yaml import Loader
from pyaml_env import  PyamlEnvConstructor

PyamlEnvConstructor.add_to_loader_class(loader_class=Loader)
# or
PyamlEnvConstructor.add_to_loader_class(
  loader_class=Loader,
  tag=custom_tag,
  add_implicit_resolver=True,
  sep=custom_sep,
  default_value=custom_default_value,
  raise_if_na=True
)
```

---

## Long story: Load a YAML configuration file and resolve any environment variables

![](https://cdn-images-1.medium.com/max/11700/1*4s_GrxE5sn2p2PNd8fS-6A.jpeg)

If you’ve worked with Python projects, you’ve probably have stumbled across the many ways to provide configuration. I am not going to go through all the ways here, but a few of them are:

* using .ini files

* using a python class

* using .env files

* using JSON or XML files

* using a yaml file

And so on. I’ve put some useful links about the different ways below, in case you are interested in digging deeper.

My preference is working with yaml configuration because I usually find very handy and easy to use and I really like that yaml files are also used in e.g. docker-compose configuration so it is something most are familiar with.

For yaml parsing I use the [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation) Python library.

In this article we’ll talk about the yaml file case and more specifically what you can do to **avoid keeping your secrets, e.g. passwords, hosts, usernames etc, directly on it**.

Let’s say we have a very simple example of a yaml file configuration:

    database:
     name: database_name
     user: me
     password: very_secret_and_complex
     host: localhost
     port: 5432

    ws:
     user: username
     password: very_secret_and_complex_too
     host: localhost

When you come to a point where you need to deploy your project, it is not really safe to have passwords and sensitive data in a plain text configuration file lying around on your production server. That’s where [**environment variables](https://medium.com/dataseries/hiding-secret-info-in-python-using-environment-variables-a2bab182eea) **come in handy. So the goal here is to be able to easily replace the very_secret_and_complex password with input from an environment variable, e.g. DB_PASS, so that this variable only exists when you set it and run your program instead of it being hardcoded somewhere.

For PyYAML to be able to resolve environment variables, we need three main things:

* A regex pattern for the environment variable identification e.g. pattern = re.compile(‘.*?\${(\w+)}.*?’)

* A tag that will signify that there’s an environment variable (or more) to be parsed, e.g. !ENV.

* And a function that the loader will use to resolve the environment variables

```python
def constructor_env_variables(loader, node):
    """
    Extracts the environment variable from the node's value
    :param yaml.Loader loader: the yaml loader
    :param node: the current node in the yaml
    :return: the parsed string that contains the value of the environment
    variable
    """
    value = loader.construct_scalar(node)
    match = pattern.findall(value)
    if match:
        full_value = value
        for g in match:
            full_value = full_value.replace(
                f'${{{g}}}', os.environ.get(g, g)
            )
        return full_value
    return value
```

Example of a YAML configuration with environment variables:

    database:
     name: database_name
     user: !ENV ${DB_USER}
     password: !ENV ${DB_PASS}
     host: !ENV ${DB_HOST}
     port: 5432

    ws:
     user: !ENV ${WS_USER}
     password: !ENV ${WS_PASS}
     host: !ENV ‘[https://${CURR_ENV}.ws.com.local'](https://${CURR_ENV}.ws.com.local')

This can also work **with more than one environment variables** declared in the same line for the same configuration parameter like this:

    ws:
     user: !ENV ${WS_USER}
     password: !ENV ${WS_PASS}
     host: !ENV '[https://${CURR_ENV}.ws.com.](https://${CURR_ENV}.ws.com.local')[${MODE}](https://${CURR_ENV}.ws.com.local')'  # multiple env var

And how to use this:

First set the environment variables. For example, for the DB_PASS :

    export DB_PASS=very_secret_and_complex

Or even better, so that the password is not echoed in the terminal:

    read -s ‘Database password: ‘ db_pass
    export DB_PASS=$db_pass

```python

# To run this:
# export DB_PASS=very_secret_and_complex
# python use_env_variables_in_config_example.py -c /path/to/yaml
# do stuff with conf, e.g. access the database password like this: conf['database']['DB_PASS']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='My awesome script')
    parser.add_argument(
        "-c", "--conf", action="store", dest="conf_file",
        help="Path to config file"
    )
    args = parser.parse_args()
    conf = parse_config(path=args.conf_file)
```


Then you can run the above script:
```bash
python use_env_variables_in_config_example.py -c /path/to/yaml
```

And in your code, do stuff with conf, e.g. access the database password like this: `conf['database']['DB_PASS']`

I hope this was helpful. Any thoughts, questions, corrections and suggestions are very welcome :)

## Useful links
[**The Many Faces and Files of Python Configs**
*As we cling harder and harder to Dockerfiles, Kubernetes, or any modern preconfigured app environment, our dependency…*hackersandslackers.com](https://hackersandslackers.com/simplify-your-python-projects-configuration/)
[**4 Ways to manage the configuration in Python**
*I’m not a native speaker. Sorry for my english. Please understand.*hackernoon.com](https://hackernoon.com/4-ways-to-manage-the-configuration-in-python-4623049e841b)
[**Python configuration files**
*A common need when writing an application is loading and saving configuration values in a human-readable text format…*www.devdungeon.com](https://www.devdungeon.com/content/python-configuration-files)
[**Configuration files in Python**
*Most interesting programs need some kind of configuration: Content Management Systems like WordPress blogs, WikiMedia…*martin-thoma.com](https://martin-thoma.com/configuration-files-in-python/)



<a href="https://www.buymeacoffee.com/mkaranasou" target="_blank" style="background: #40DCA5;"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
