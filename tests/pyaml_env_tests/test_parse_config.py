import os
import unittest
from pyaml_env import parse_config


class TestParseConfig(unittest.TestCase):
    def setUp(self):
        self.test_file_name = f'{os.path.abspath(".")}/testfile.yaml'
        self.env_var1 = 'ENV_TAG1'
        self.env_var2 = 'ENV_TAG2'
        self.env_var3 = 'ENV_TAG3'
        os.unsetenv(self.env_var1)
        os.unsetenv(self.env_var2)
        os.unsetenv(self.env_var3)

    def tearDown(self):
        if self.env_var1 in os.environ:
            del os.environ[self.env_var1]
        if self.env_var2 in os.environ:
            del os.environ[self.env_var2]
        if self.env_var3 in os.environ:
            del os.environ[self.env_var3]

        if os.path.isfile(self.test_file_name):
            os.remove(self.test_file_name)

    def test_parse_config_with_data(self):
        os.environ[self.env_var1] = 'it works!'
        os.environ[self.env_var2] = 'this works too!'
        test_data = '''
        test1:
            data0: !ENV ${ENV_TAG1}
            data1:  !ENV ${ENV_TAG2}
        '''
        config = parse_config(data=test_data)

        expected_config = {
            'test1': {
                'data0': 'it works!',
                'data1': 'this works too!'
            }
        }

        self.assertDictEqual(
            config,
            expected_config
        )

    def test_parse_config_with_file_path(self):
        os.environ[self.env_var1] = 'it works!'
        os.environ[self.env_var2] = 'this works too!'
        test_data = '''
        test1:
            data0: !ENV ${ENV_TAG1}
            data1:  !ENV ${ENV_TAG2}
        '''
        with open(self.test_file_name, 'w') as test_file:
            test_file.write(test_data)

        config = parse_config(path=self.test_file_name)

        expected_config = {
            'test1': {
                'data0': 'it works!',
                'data1': 'this works too!'
            }
        }

        self.assertDictEqual(
            config,
            expected_config
        )

    def test_parse_config_diff_tag(self):
        os.environ[self.env_var1] = 'it works!'
        os.environ[self.env_var2] = 'this works too!'
        test_data = '''
        test1:
            data0: !TEST ${ENV_TAG1}
            data1:  !TEST ${ENV_TAG2}
        '''
        config = parse_config(data=test_data, tag='!TEST')

        expected_config = {
            'test1': {
                'data0': 'it works!',
                'data1': 'this works too!'
            }
        }

        self.assertDictEqual(
            config,
            expected_config
        )

    def test_parse_config_more_than_one_env_value(self):
        os.environ[self.env_var1] = 'it works!'
        os.environ[self.env_var2] = 'this works too!'
        test_data = '''
        test1:
            data0: !TEST ${ENV_TAG1}/somethingelse/${ENV_TAG2}
            data1:  !TEST ${ENV_TAG2}
        '''
        config = parse_config(data=test_data, tag='!TEST')

        expected_config = {
            'test1': {
                'data0': 'it works!/somethingelse/this works too!',
                'data1': 'this works too!'
            }
        }

        self.assertDictEqual(
            config,
            expected_config
        )

    def test_parse_config_default_separator(self):
        # os.environ[self.env_var1] = 'it works!'
        # os.environ[self.env_var2] = 'this works too!'
        test_data = '''
        test1:
            data0: !TEST ${ENV_TAG1:default1}/somethingelse/${ENV_TAG2}
            data1:  !TEST ${ENV_TAG2:default2}
        '''
        config = parse_config(data=test_data, tag='!TEST', default_sep=':')

        expected_config = {
            'test1': {
                'data0': 'default1/somethingelse/N/A',
                'data1': 'default2'
            }
        }

        self.assertDictEqual(
            config,
            expected_config
        )

    def test_parse_config_default_separator_two_env_vars_in_one_line(self):
        test_data = '''
        test1:
            data0: !TEST ${ENV_TAG1:default1}/somethingelse/${ENV_TAG2:default2}
            data1:  !TEST ${ENV_TAG2}
        '''
        config = parse_config(data=test_data, tag='!TEST', default_sep=':')

        expected_config = {
            'test1': {
                'data0': 'default1/somethingelse/default2',
                'data1': 'N/A'
            }
        }

        self.assertDictEqual(
            config,
            expected_config
        )

    def test_parse_config_default_separator_diff_default_value(self):
        test_data = '''
        test1:
            data0: !TEST ${ENV_TAG1:default1}/somethingelse/${ENV_TAG2:default2}
            data1:  !TEST ${ENV_TAG2}
        '''
        config = parse_config(
            data=test_data,
            tag='!TEST',
            default_sep=':',
            default_value='DEFAULT_VALUE'
        )

        expected_config = {
            'test1': {
                'data0': 'default1/somethingelse/default2',
                'data1': 'DEFAULT_VALUE'
            }
        }

        self.assertDictEqual(
            config,
            expected_config
        )

    def test_parse_config_raise_if_na(self):
        test_data = '''
        test1:
            data0: !TEST ${ENV_TAG1:default1}/somethingelse/${ENV_TAG2:default2}
            data1:  !TEST ${ENV_TAG2}
        '''

        with self.assertRaises(ValueError):
            _ = parse_config(
                data=test_data,
                tag='!TEST',
                default_sep=':',
                raise_if_na=True
            )

    def test_parse_config_raise_if_na_not_raised(self):
        test_data = '''
        test1:
            data0: !TEST ${ENV_TAG1:default1}/somethingelse/${ENV_TAG2:default2}
            data1:  !TEST ${ENV_TAG2:default3}
        '''
        expected_config = {
            'test1': {
                'data0': 'default1/somethingelse/default2',
                'data1': 'default3'
            }
        }

        # no na so this should not raise anything
        config = parse_config(
            data=test_data,
            tag='!TEST',
            default_sep=':',
            raise_if_na=True
        )
        self.assertDictEqual(
            config,
            expected_config
        )

    def test_parse_config_default_separator_strong_password(self):
        test_data = '''
        test1:
            data0: !TEST ${ENV_TAG1:NoHtnnmEuluGp2boPvGQkGrXqTAtBvIVz9VRmV65}/somethingelse/${ENV_TAG2}
            data1:  !TEST ${ENV_TAG2:0.0.0.0}
        '''
        config = parse_config(data=test_data, tag='!TEST', default_sep=':')

        expected_config = {
            'test1': {
                'data0': 'NoHtnnmEuluGp2boPvGQkGrXqTAtBvIVz9VRmV65/somethingelse/N/A',
                'data1': '0.0.0.0'
            }
        }

        self.assertDictEqual(
            config,
            expected_config
        )

    def test_parse_config_default_separator_var_chars(self):
        test_data = '''
        test1:
            data0: !TEST ${ENV_TAG1:35xV*+/\gPEFGxrg}/somethingelse/${ENV_TAG2}
            data1:  !TEST ${ENV_TAG2:0.0.0.0}
        '''
        config = parse_config(data=test_data, tag='!TEST', default_sep=':')

        expected_config = {
            'test1': {
                'data0': '35xV*+/\gPEFGxrg/somethingelse/N/A',
                'data1': '0.0.0.0'
            }
        }

        self.assertDictEqual(
            config,
            expected_config
        )

    def test_parse_config_default_separator_var_chars_env_var(self):
        os.environ[self.env_var1] = 'test'
        test_data = '''
        test1:
            data0: !TEST ${ENV_TAG1:35xV*+/\gPEFGxrg}/somethingelse/${ENV_TAG2}
            data1:  !TEST ${ENV_TAG2:0.0.0.0}
        '''
        config = parse_config(data=test_data, tag='!TEST', default_sep=':')

        expected_config = {
            'test1': {
                'data0': 'test/somethingelse/N/A',
                'data1': '0.0.0.0'
            }
        }

        self.assertDictEqual(
            config,
            expected_config
        )

    def test_parse_config_default_separator_strong_password_overwritten_by_env_var(self):
        os.environ[self.env_var1] = "myWeakPassword"

        test_data = '''
        test1:
            data0: !TEST ${ENV_TAG1:NoHtnnmEuluGp2boPvGQkGrXqTAtBvIVz9VRmV65}/somethingelse/${ENV_TAG2}
            data1:  !TEST ${ENV_TAG2:0.0.0.0}
        '''
        config = parse_config(data=test_data, tag='!TEST', default_sep=':')

        expected_config = {
            'test1': {
                'data0': 'myWeakPassword/somethingelse/N/A',
                'data1': '0.0.0.0'
            }
        }

        self.assertDictEqual(
            config,
            expected_config
        )

    def test_parse_config_default_separator_two_env_var(self):
        os.environ[self.env_var1] = "1value"
        os.environ[self.env_var2] = "2values"

        test_data = '''
        test1:
            data0: !TEST ${ENV_TAG1:NoHtnnmEuluGp2boPvGQkGrXqTAtBvIVz9VRmV65}/somethingelse/${ENV_TAG2}
            data1:  !TEST ${ENV_TAG2:0.0.0.0}
        '''
        config = parse_config(data=test_data, tag='!TEST', default_sep=':')

        expected_config = {
            'test1': {
                'data0': '1value/somethingelse/2values',
                'data1': '2values'
            }
        }

        self.assertDictEqual(
            config,
            expected_config
        )