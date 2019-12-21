# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools

import pytest

from oas.exceptions import UndocumentedResponse
from oas.exceptions import ValidationError
from oas.response.models import Response
from oas.response.validators import validate_response
from oas.schema.unmarshalers import SchemaUnmarshaler


class MockResponse(Response):

    status_code = 200
    media_type = 'application/json'

    def __init__(self, headers=None, media=None):
        self._headers = headers or {}
        self._media = media

    @property
    def media(self):
        return self._media

    @property
    def header(self):
        return self._headers


@pytest.fixture
def validate():
    return functools.partial(validate_response, SchemaUnmarshaler())


def test_validate_response(validate):
    response = MockResponse(headers={'X-Id': '42'}, media='2020-01-02')
    operation = {
        'responses': {
            str(response.status_code): {
                'headers': {'X-Id': {'schema': {'type': 'integer'}}},
                'content': {
                    response.media_type: {
                        'schema': {'type': 'string', 'format': 'date'}
                    },
                },
            },
            'default': {'content': {}},
        }
    }

    try:
        validate(response, operation)
    except Exception as e:
        pytest.fail('Unexpected error: {}'.format(e))


def test_validate_response_default(validate):
    response = MockResponse(media='2020-01-02')
    operation = {
        'responses': {
            'default': {
                response.media_type: {
                    'schema': {'type': 'string', 'format': 'date'}
                }
            }
        }
    }

    try:
        validate(response, operation)
    except Exception as e:
        pytest.fail('Unexpected error: {}'.format(e))


def test_validate_response_undocumented_response(validate):
    response = MockResponse()
    operation = {'responses': {}}

    with pytest.raises(UndocumentedResponse):
        validate(response, operation)


def test_validate_response_optional(validate):
    response = MockResponse()
    operation = {'responses': {'default': {}}}

    try:
        validate(response, operation)
    except Exception as e:
        pytest.fail('Unexpected error: {}'.format(e))


def test_validate_response_errors(validate):
    response = MockResponse(
        headers={'X-Id': 'not-integer'}, media='2020/01/02',
    )
    operation = {
        'responses': {
            'default': {
                'headers': {'X-Id': {'schema': {'type': 'integer'}}},
                'content': {
                    response.media_type: {
                        'schema': {'type': 'string', 'format': 'date'}
                    },
                },
            }
        }
    }

    with pytest.raises(ValidationError) as exc_info:
        validate(response, operation)

    errors = exc_info.value.errors
    assert len(errors) == 2
    assert list(errors[0].schema_path) == [
        'responses',
        'default',
        'headers',
        0,
        'schema',
        'type',
    ]
    assert list(errors[0].path) == ['header', 'X-Id']
    assert list(errors[1].schema_path) == [
        'responses',
        'default',
        'content',
        response.media_type,
        'schema',
        'format',
    ]
    assert list(errors[1].path) == []
