class Record(object):

    def __init__(self, id, date, hour, last_updated, status, uri):

        self.id = id
        self.date = date
        self.hour = hour
        self.last_updated = last_updated
        self.status = status
        self.uri = uri

    @property
    def properties(self):

        return self.__dict__
