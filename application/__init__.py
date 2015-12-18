from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import json
from flask.ext.api.exceptions import APIException, ParseError, NotFound
from flask.ext.api import status


app = Flask(__name__)
db = SQLAlchemy(app)

# Register routes after establishing the db prevents improperly loaded modules
# caused from circular imports
from .deed.views import deed_bp
app.config.from_pyfile("config.py")
app.register_blueprint(deed_bp, url_prefix='/deed')


@app.route("/health")
def check_status():
    return json.dumps({"Status": "OK"})


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(APIException)
def handle_parse_error(error):

    def lookup(error):
        try:
            map = {
                ParseError: [error.detail, status.HTTP_400_BAD_REQUEST],
                APIException: [error.detail,
                                status.HTTP_500_INTERNAL_SERVER_ERROR],
                NotFound: [error.detail, status.HTTP_404_NOT_FOUND]
            }
            res = map[type(error)][0], map[type(error)][1]
        except Exception:
            return error.detail, status.HTTP_500_INTERNAL_SERVER_ERROR

    return lookup(error)
