from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six

from ..content.models import Content


@six.add_metaclass(abc.ABCMeta)
class RequestBody(Content):
    @abc.abstractproperty
    def content_length(self):
        """Return the content length."""
