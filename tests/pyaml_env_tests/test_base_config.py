import os
import unittest
from src.pyaml_env import BaseConfig


class TestBaseConfig(unittest.TestCase):
    def setUp(self):
        self.simple_data = {
            'a': 1,
            'b': 2,
        }
        self.complex_data = {
            'a': {
                'b': {
                    'c': [1, 2],
                    'd': {
                        'e': 12,
                        'f': 'test'
                    }
                }
            },
            'g': {
                'h': {
                    'i': 'ai',
                    'j': 'jay'
                },
                'k': [1, 3, 5]
            }
        }

    def test_base_config_simple_structure(self):
        base_config = BaseConfig(self.simple_data)
        self.assertTrue(
            hasattr(base_config, 'a')
        )
        self.assertTrue(
            hasattr(base_config, 'b')
        )
        print(base_config.a)
        print(base_config.b)
        self.assertEquals(self.simple_data['a'], base_config.a)
        self.assertEquals(self.simple_data['b'], base_config.b)

    def test_base_config_complex_structure(self):
        base_config = BaseConfig(self.complex_data)
        self.assertTrue(
            hasattr(base_config, 'a')
        )
        self.assertTrue(
            hasattr(base_config, 'g')
        )
        print(base_config.a)
        print(base_config.g)
        print(base_config.g.h)
        print(base_config.g.h.i)
        print(base_config.g.h.j)
        print(base_config.g.k)
        print(base_config.a.b)
        print(base_config.a.b.c)
        print(base_config.a.b.d)
        print(base_config.a.b.d.e)
        print(base_config.a.b.d.f)
        self.assertIsInstance(base_config.a, BaseConfig)
        self.assertIsInstance(base_config.g, BaseConfig)
        self.assertIsInstance(base_config.g.h, BaseConfig)
        self.assertIsInstance(base_config.g.h.i, str)
        self.assertIsInstance(base_config.g.h.j, str)
        self.assertIsInstance(base_config.g.k, list)
        self.assertIsInstance(base_config.a.b, BaseConfig)
        self.assertIsInstance(base_config.a.b.c, list)
        self.assertIsInstance(base_config.a.b.d, BaseConfig)
        self.assertIsInstance(base_config.a.b.d.e, int)
        self.assertIsInstance(base_config.a.b.d.f, str)