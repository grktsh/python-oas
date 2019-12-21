# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import functools
from collections import deque

import jsonschema
import pytest

from oas.request_body import unmarshal_request_body
from oas.schema.unmarshalers import SchemaUnmarshaler

MEDIA_TYPE = 'application/json'


@pytest.fixture
def unmarshal():
    return functools.partial(unmarshal_request_body, SchemaUnmarshaler())


def test_missing_required(mocker, unmarshal):
    request_body = mocker.Mock(content_length=0)
    request_body_spec_dict = {'content': {}, 'required': True}

    _, errors = unmarshal(request_body, request_body_spec_dict)

    assert len(errors) == 1
    error = errors[0]
    assert isinstance(error, jsonschema.ValidationError)
    assert error.message == 'Request body is required'
    assert error.validator == 'required'
    assert error.validator_value is True
    assert error.schema == request_body_spec_dict
    assert error.schema_path == deque(['required'])
    assert error.path == deque([])


def test_missing_optional(mocker, unmarshal):
    request_body = mocker.Mock(content_length=0)
    request_body_spec_dict = {'content': {}}

    result = unmarshal(request_body, request_body_spec_dict)

    assert result == (None, None)


def test_unmarshal_content(mocker, unmarshal):
    request_body = mocker.Mock(media='2018-01-02', media_type=MEDIA_TYPE)
    request_body_spec_dict = {
        'content': {
            MEDIA_TYPE: {'schema': {'type': 'string', 'format': 'date'}}
        }
    }
    result = unmarshal(request_body, request_body_spec_dict)

    assert result == (datetime.date(2018, 1, 2), None)


def test_unmarshal_content_error(mocker, unmarshal):
    request_body = mocker.Mock(
        media=str('2018/01/02'), media_type='application/json'
    )
    request_body_spec_dict = {
        'content': {
            MEDIA_TYPE: {'schema': {'type': 'string', 'format': str('date')}}
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
    assert error.schema_path == deque(
        ['content', MEDIA_TYPE, 'schema', 'format']
    )
    assert error.path == deque([])
