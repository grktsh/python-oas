from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six

from ..parameters.models import Parameters
from ..request_body.models import RequestBody


@six.add_metaclass(abc.ABCMeta)
class Request(Parameters, RequestBody):
    @abc.abstractproperty
    def uri_template(self):
        """Return the key of Path Item Object with the base path."""

    @abc.abstractproperty
    def method(self):
        """Return the HTTP method of Operation Object."""

    @abc.abstractproperty
    def context(self):
        """Return the request context."""
