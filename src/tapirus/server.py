import urllib.parse
import datetime

from flask import Flask, Response
from flask import jsonify
import flask
from webargs import Arg
from webargs.flaskparser import use_args

from tapirus.utils import io
from tapirus.dao import RecordDAO
from tapirus.usecases import RecordUseCases
from tapirus import constants


app = Flask(__name__)


def list_endpoints():

    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = '[{0}]'.format(arg)

        url = flask.url_for(rule.endpoint, **options)

        if rule.endpoint != 'static':
            doc = app.view_functions[rule.endpoint].__doc__
        else:
            doc = ''

        output.append(dict(endpoint=rule.endpoint, methods=rule.methods, url=url, doc=doc))

    return output


@app.route('/help/', methods=['GET'])
def endpoints():
    """List available endpoints."""

    output = []
    for entry in list_endpoints():

        line = urllib.parse.unquote(
            '{:50s} {:20s} {} => [{}]'.format(
                entry['endpoint'],
                ','.join([x for x in entry['methods'] if x not in ('OPTIONS', 'HEAD')]),
                entry['url'],
                entry['doc']
            )
        )

        output.append(line)

    options = '\n'.join([line for line in sorted(output)])

    return Response(response=options, status=200, mimetype='text/plain')


@app.route('/records/', methods=['GET'])
@use_args({
    'date': Arg(str, required=True, location='query'),
    'hour': Arg(int, required=True, validate=lambda x: 0 <= x <= 23, error='Invalid hour', location='query')
})
def records(args):

    date = args['date']
    hour = args['hour']

    if not io.validate_date(date):

        message = 'Invalid date. Format: YYYY-mm-dd'

        return jsonify(dict(message=message)), 400

    if not io.validate_hour(str(hour)):

        message = 'Invalid hour. Format: HH, [0-23]'

        return jsonify(dict(message=message)), 400

    timestamp = io.parse_timestamp(date=date, hour=str(hour))

    # TODO: run update record first
    record = RecordUseCases.update_record_status(timestamp=timestamp)

    # record = RecordDAO.read(timestamp=timestamp)

    data = {
        'date': str(record.timestamp.date()),
        'hour': record.timestamp.hour,
        'status': record.status,
        'uri': record.uri
    }

    status = 404 if record.status == constants.STATUS_NOT_FOUND else 200

    return jsonify(data), status


@app.route('/records/interval/', methods=['GET'])
@use_args({
    'startDate': Arg(str, required=True, location='query'),
    'startHour': Arg(int, required=True, validate=lambda x: 0 <= x <= 23, error='Invalid hour', location='query'),
    'endDate': Arg(str, required=True, location='query'),
    'endHour': Arg(int, required=True, validate=lambda x: 0 <= x <= 23, error='Invalid hour', location='query')
})
def interval_records(args):

    start_date = args['startDate']
    start_hour = args['startHour']
    end_date = args['endDate']
    end_hour = args['endHour']

    if not io.validate_date(start_date):

        return jsonify(dict(message='Invalid start date. Format: YYYY-mm-dd')), 400

    if not io.validate_date(end_date):

        return jsonify(dict(message='Invalid end date. Format: YYYY-mm-dd')), 400

    if not io.validate_hour(str(start_hour)):

        return jsonify(dict(message='Invalid start hour. Format: HH, [0-23]')), 400

    if not io.validate_hour(str(end_hour)):

        return jsonify(dict(message='Invalid end hour. Format: HH, [0-23]')), 400

    start_timestamp = io.parse_timestamp(date=start_date, hour=str(start_hour))
    end_timestamp = io.parse_timestamp(date=end_date, hour=str(end_hour))

    if start_timestamp > end_timestamp:

        message = 'The end timestamp {0} is greater than the start timestamp {1}'.format(
            '-'.join([str(start_timestamp.date()), str(start_timestamp.hour)]),
            '-'.join([str(end_timestamp.date()), str(end_timestamp.hour)])
        )

        return jsonify(dict(message=message)), 400

    time_delta = end_timestamp - start_timestamp

    # Limit request period
    if time_delta.total_seconds() > 60*60*(48-1):

        end_timestamp = start_timestamp + datetime.timedelta(seconds=60*60*(48-1))

    # TODO: update record status first, for each hour

    delta = datetime.timedelta(hours=1)

    timestamp = start_timestamp

    while timestamp <= end_timestamp:

        _ = RecordUseCases.update_record_status(timestamp)

        timestamp = timestamp + delta

    records = RecordDAO.get_records(start_timestamp=start_timestamp,
                                    end_timestamp=end_timestamp)

    results = [
        {'date': str(record.timestamp.date()), 'hour': record.timestamp.hour,
         'status': record.status, 'uri': record.uri} for record in records
    ]

    metadata = {
        'startDate': str(start_timestamp.date()),
        'startHour': start_timestamp.hour,
        'endDate': str(end_timestamp.date()),
        'endHour': end_timestamp.hour
    }

    count = len(results)

    data = dict(metadata=metadata, records=results, count=count)

    return jsonify(data), 200


@app.route('/records/timeline/', methods=['GET'])
@use_args({
    'limit': Arg(int, required=False, default=24, validate=lambda x: 24 > x >= 1,
                 error='Limit must be between 1 and 24', location='query'),
    'skip': Arg(int, required=False, default=0, validate=lambda x: x >= 0,
                error='Skip must be greater than 0', location='query'),
    'reverse': Arg(bool, required=False, default=False, location='query'),
})
def timeline(args):

    limit = args['limit']
    skip = args['skip']
    reverse = args['reverse']

    records = RecordDAO.list(skip=skip, limit=limit, reverse=reverse)

    results = [
        {'date': str(record.timestamp.date()), 'hour': record.timestamp.hour,
         'status': record.status, 'uri': record.uri} for record in records
    ]

    count = len(results)
    total = RecordDAO.count()

    if reverse:
        start_index = 0
        end_index = -1
    else:
        start_index = -1
        end_index = 0

    data = {
        'metadata': {
            'timeline': {
                'start': {
                    'date': results[start_index]['date'] if results else None,
                    'hour': results[start_index]['hour'] if results else None,
                },
                'end': {
                    'date': results[end_index]['date'] if results else None,
                    'hour': results[end_index]['hour'] if results else None
                }
            },
            'count': count,
            'total': total,
        },
        'records': results
    }

    return jsonify(data), 200


@app.route('/', methods=['GET'])
def index():

    return Response('Go!', status=200, mimetype='text/plain')


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


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

# TODO: add support for response in XML
