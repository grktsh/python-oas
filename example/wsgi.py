import dataclasses
import pathlib
import re

import yaml
from flask import _request_ctx_stack
from flask import abort
from flask import Flask
from flask import jsonify
from flask import request

import oas

_uri_template_re = re.compile(r'<(?:[^:]+:)?([^>]+)>')


class FlaskOAS:
    def __init__(self, spec_dict):
        self.spec = oas.create_spec_from_dict(spec_dict)

    @property
    def request(self):
        ctx = _request_ctx_stack.top
        if ctx is None:
            raise RuntimeError('Outside of the request context')

        if not hasattr(ctx, 'oas_request'):
            ctx.oas_request = self._unmarshal_request()
        return ctx.oas_request

    def _unmarshal_request(self):
        oas_req = FlaskRequestAdapter(request)
        operation = self.spec.get_operation(
            oas_req.uri_template, oas_req.method, oas_req.media_type
        )
        schema_unmarshaler = oas.SchemaUnmarshaler(spec=self.spec)
        return oas.unmarshal_request(schema_unmarshaler, oas_req, operation)


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


@dataclasses.dataclass
class Pet:
    id: int
    name: str


PETS = []

app = Flask(__name__)

spec_path = pathlib.Path(__file__).parents[1] / 'tests/petstore.yaml'
with spec_path.open() as f:
    spec_dict = yaml.safe_load(f)
flask_oas = FlaskOAS(spec_dict)


@app.errorhandler(oas.exceptions.UndocumentedMediaType)
def handle_undocumented_media_type(e):
    return str(e), 400


@app.errorhandler(oas.exceptions.UnmarshalError)
def handle_unmarshal_error(e):
    return str(e), 400


@app.route('/api/v1/pets', methods=['GET', 'POST'])
def collection():
    _, request_body = flask_oas.request

    if request.method == 'POST':
        pet = Pet(id=len(PETS) + 1, name=request_body['name'])
        PETS.append(pet)
        return dataclasses.asdict(pet)
    else:
        return jsonify([dataclasses.asdict(pet) for pet in PETS])


@app.route('/api/v1/pets/<pet_id>')
def item(pet_id):
    parameters, _ = flask_oas.request

    for pet in PETS:
        if pet.id == parameters['path']['pet_id']:
            return dataclasses.asdict(pet)
    abort(404)
