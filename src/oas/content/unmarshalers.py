from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..exceptions import UndocumentedMediaType
from ..exceptions import ValidationError


def unmarshal_content(schema_unmarshaler, content, content_spec_dict):
    try:
        media_type_spec_dict = content_spec_dict[content.media_type]
    except KeyError:
        raise UndocumentedMediaType()

    try:
        schema = media_type_spec_dict['schema']
    except KeyError:
        return content.media, None

    try:
        unmarshaled = schema_unmarshaler.unmarshal(content.media, schema)
    except ValidationError as e:
        for error in e.errors:
            error.schema_path.extendleft(['schema', content.media_type])
        return None, e.errors
    else:
        return unmarshaled, None
