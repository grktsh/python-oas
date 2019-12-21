# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import functools

import jsonschema
import pytest

from oas.request_body.models import RequestBody
from oas.request_body.unmarshalers import unmarshal_request_body
from oas.schema.unmarshalers import SchemaUnmarshaler


class MockRequestBody(RequestBody):
    media_type = 'application/json'

    def __init__(self, media=None, content_length=1):
        self._media = media
        self._content_length = content_length

    @property
    def media(self):
        return self._media

    @property
    def content_length(self):
        return self._content_length


@pytest.fixture
def unmarshal():
    return functools.partial(unmarshal_request_body, SchemaUnmarshaler())


def test_missing_required(unmarshal):
    request_body = MockRequestBody(content_length=0)
    request_body_spec_dict = {'content': {}, 'required': True}

    _, errors = unmarshal(request_body, request_body_spec_dict)

    assert len(errors) == 1
    error = errors[0]
    assert isinstance(error, jsonschema.ValidationError)
    assert error.message == 'Request body is required'
    assert error.validator == 'required'
    assert error.validator_value is True
    assert error.schema == request_body_spec_dict
    assert list(error.schema_path) == ['required']
    assert list(error.path) == []


def test_missing_optional(unmarshal):
    request_body = MockRequestBody(content_length=0)
    request_body_spec_dict = {'content': {}}

    result = unmarshal(request_body, request_body_spec_dict)

    assert result == (None, None)


def test_unmarshal_content(unmarshal):
    request_body = MockRequestBody(media='2018-01-02')
    request_body_spec_dict = {
        'content': {
            request_body.media_type: {
                'schema': {'type': 'string', 'format': 'date'}
            }
        }
    }
    result = unmarshal(request_body, request_body_spec_dict)

    assert result == (datetime.date(2018, 1, 2), None)


def test_unmarshal_content_error(unmarshal):
    request_body = MockRequestBody(media=str('2018/01/02'))
    request_body_spec_dict = {
        'content': {
            request_body.media_type: {
                'schema': {'type': 'string', 'format': str('date')}
            }
        }
    }
    _, errors = unmarshal(request_body, request_body_spec_dict)

    assert len(errors) == 1
    error = errors[0]
    assert isinstance(error, jsonschema.ValidationError)
    assert error.message == "'2018/01/02' is not a 'date'"
    assert error.validator == 'format'
    assert error.validator_value == 'date'
    assert error.schema == {'type': 'string', 'format': str('date')}
    assert list(error.schema_path) == [
        'content',
        request_body.media_type,
        'schema',
        'format',
    ]
    assert list(error.path) == []
