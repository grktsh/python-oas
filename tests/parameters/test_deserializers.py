from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from oas.parameters.deserializers import deserialize_parameter
from oas.parameters.models import Parameters

LOCATION = 'query'
NAME = 'p'


def deserialize(parameters, parameter_spec_dict):
    return deserialize_parameter(
        parameters, LOCATION, NAME, parameter_spec_dict
    )


class MockParameters(Parameters):
    def __init__(self, name=NAME, value=None):
        self._query = {}
        if name is not None:
            self._query[name] = value

    @property
    def query(self):
        return self._query

    path = None
    header = None
    cookie = None


def test_deserialize_parameter_default():
    parameters = MockParameters(name=None)
    parameter_spec_dict = {'schema': {'default': 42}}

    result = deserialize(parameters, parameter_spec_dict)
    assert result == (42, parameter_spec_dict['schema'])


@pytest.mark.parametrize('parameter_spec_dict', [{}, {'schema': {}}])
def test_deserialize_parameter_no_default(parameter_spec_dict):
    parameters = MockParameters(name=None)

    with pytest.raises(KeyError):
        deserialize(
            parameters, parameter_spec_dict,
        )


@pytest.mark.parametrize(
    'value,parameter_spec_dict', [('2', {}), ('2', {'schema': {}})]
)
def test_deserialize_parameter_no_schema_or_type(value, parameter_spec_dict):
    parameters = MockParameters(value=value)

    result = deserialize(parameters, parameter_spec_dict)
    assert result == (value, {})


@pytest.mark.parametrize(
    'value,schema_type,expected_value',
    [
        ('2', 'integer', 2),
        ('2.3', 'number', 2.3),
        ('2', 'number', 2.0),
        ('1', 'boolean', True),
        ('0', 'boolean', False),
        ('true', 'boolean', True),
        ('false', 'boolean', False),
        ('t', 'boolean', True),
        ('f', 'boolean', False),
        ('yes', 'boolean', True),
        ('no', 'boolean', False),
        ('x', 'string', 'x'),
    ],
)
def test_deserialize_parameter_parse_success(
    value, schema_type, expected_value
):
    parameters = MockParameters(value=value)
    parameter_spec_dict = {'schema': {'type': schema_type}}

    value, schema = deserialize(parameters, parameter_spec_dict)
    assert value == expected_value
    assert isinstance(value, type(expected_value))
    assert schema == parameter_spec_dict['schema']


@pytest.mark.parametrize(
    'value,schema_type',
    [
        ('x', 'integer'),
        ('2.3', 'integer'),
        ('x', 'number'),
        ('2', 'boolean'),
        ('x', 'boolean'),
        ('{}', 'object'),  # Unsupported yet
        ('[]', 'array'),  # Unsupported yet
    ],
)
def test_deserialize_parameter_parse_error(value, schema_type):
    parameters = MockParameters(value=value)
    parameter_spec_dict = {'schema': {'type': schema_type}}

    result = deserialize(parameters, parameter_spec_dict)
    assert result == (value, parameter_spec_dict['schema'])
