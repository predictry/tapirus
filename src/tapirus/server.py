import urllib.parse

from flask import Flask, Response
from flask import jsonify
import flask
from webargs import Arg
from webargs.flaskparser import use_args

from tapirus.utils.io import parse_date, validate_hour, validate_date
from tapirus.dao import RecordDAO

app = Flask(__name__)


def list_endpoints():

    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        url = flask.url_for(rule.endpoint, **options)

        if rule.endpoint != "static":
            doc = app.view_functions[rule.endpoint].__doc__
        else:
            doc = ""

        output.append(dict(endpoint=rule.endpoint, methods=rule.methods, url=url, doc=doc))

    return output


@app.route("/help", methods=['GET'])
def endpoints():
    """List available endpoints."""

    output = []
    for entry in list_endpoints():

        line = urllib.parse.unquote(
            "{:50s} {:20s} {} => [{}]".format(
                entry["endpoint"],
                ','.join([x for x in entry["methods"] if x not in ("OPTIONS", "HEAD")]),
                entry["url"],
                entry["doc"]
            )
        )

        output.append(line)

    options = '\n'.join([line for line in sorted(output)])

    return Response(response=options, status=200, mimetype="text/plain")


@app.route("/records", methods=["GET"])
@use_args({
    "date": Arg(str, required=True, location="query"),
    "hour": Arg(int, required=True, validate=lambda x: 0 <= x <= 23, error="Invalid hour", location="query")
})
def records(args):

    date = args["date"]
    hour = args["hour"]

    if not validate_date(date):

        message = "Invalid date. Format: YYYY-mm-dd"

        return jsonify(dict(message=message)), 400

    if not validate_hour(str(hour)):

        message = "Invalid hour. Format: HH, [0-23]"

        return jsonify(dict(message=message)), 400

    record = RecordDAO.read(parse_date(date), hour)

    return jsonify(record), 404


@app.route("/records/interval", methods=["GET"])
@use_args({
    "startDate": Arg(str, required=True, location="query"),
    "startHour": Arg(int, required=True, validate=lambda x: 0 <= x <= 23, error="Invalid hour", location="query"),
    "endDate": Arg(str, required=True, location="query"),
    "endHour": Arg(int, required=True, validate=lambda x: 0 <= x <= 23, error="Invalid hour", location="query")
})
def interval_records(args):

    start_date = args["startDate"]
    start_hour = args["startHour"]
    end_date = args["endDate"]
    end_hour = args["endHour"]

    if not validate_date(start_date):

        return jsonify(dict(message="Invalid start date. Format: YYYY-mm-dd")), 400

    if not validate_date(end_date):

        return jsonify(dict(message="Invalid end date. Format: YYYY-mm-dd")), 400

    if not validate_hour(str(start_hour)):

        return jsonify(dict(message="Invalid start hour. Format: HH, [0-23]")), 400

    if not validate_hour(str(end_hour)):

        return jsonify(dict(message="Invalid end hour. Format: HH, [0-23]")), 400

    records = [x.properties for x in RecordDAO.get_records(
        parse_date(start_date),
        start_hour,
        parse_date(end_date),
        end_hour
    )]

    data = dict(records=records, count=len(records))

    return jsonify(data), 200


@app.route("/timeline", methods=["GET"])
@use_args({

})
def timeline(args):

    data = {
        "start": {
            "date": None,
            "hour": None
        },
        "end": {
            "date": None,
            "hour": None
        },
        "count": 0,
        "missing": 0
    }

    return jsonify(data), 200


@app.route("/", methods=["GET"])
def index():

    data = {
        "message": "Go!"
    }

    return jsonify(data), 200


@app.errorhandler(400)
def handle_bad_request(err):
    data = getattr(err, 'data', None)
    if data:
        err_message = data['message']
    else:
        err_message = 'Invalid request'
    return jsonify({
        'message': err_message,
    }), 400


@app.errorhandler(500)
def handle_bad_request(err):
    data = getattr(err, 'data', None)
    if data:
        err_message = data['message']
    else:
        err_message = 'Internal Server Error'
    return jsonify({
        'message': err_message,
    }), 500


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
