from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from jsonschema import Draft4Validator
from jsonschema import validators

from ..exceptions import ValidationError


def _nullable(base_validator):
    def _validator(validator, v, instance, schema):
        if instance is None and schema.get('nullable'):
            return
        for error in base_validator(validator, v, instance, schema):
            yield error

    return _validator


_Validator = validators.extend(
    Draft4Validator,
    {
        'type': _nullable(Draft4Validator.VALIDATORS['type']),
        'enum': _nullable(Draft4Validator.VALIDATORS['enum']),
    },
)


class SchemaValidator(object):
    def __init__(self, schema, format_checker=None):
        self._validator = _Validator(schema, format_checker=format_checker)

    def validate(self, instance, schema):
        errors = list(self._validator.iter_errors(instance, schema))
        if errors:
            raise ValidationError(errors)
