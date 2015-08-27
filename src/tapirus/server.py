import urllib.parse
import datetime
from functools import wraps

from flask import Flask
from flask import Response
from flask import jsonify
from flask import request
import flask
import tapirus.constants
from webargs import Arg
from webargs.flaskparser import use_args
from tapirus.utils import io
from tapirus.repo.dao import RecordDAO
from tapirus.domain import RecordDomain
from tapirus import constants

app = Flask(__name__, static_folder="../../static", template_folder="../../static/templates")


def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                    .replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return flask.render_template(template_name, **ctx)
        return decorated_function
    return decorator


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
    'hour': Arg(int, required=True, validate=lambda x: 0 <= x <= 23, error='Invalid hour', location='query'),
    'tenant': Arg(str, required=False, default=None, location='query', validate=lambda x: len(x) > 1,
                  error='Invalid tenant Id')
})
def records(args):
    date = args['date']
    hour = args['hour']
    tenant = args['tenant']

    if not io.validate_date(date):
        message = 'Invalid date. Format: YYYY-mm-dd'

        return jsonify(dict(message=message)), 400

    if not io.validate_hour(str(hour)):
        message = 'Invalid hour. Format: HH, [0-23]'

        return jsonify(dict(message=message)), 400

    timestamp = io.parse_timestamp(date=date, hour=str(hour))

    record = RecordDomain.update_record_status(timestamp=timestamp)

    # record = RecordDAO.read(timestamp=timestamp)
    tenant_records = RecordDomain.get_tenant_records(timestamp=timestamp, tenant=tenant)

    data = {
        'date': str(record.timestamp.date()),
        'hour': record.timestamp.hour,
        'status': record.status,
        'record_files': [
            {'tenant': x.tenant, 'uri': x.uri} for x in tenant_records
            ],
        'last_updated': str(record.last_updated)
    }

    status = 404 if record.status == tapirus.constants.STATUS_NOT_FOUND else 200

    return jsonify(data), status


@app.route('/records/interval/', methods=['GET'])
@use_args({
    'startDate': Arg(str, required=True, location='query'),
    'startHour': Arg(int, required=True, validate=lambda x: 0 <= x <= 23, error='Invalid hour', location='query'),
    'endDate': Arg(str, required=True, location='query'),
    'endHour': Arg(int, required=True, validate=lambda x: 0 <= x <= 23, error='Invalid hour', location='query'),
    'tenant': Arg(str, required=False, default=None, location='query', validate=lambda x: len(x) > 1,
                  error='Invalid tenant Id')
})
def interval_records(args):
    start_date = args['startDate']
    start_hour = args['startHour']
    end_date = args['endDate']
    end_hour = args['endHour']
    tenant = args['tenant']

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
    if time_delta.total_seconds() > 60 * 60 * (48 - 1):
        end_timestamp = start_timestamp + datetime.timedelta(seconds=60 * 60 * (48 - 1))

    delta = datetime.timedelta(hours=1)

    timestamp = start_timestamp

    while timestamp <= end_timestamp:
        _ = RecordDomain.update_record_status(timestamp)

        timestamp = timestamp + delta

    records = RecordDAO.get_records(start_timestamp=start_timestamp,
                                    end_timestamp=end_timestamp)

    results = []

    for record in records:
        tenant_records = RecordDomain.get_tenant_records(timestamp=record.timestamp, tenant=tenant)

        result = {'date': str(record.timestamp.date()),
                  'hour': record.timestamp.hour,
                  'status': record.status,
                  'record_files': [{'tenant': x.tenant, 'uri': x.uri} for x in tenant_records],
                  'last_updated': str(record.last_updated)
                  }

        results.append(result)

    metadata = {
        'startDate': str(start_timestamp.date()),
        'startHour': start_timestamp.hour,
        'endDate': str(end_timestamp.date()),
        'endHour': end_timestamp.hour,
        'tenant': tenant if tenant else "*"
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
    'tenant': Arg(str, required=False, default=None, location='query', validate=lambda x: len(x) > 1,
                  error='Invalid tenant Id')
})
def timeline(args):
    limit = args['limit']
    skip = args['skip']
    reverse = args['reverse']
    tenant = args['tenant']

    records = RecordDAO.list(skip=skip, limit=limit, reverse=reverse)

    # results = [
    #     {'date': str(record.timestamp.date()), 'hour': record.timestamp.hour,
    #      'status': record.status, 'uri': record.uri,
    #      'last_updated': str(record.last_updated)} for record in records
    # ]

    results = []

    for record in records:
        tenant_records = RecordDomain.get_tenant_records(timestamp=record.timestamp, tenant=tenant)

        result = {'date': str(record.timestamp.date()),
                  'hour': record.timestamp.hour,
                  'status': record.status,
                  'record_files': [{'tenant': x.tenant, 'uri': x.uri} for x in tenant_records],
                  'last_updated': str(record.last_updated)
                  }

        results.append(result)

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
            'tenant': tenant if tenant else "*"
        },
        'records': results
    }

    return jsonify(data), 200


@app.route('/dev/playground', methods=['GET', 'POST'])
@templated('payload.html')
def debug():

    print(request)

    if request.method == 'POST':

        data = request.form['data']
        doublepass = request.form['doublepass']

        from tapirus.parser.v1 import pl
        from tapirus.repo import models
        from jsonuri import jsonuri

        flags = {'decode.double': False}

        if doublepass:
            flags['decode.double'] = True

        payload = None
        errors = []

        if not data:
            return dict(errors=errors, message='Empty Payload')

        if flags['decode.double']:

            try:

                payload = jsonuri.deserialize(data, decode_twice=True)

                if not pl.is_valid_schema(payload):
                    raise ValueError("Invalid data schema, double decoding-pass")

            except ValueError:

                if payload:

                    faults = pl.detect_schema_errors(
                        models.Error(
                            constants.ERROR_INVALIDSCHEMA_DD,
                            payload,
                            None
                        )
                    )

                    errors.extend(faults)

                else:

                    faults = pl.detect_schema_errors(
                        models.Error(
                            constants.ERROR_DESERIALIZATION_DD,
                            data,
                            None
                        )
                    )

                    errors.extend(faults)

                try:

                    payload = jsonuri.deserialize(data, decode_twice=False)

                    if not pl.is_valid_schema(payload):
                        raise ValueError("Invalid data schema, single decoding-pass")

                except ValueError:

                    if payload:

                        faults = pl.detect_schema_errors(
                            models.Error(
                                constants.ERROR_INVALIDSCHEMA_SD,
                                payload,
                                None
                            )
                        )

                        errors.extend(faults)

                    else:

                        faults = pl.detect_schema_errors(
                            models.Error(
                                constants.ERROR_DESERIALIZATION_SD,
                                data,
                                None
                            )
                        )

                        errors.extend(faults)

        else:

            try:

                payload = jsonuri.deserialize(data, decode_twice=False)

                if not pl.is_valid_schema(payload):
                    raise ValueError("Invalid data schema, single decoding-pass")

            except ValueError:

                if payload:

                    faults = pl.detect_schema_errors(
                        models.Error(
                            constants.ERROR_INVALIDSCHEMA_SD,
                            payload,
                            None
                        )
                    )

                    errors.extend(faults)

                else:

                    faults = pl.detect_schema_errors(
                        models.Error(
                            constants.ERROR_DESERIALIZATION_SD,
                            data,
                            None
                        )
                    )

                    errors.extend(faults)

        if payload:
            import json
            payload = json.dumps(payload, indent=4)

        return dict(data=data, payload=payload, doublepass=flags['decode.double'], faults=errors)

    else:

        return dict()


@app.route('/', methods=['GET'])
def index():

    def url(path):

        return ''.join([request.scheme, '://', request.host, path])

    data = {
        'api': {
            'records': {
                'href': url('/records/')
            },
            'interval': {
                'href': url('/records/interval')
            },
            'timeline': {
                'href': url('/records/timeline')
            }
        },
        'help': {
            'href': url('/help')
        },
        'playground': {
            'href': url('/dev/playground')
        }
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


if not app.debug:
    from tapirus.utils import config
    from tapirus.utils.logger import Logger

    logging = config.get("logging")

    Logger.setup_logging(logging["logconfig"])


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

# TODO: add support for response in XML
