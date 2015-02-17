__author__ = 'guilherme'


import gzip
import traceback
import codecs

from tapirus.utils import jsonuri
from tapirus.operator import schema
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

                date, time, ip, path, status = l[0], l[1], l[4], l[7], int(l[8])

                if ".gif" not in path or status not in [0, 200, 304]:
                    continue

                try:

                    payload = jsonuri.deserialize(l[11])

                except ValueError as e:

                    Logger.error("Error in deserialization of payload: [{0}]\n\t{1}".format(l[11], e))

                    continue

                queries.extend(schema.generate_queries(date, time, ip, path, payload))
                count += 1

            if count % batch_size == 0 and count > 0:

                #upload
                #run queries
                try:

                    processor(queries)

                except Exception as e:
                    Logger.error(traceback.format_exc())
                    raise e
                else:

                    print("[Processed {0} actions {{Total: {1}}}, with {2} queries]".format(
                        (count//batch_size + 1)*batch_size - count,
                        count,
                        len(queries))
                    )

                    Logger.info("[Processed {0} actions {{Total: {1}}}, with {2} queries]".format(
                        (count//batch_size + 1)*batch_size - count,
                        count,
                        len(queries))
                    )

                    queries.clear()

        if queries:

            try:

                processor(queries)

            except Exception as e:
                Logger.error(traceback.format_exc())
                raise e

            else:
                print("[Processed {0} actions {{Total: {1}}}, with {2} queries.".format(
                    (count//batch_size + 1)*batch_size - count,
                    count,
                    len(queries))
                )

                Logger.info("[Processed {0} actions {{Total: {1}}}, with {2} queries.".format(
                    (count//batch_size + 1)*batch_size - count,
                    count,
                    len(queries))
                )

                queries.clear()

    Logger.info("Processed [`{0}`] records in log file [`{1}`]".format(count, file_name.split("/")[-1]))