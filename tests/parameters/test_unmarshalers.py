# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import functools

import jsonschema
import pytest

from oas.parameters.models import Parameters
from oas.parameters.unmarshalers import unmarshal_parameters
from oas.schema.unmarshalers import SchemaUnmarshaler

LOCATION = str('query')


class MockParameters(Parameters):
    def __init__(self, name=None, value=None):
        self._query = {}
        if name is not None:
            self._query[name] = value

    @property
    def query(self):
        return self._query

    path = None
    header = None
    cookie = None


@pytest.fixture
def unmarshal():
    return functools.partial(unmarshal_parameters, SchemaUnmarshaler())


def test_missing(unmarshal):
    parameters = MockParameters()
    parameter_spec_dicts = [
        {'name': str('p1'), 'in': LOCATION, 'required': True},
        {'name': 'p2', 'in': LOCATION},
    ]

    _, errors = unmarshal(parameters, parameter_spec_dicts)

    assert len(errors) == 1
    assert isinstance(errors[0], jsonschema.ValidationError)
    assert errors[0].message == "'p1' is a required in 'query' parameter"
    assert errors[0].validator == 'required'
    assert errors[0].validator_value is True
    assert errors[0].schema == parameter_spec_dicts[0]
    assert list(errors[0].schema_path) == [0, 'required']
    assert list(errors[0].path) == [LOCATION, 'p1']


def test_default(unmarshal):
    parameters = MockParameters()
    parameter_spec_dicts = [
        {'name': 'p1', 'in': LOCATION, 'schema': {'default': 42}},
        {'name': 'p2', 'in': LOCATION, 'schema': {'default': 'x'}},
    ]
    unmarshaled, errors = unmarshal(parameters, parameter_spec_dicts)

    assert unmarshaled == {LOCATION: {'p1': 42, 'p2': 'x'}}
    assert errors is None


def test_undocumented_schema(unmarshal):
    parameters = MockParameters(name='p', value='as is')
    parameter_spec_dicts = [{'name': 'p', 'in': LOCATION}]
    unmarshaled, errors = unmarshal(parameters, parameter_spec_dicts)

    assert unmarshaled == {LOCATION: {'p': 'as is'}}
    assert errors is None


def test_unmarshal_success(unmarshal):
    parameters = MockParameters(name='p', value='2018-01-02')
    parameter_spec_dicts = [
        {
            'name': 'p',
            'in': LOCATION,
            'schema': {'type': 'string', 'format': 'date'},
        }
    ]
    unmarshaled, errors = unmarshal(parameters, parameter_spec_dicts)

    assert unmarshaled == {LOCATION: {'p': datetime.date(2018, 1, 2)}}
    assert errors is None


def test_unmarshal_error(unmarshal):
    parameters = MockParameters(name='p', value=str('2018/01/02'))
    parameter_spec_dicts = [
        {
            'name': 'p',
            'in': LOCATION,
            'schema': {'type': 'string', 'format': str('date')},
        }
    ]
    _, errors = unmarshal(parameters, parameter_spec_dicts)

    assert len(errors) == 1
    assert isinstance(errors[0], jsonschema.ValidationError)
    assert errors[0].message == "'2018/01/02' is not a 'date'"
    assert errors[0].validator == 'format'
    assert errors[0].validator_value == 'date'
    assert errors[0].instance == '2018/01/02'
    assert errors[0].schema == {'type': 'string', 'format': str('date')}
    assert list(errors[0].schema_path) == [0, 'schema', 'format']
    assert list(errors[0].path) == [LOCATION, 'p']
