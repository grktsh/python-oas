from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Content(object):
    @abc.abstractproperty
    def media_type(self):
        """Return the media type of the content without parameter."""
        # TODO: Support parameter

    @abc.abstractproperty
    def media(self):
        """Return deserialized content."""
