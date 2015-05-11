__author__ = 'guilherme'


import gzip
import traceback
import codecs
import time

import dateutil.parser
import dateutil.tz
from jsonuri import jsonuri

from tapirus.processor import schema
from tapirus.utils.logger import Logger


LOG_FILE_COLUMN_SEPARATOR = "\t"


def process_log(file_name, batch_size, processor, transformer=None):
    """

    :param file_name:
    :return:
    """

    entries = []

    gz_fh = gzip.open(file_name)
    utf8_codec = codecs.getreader("UTF-8")

    with utf8_codec(gz_fh) as f:
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
        line_index = 0

        try:
            for line in f:

                l = line.split(LOG_FILE_COLUMN_SEPARATOR)

                if len(l) >= 12:

                    date, timestamp, ip, path, status = l[0], l[1], l[4], l[7], int(l[8])

                    if ".gif" not in path or status not in [0, 200, 304]:
                        continue

                    try:

                        payload = jsonuri.deserialize(l[11], False)

                    except ValueError as e:

                        Logger.warning(
                            "Error deserializing payload, single decoding, line index [{0}]\n\t{1}".format(
                                line_index, e
                            )
                        )

                        try:
                            payload = jsonuri.deserialize(l[11], True)
                        except ValueError as e:

                            Logger.warning(
                                "Error deserializing payload, double decoding, line index [{0}]\n\t{1}".format(
                                    line_index, e
                                )
                            )

                            line_index += 1

                            continue

                    if "date" not in payload:
                        payload["date"] = date
                    if "time" not in payload:
                        payload["time"] = time
                    if "datetime" not in payload:
                        payload["datetime"] = dateutil.parser.parse(''.join([date, "T", time, "Z"]))

                    if transformer:
                        entries.extend(transformer(payload))
                    else:
                        entries.append(payload)

                    count += 1
                    line_index += 1

                if count % batch_size == 0 and count > 0:

                    #upload
                    #run entries
                    try:

                        start = time.time()
                        processor(entries)
                        end = time.time()

                    except Exception as e:
                        Logger.error(traceback.format_exc())
                        raise e
                    else:

                        Logger.info("[Processed {0} actions {{Total: {1}}}, with {2} entries] in {3}s.".format(
                            (count//batch_size + 1)*batch_size - count,
                            count,
                            len(entries),
                            end-start)
                        )

                        del entries[:]

        except EOFError as exc:

            Logger.error(exc)

        if entries:
            #We're exiting before we process the remaining entries because their number if not a multiple of batch_size

            try:
                start = time.time()
                processor(entries)
                end = time.time()
                #pass

            except Exception as e:
                Logger.error(traceback.format_exc())
                raise e

            else:
                Logger.info("[Processed {0} actions {{Total: {1}}}, with {2} entries in {3}s.".format(
                    count - (count//batch_size)*batch_size,
                    count,
                    len(entries),
                    end-start)
                )

                del entries[:]

    Logger.info("Processed [`{0}`] records in log file [`{1}`]".format(count, file_name.split("/")[-1]))