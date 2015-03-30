__author__ = 'guilherme'


import gzip
import traceback
import codecs
import time

from jsonuri import jsonuri
from tapirus.processor import schema
from tapirus.utils.logger import Logger


LOG_FILE_COLUMN_SEPARATOR = "\t"


def process_log(file_name, batch_size, processor):
    """

    :param file_name:
    :return:
    """

    queries = []

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

        for line in f:

            l = line.split(LOG_FILE_COLUMN_SEPARATOR)

            if len(l) >= 12:

                date, timestamp, ip, path, status = l[0], l[1], l[4], l[7], int(l[8])

                if ".gif" not in path or status not in [0, 200, 304]:
                    continue

                try:

                    payload = jsonuri.deserialize(l[11], False)

                except ValueError as e:

                    Logger.warning("Error deserializing payload, single decoding: [{0}]\n\t{1}".format(l[11], e))

                    try:
                        payload = jsonuri.deserialize(l[11], True)
                    except ValueError as e:

                        Logger.warning("Error deserializing payload, single twice: [{0}]\n\t{1}".format(l[11], e))

                        continue

                    continue

                queries.extend(schema.generate_queries(date, timestamp, ip, path, payload))
                count += 1

            if count % batch_size == 0 and count > 0:

                #upload
                #run queries
                try:

                    start = time.time()
                    processor(queries)
                    end = time.time()

                except Exception as e:
                    Logger.error(traceback.format_exc())
                    raise e
                else:

                    Logger.info("[Processed {0} actions {{Total: {1}}}, with {2} queries] in {3}s.".format(
                        (count//batch_size + 1)*batch_size - count,
                        count,
                        len(queries),
                        end-start)
                    )

                    del queries[:]

        if queries:
            #We're exiting before we process the remaining queries because their number if not a multiple of batch_size

            try:
                start = time.time()
                processor(queries)
                end = time.time()
                #pass

            except Exception as e:
                Logger.error(traceback.format_exc())
                raise e

            else:
                Logger.info("[Processed {0} actions {{Total: {1}}}, with {2} queries in {3}s.".format(
                    count - (count//batch_size)*batch_size,
                    count,
                    len(queries),
                    end-start)
                )

                del queries[:]

    Logger.info("Processed [`{0}`] records in log file [`{1}`]".format(count, file_name.split("/")[-1]))