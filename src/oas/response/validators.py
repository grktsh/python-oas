from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import iteritems

from ..content.unmarshalers import unmarshal_content
from ..exceptions import UndocumentedResponse
from ..exceptions import ValidationError
from ..parameters.unmarshalers import unmarshal_parameters


def validate_response(schema_unmarshaler, response, operation):
    errors = []

    for status_code in (str(response.status_code), 'default'):
        try:
            response_spec_dict = operation['responses'][status_code]
        except KeyError:
            pass
        else:
            break
    else:
        raise UndocumentedResponse()

    if 'headers' in response_spec_dict:
        parameter_spec_dicts = [
            dict(definition, **{'name': name, 'in': 'header'})
            for name, definition in iteritems(response_spec_dict['headers'])
            if name.lower() != 'content-type'
        ]

        _, headers_errors = unmarshal_parameters(
            schema_unmarshaler, response, parameter_spec_dicts
        )
        if headers_errors:
            for error in headers_errors:
                error.schema_path.extendleft(
                    ['headers', status_code, 'responses']
                )
            errors.extend(headers_errors)

    if 'content' in response_spec_dict:
        _, content_errors = unmarshal_content(
            schema_unmarshaler, response, response_spec_dict['content']
        )
        if content_errors:
            for error in content_errors:
                error.schema_path.extendleft(
                    ['content', status_code, 'responses']
                )
            errors.extend(content_errors)

    if errors:
        raise ValidationError(errors)
