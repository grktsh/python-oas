from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Parameters(object):
    @abc.abstractproperty
    def path(self):
        """Return the path parameters."""

    @abc.abstractproperty
    def query(self):
        """Return the query parameters."""

    @abc.abstractproperty
    def header(self):
        """Return the header parameters."""

    @abc.abstractproperty
    def cookie(self):
        """Return the header parameters."""
