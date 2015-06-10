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

    def __str__(self):

        return "Record(id={0}, date={1}, hour={2}, last_updated={3}, status={4}, uri={5})".format(
            self.id, self.date, self.hour, self.last_updated, self.status, self.uri
        )
