class Record(object):

    def __init__(self, id, timestamp, last_updated, status):

        self.id = id
        self.timestamp = timestamp
        self.last_updated = last_updated
        self.status = status

    @property
    def properties(self):

        return self.__dict__

    def __str__(self):

        return "Record[id={0}, timestamp={1}, last_updated={2}, status={3}]".format(
            self.id, self.timestamp, self.last_updated, self.status
        )


class TenantRecord(object):

    def __init__(self, id, tenant, timestamp, last_updated, uri):

        self.id = id
        self.tenant = tenant
        self.timestamp = timestamp
        self.last_updated = last_updated
        self.uri = uri

    @property
    def properties(self):

        return self.__dict__

    def __str__(self):

        return "TenantRecord[id={0}, tenant={1}, timestamp={2}, last_updated={3}, uri={4}]".format(
            self.id, self.tenant, self.timestamp, self.last_updated, self.uri
        )


class LogFile(object):

    def __init__(self, id, record, log, filepath):

        self.id = id
        self.record = record
        self.log = log
        self.filepath = filepath

    @property
    def properties(self):

        return self.__dict__

    def __str__(self):

        return "LogFile[id={0}, record={1}, log={2}, filepath={3}]".format(
            self.id, self.record, self.log, self.filepath
        )


class Error(object):

    def __init__(self, code, data, timestamp):

        self.code = code
        self.data = data
        self.timestamp = timestamp

    def __repr__(self):

        return "{0},{1},{2}".format(
            self.code, self.data, str(self.timestamp)
        )
