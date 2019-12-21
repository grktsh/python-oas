from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six

from ..content.models import Content


@six.add_metaclass(abc.ABCMeta)
class Response(Content):
    @abc.abstractproperty
    def status_code(self):
        """Return the status code."""

    @abc.abstractproperty
    def header(self):
        """Return the header parameters."""
