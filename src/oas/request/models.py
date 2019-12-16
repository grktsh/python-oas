from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class RequestParameters(object):
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


@six.add_metaclass(abc.ABCMeta)
class RequestBody(object):
    @abc.abstractproperty
    def content_length(self):
        """Return the content length."""

    @abc.abstractproperty
    def media_type(self):
        """Return the media type of the request without parameter."""

    @abc.abstractproperty
    def media(self):
        """Return deserialized request body."""


@six.add_metaclass(abc.ABCMeta)
class Request(RequestParameters, RequestBody):
    @abc.abstractproperty
    def uri_template(self):
        """Return the key of Path Item Object with the base path."""

    @abc.abstractproperty
    def method(self):
        """Return the HTTP method of Operation Object."""

    @abc.abstractproperty
    def context(self):
        """Return the request context."""
