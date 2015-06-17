import gzip
import codecs

import dateutil.parser
import dateutil.tz
from jsonuri import jsonuri

from tapirus.model.store import is_valid_schema
from tapirus.utils.logger import Logger
from tapirus import constants

LOG_FILE_COLUMN_SEPARATOR = "\t"

UNSENT, HTTP_OK, HTTP_NOT_MODIFIED = 0, 200, 304


def process_log(file_name, errors):
    """

    :param file_name:
    :return:
    """

    gz_fh = gzip.open(file_name)
    utf8_codec = codecs.getreader("UTF-8")

    assert isinstance(errors, list)

    with utf8_codec(gz_fh) as fp:
        """
            #indeces
            #0: date
            #1: time
            #4: ip
            #5: method
            #6: server
            #7: path
            #8: status
            #9: source page
            #10: agent (encoded)
            #11: payload
        """

        count = 0
        failed_count = 0
        line_index = 0

        try:
            for line in fp:

                columns = line.split(LOG_FILE_COLUMN_SEPARATOR)

                if len(columns) >= 12:

                    date, timestamp, ip, path, status = columns[0], columns[1], columns[4], columns[7], int(columns[8])

                    if ".gif" not in path or status not in (UNSENT, HTTP_OK, HTTP_NOT_MODIFIED):
                        continue

                    payload = None

                    try:

                        payload = jsonuri.deserialize(columns[11], decode_twice=True)

                        if not is_valid_schema(payload):
                            raise ValueError("Invalid data schema, double decoding-pass")

                    except ValueError as e:

                        if payload:

                            # TODO: log to error log
                            errors.append(
                                (constants.ERROR_INVALIDSCHEMA_SD,
                                 payload,
                                 dateutil.parser.parse(''.join([date, "T", timestamp, "Z"]))
                                 )
                            )
                        else:

                            # TODO: log to error log
                            errors.append(
                                (constants.ERROR_DESERIALIZATION_SD,
                                 columns[11],
                                 dateutil.parser.parse(''.join([date, "T", timestamp, "Z"]))
                                 )
                            )

                        Logger.info(
                            "Error deserializing payload, double decoding, line index [{0}]\n\t{1}".format(
                                line_index, e
                            )
                        )

                        try:

                            payload = jsonuri.deserialize(columns[11], decode_twice=False)

                            if not is_valid_schema(payload):

                                raise ValueError("Invalid data schema, single decoding-pass")

                        except ValueError as e:

                            if payload:

                                # TODO: log to error log

                                errors.append(
                                    (constants.ERROR_INVALIDSCHEMA_DD,
                                     payload,
                                     dateutil.parser.parse(''.join([date, "T", timestamp, "Z"]))
                                     )
                                )
                            else:

                                # TODO: log to error log
                                errors.append(
                                    (constants.ERROR_DESERIALIZATION_DD,
                                     columns[11],
                                     dateutil.parser.parse(''.join([date, "T", timestamp, "Z"]))
                                     )
                                )

                            Logger.info(
                                "Error deserializing payload, single decoding, line index [{0}]\n\t{1}".format(
                                    line_index, e
                                )
                            )

                            failed_count += 1
                            line_index += 1

                            continue

                    if "date" not in payload:
                        payload["date"] = date
                    if "time" not in payload:
                        payload["time"] = timestamp
                    if "datetime" not in payload:
                        payload["datetime"] = dateutil.parser.parse(''.join([date, "T", timestamp, "Z"]))

                    yield payload

                    count += 1
                    line_index += 1

        except EOFError as exc:

            Logger.error(exc)

        except OSError as exc:

            Logger.error(exc)

    Logger.info(
        "Successfully parsed [`{0}`] records, [`{1}`] failed, from log file [`{1}`]".format(
            count, failed_count, file_name.split("/")[-1]
        )
    )
