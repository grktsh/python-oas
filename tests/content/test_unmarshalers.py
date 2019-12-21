# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import functools

import jsonschema
import pytest

from oas.content.models import Content
from oas.content.unmarshalers import unmarshal_content
from oas.exceptions import UndocumentedMediaType
from oas.schema.unmarshalers import SchemaUnmarshaler


class MockContent(Content):
    media_type = 'application/json'

    def __init__(self, media):
        self._media = media

    @property
    def media(self):
        return self._media


@pytest.fixture
def unmarshal():
    return functools.partial(unmarshal_content, SchemaUnmarshaler())


def test_undocumented_media_type(unmarshal):
    content = MockContent(media='foo')
    content_spec_dict = {}

    with pytest.raises(UndocumentedMediaType):
        unmarshal(content, content_spec_dict)


def test_undocumented_media_type_schema(unmarshal):
    content = MockContent(media='foo')
    content_spec_dict = {content.media_type: {}}

    result = unmarshal(content, content_spec_dict)

    assert result == ('foo', None)


def test_unmarshal_success(unmarshal):
    content = MockContent(media='2018-01-02')
    content_spec_dict = {
        content.media_type: {'schema': {'type': 'string', 'format': 'date'}}
    }
    result = unmarshal(content, content_spec_dict)

    assert result == (datetime.date(2018, 1, 2), None)


def test_unmarshal_error(unmarshal):
    content = MockContent(media=str('2018/01/02'))
    content_spec_dict = {
        content.media_type: {
            'schema': {'type': 'string', 'format': str('date')}
        }
    }
    _, errors = unmarshal(content, content_spec_dict)

    assert len(errors) == 1
    error = errors[0]
    assert isinstance(error, jsonschema.ValidationError)
    assert error.message == "'2018/01/02' is not a 'date'"
    assert error.validator == 'format'
    assert error.validator_value == 'date'
    assert error.schema == {'type': 'string', 'format': 'date'}
    assert list(error.schema_path) == [content.media_type, 'schema', 'format']
    assert list(error.path) == []
