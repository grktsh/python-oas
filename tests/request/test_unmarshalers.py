# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import functools

import pytest

from oas.exceptions import UnmarshalError
from oas.request.models import Request
from oas.request.unmarshalers import unmarshal_request
from oas.schema.unmarshalers import SchemaUnmarshaler


class MockRequest(Request):
    media_type = 'application/json'

    def __init__(self, query, media):
        self._query = query
        self._media = media

    @property
    def query(self):
        return self._query

    @property
    def media(self):
        return self._media

    path = None
    header = None
    cookie = None
    content_length = 1
    uri_template = None
    method = None
    context = None


@pytest.fixture
def unmarshal():
    return functools.partial(unmarshal_request, SchemaUnmarshaler())


def test_unmarshal_request(unmarshal):
    request = MockRequest(query={'p': '42'}, media='2020-01-02')
    operation = {
        'parameters': [
            {'name': 'p', 'in': 'query', 'schema': {'type': 'integer'}}
        ],
        'requestBody': {
            'content': {
                request.media_type: {
                    'schema': {'type': 'string', 'format': 'date'}
                }
            }
        },
    }
    parameters, request_body = unmarshal(request, operation)
    assert parameters == {'query': {'p': 42}}
    assert request_body == datetime.date(2020, 1, 2)


def test_unmarshal_request_without_request_body(unmarshal):
    request = MockRequest(query={'p': '42'}, media='2020-01-02')
    operation = {
        'parameters': [
            {'name': 'p', 'in': 'query', 'schema': {'type': 'integer'}}
        ]
    }
    parameters, request_body = unmarshal(request, operation)
    assert parameters == {'query': {'p': 42}}
    assert request_body is None


def test_unmarshal_request_error(unmarshal):
    request = MockRequest(query={'p': 'not-integer'}, media='2020/01/02')
    operation = {
        'parameters': [
            {'name': 'p', 'in': 'query', 'schema': {'type': 'integer'}}
        ],
        'requestBody': {
            'content': {
                request.media_type: {
                    'schema': {'type': 'string', 'format': 'date'}
                }
            }
        },
    }
    with pytest.raises(UnmarshalError) as exc_info:
        unmarshal(request, operation)

    parameter_errors = exc_info.value.parameter_errors
    assert len(parameter_errors) == 1
    assert parameter_errors[0].schema_path[0] == 'parameters'
    request_body_errors = exc_info.value.request_body_errors
    assert len(request_body_errors) == 1
    assert request_body_errors[0].schema_path[0] == 'requestBody'
