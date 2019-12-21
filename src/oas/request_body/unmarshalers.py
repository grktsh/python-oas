from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import jsonschema

from ..content.unmarshalers import unmarshal_content


def unmarshal_request_body(
    schema_unmarshaler, request_body, request_body_spec_dict
):
    if not request_body.content_length:
        if request_body_spec_dict.get('required', False):
            error = jsonschema.ValidationError(
                'Request body is required',
                validator='required',
                validator_value=True,
                schema=request_body_spec_dict,
                schema_path=('required',),
            )
            return None, [error]
        return None, None

    unmarshaled, errors = unmarshal_content(
        schema_unmarshaler, request_body, request_body_spec_dict['content']
    )
    if errors:
        for error in errors:
            error.schema_path.appendleft('content')
    return unmarshaled, errors
