from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import iteritems

from ..exceptions import ValidationError
from ..utils import cached_property
from .formats import default_formats
from .validators import SchemaValidator


class SchemaUnmarshaler(object):
    def __init__(self, spec=None, formats=None):
        if formats is None:
            formats = default_formats

        self._spec = spec
        self._formats = formats

    def unmarshal(self, instance, schema):
        """Validate and unmarshal the instance with the schema.

        :meth:`~._unmarshal` can assume the validated instance.
        """
        self._validator.validate(instance, schema)
        return self._unmarshal(instance, schema)

    @cached_property
    def _validator(self):
        return SchemaValidator(
            self._spec.data if self._spec is not None else {},
            format_checker=self._formats.format_checker,
        )

    def _unmarshal(self, instance, schema):
        if instance is None:
            # Support nullable value
            return instance

        if 'allOf' in schema:
            sub_schemas = iter(schema['allOf'])
            result = self._unmarshal(instance, next(sub_schemas))
            # If the first sub-schema of ``allOf`` specifies an object, also
            # unmarshal the remaining sub-schemas and merge the results.
            if schema['allOf'][0].get('type', 'object') == 'object':
                for sub_schema in sub_schemas:
                    for k, v in iteritems(
                        self._unmarshal(instance, sub_schema)
                    ):
                        # If ``sub_schema``s have the same property and
                        # the former unmarshaling has modified the value of the
                        # property, the former result wins.
                        if k not in result or result[k] == instance[k]:
                            result[k] = v
            return result

        for sub_schema in schema.get('oneOf') or schema.get('anyOf') or []:
            try:
                # TODO: Remove duplicate validation
                return self.unmarshal(instance, sub_schema)
            except ValidationError:
                pass

        try:
            handler = self._unmarshalers[schema['type']]
        except KeyError:
            return instance
        else:
            return handler(self, instance, schema)

    def _unmarshal_array(self, instance, schema):
        # ``items`` MUST be present if the ``type`` is ``array``.
        return [self._unmarshal(x, schema['items']) for x in instance]

    def _unmarshal_object(self, instance, schema):
        try:
            properties = schema['properties']
        except KeyError:
            properties = {}

        result = {}

        for name, sub_schema in iteritems(properties):
            try:
                value = instance[name]
            except KeyError:
                try:
                    value = sub_schema['default']
                except KeyError:
                    continue
            result[name] = self._unmarshal(value, sub_schema)

        additional_properties = schema.get('additionalProperties', True)
        if isinstance(additional_properties, dict):
            for k, v in iteritems(instance):
                if k not in properties:
                    result[k] = self._unmarshal(v, additional_properties)
        elif additional_properties is True:
            for k, v in iteritems(instance):
                if k not in properties:
                    result[k] = v

        return result

    def _unmarshal_primitive(self, instance, schema):
        try:
            modifier = self._formats[schema['format']]
        except KeyError:
            return instance
        else:
            return modifier(instance)

    _unmarshalers = {
        'integer': _unmarshal_primitive,
        'number': _unmarshal_primitive,
        'boolean': _unmarshal_primitive,
        'string': _unmarshal_primitive,
        'array': _unmarshal_array,
        'object': _unmarshal_object,
    }
