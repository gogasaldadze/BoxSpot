from flask import Flask, request
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
api = Api(app)

# Custom Validato
def name_validator(name):
    if not name.isalpha():
        raise BadRequest("Name must contain only alphabetic characters.")
    if len(name) > 5:
        raise BadRequest("Name must not exceed 5 characters.")
    return name

# Define a parser with the custom validator
parser = reqparse.RequestParser()
parser.add_argument('name', type=name_validator, required=True, help='Name must contain only alphabetic characters and must not exceed 5 characters.')

# Model for error responses
error_model = api.model('Error', {
    'message': fields.String(required=True, description='Error message'),
})

# Custom error handler
@api.errorhandler(BadRequest)
def handle_bad_request_error(e):
    return {'message': str(e)}, 400

# API Resource
@api.route('/validate_name')
class ValidateNameResource(Resource):
    @api.expect(parser)
    @api.response(200, 'Success')
    @api.response(400, 'Validation Error', model=error_model)
    def get(self):
        args = parser.parse_args()
        return {'name': args['name']}

if __name__ == '__main__':
    app.run(debug=True)
