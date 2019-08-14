python-oas
==========

.. image:: https://img.shields.io/pypi/v/oas.svg
   :alt: PyPI
   :target: https://pypi.org/project/oas

.. image:: https://img.shields.io/travis/grktsh/python-oas/master.svg
   :alt: Travis
   :target: https://travis-ci.org/grktsh/python-oas

.. image:: https://img.shields.io/codecov/c/github/grktsh/python-oas/master.svg
   :alt: Codecov
   :target: https://codecov.io/gh/grktsh/python-oas

Prerequisites
-------------

- Validated OpenAPI 3 document

  - python-oas does not validate OpenAPI 3 document itself at runtime.  It should be validated in advance.

Example
-------

.. code-block:: python

   import flask
   import oas

   app = flask.Flask(__name__)
   spec = oas.create_spec_from_dict(spec_dict)


   @app.route('/example')
   def example():
       # Create an instance of the subclass of oas.Request.
       oas_req = FlaskRequestAdapter(flask.request)
       # Find Operation Object for the request.
       operation = spec.get_operation(
          oas_req.uri_template, oas_req.method, oas_req.media_type
       )
       # Unmarshal the request and obtain unmarshaled parameters and
       # request body.
       schema_unmarshaler = oas.SchemaUnmarshaler(spec=spec)
       parameters, request_body = oas.unmarshal_request(
          schema_unmarshaler, oas_req, operation
       )
       # ...
       return flask.jsonify({...})

``spec.get_operation()`` and ``oas.unmarshal_request()`` may raise ``oas.exceptions.UndocumentedMediaType`` and ``oas.exceptions.UnmarshalError`` respectively. You should register error handlers for them:

.. code-block:: python

   @app.errorhandler(oas.exceptions.UndocumentedMediaType)
   def handle_undocumented_media_type(e):
       return str(e), 400


   @app.errorhandler(oas.exceptions.UnmarshalError)
   def handle_unmarshal_error(e):
       return str(e), 400

``FlaskRequestAdapter`` might be something like the following:

.. code-block:: python

   import re

   _uri_template_re = re.compile(r'<(?:[^:]+:)?([^>]+)>')


   class FlaskRequestAdapter(oas.Request):

       def __init__(self, request):
           self._request = request

       @property
       def uri_template(self):
           url_rule = self._request.url_rule
           if url_rule is not None:
               return _uri_template_re.sub(r'{\1}', url_rule.rule)

       @property
       def method(self):
           return self._request.method.lower()

       @property
       def context(self):
           return None

       @property
       def path(self):
           return self._request.view_args

       @property
       def query(self):
           return self._request.args

       @property
       def header(self):
           return self._request.headers

       @property
       def cookie(self):
           return self._request.cookies

       @property
       def content_length(self):
           return self._request.content_length

       @property
       def media_type(self):
           content_type = self._request.content_type
           if content_type is not None:
               return content_type.split(';', 1)[0]

       @property
       def media(self):
           # TODO: Support media types other than JSON
           return self._request.json


Related projects
----------------

- `falcon-oas <https://github.com/grktsh/falcon-oas>`_ promotes the design first approach with OpenAPI 3 for Falcon
