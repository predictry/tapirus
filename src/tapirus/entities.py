class Record(object):

    def __init__(self, id, timestamp, last_updated, status, uri):

        self.id = id
        self.timestamp = timestamp
        self.last_updated = last_updated
        self.status = status
        self.uri = uri

    @property
    def properties(self):

        return self.__dict__

    def __str__(self):

        return "Record(id={0}, timestamp={1}, last_updated={2}, status={3}, uri={4})".format(
            self.id, self.timestamp, self.last_updated, self.status, self.uri
        )


class LogFile(object):

    def __init__(self, id, record, log, filepath):

        self.id = id
        self.record = record
        self.log = log
        self.filepath = filepath


class Error(object):

    def __init__(self, id, code, data, timestamp):

        self.id = id
        self.code = code
        self.data = data
        self.timestamp = timestamp
