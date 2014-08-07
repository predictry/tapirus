__author__ = 'guilherme'

def ent(x):
    if x is None:
        return ''
    else:
        return x + ' '


def error(err, o=None, p=None):

    errors = {
        'ResourceDoesNotExist': dict(error="Resource " + ent(o) + "not found",
                                     message="Resource " + ent(o) + "with that ID does not exist", status=404),
        'ResourceIdNotProvided': dict(error="Resource " + ent(o) + "{id} property not provided",
                                      message="Resource " + ent(o) + "{id} property must be specified",
                                      status=400),
        'ResourceAlreadyExists': dict(error="Resource already exists",
                                      message="Resource " + ent(o) + "with that ID already exists", status=400),
        'MissingParameter': dict(error="Missing parameter",
                                       message="The parameter " + ent(p) + "is missing from your request", status=400),
        'Unknown': dict(error="An unknown error has occurred",
                        message="For unknown reasons, the transaction has failed", status=500)
    }

    if err in errors:
        e = errors[err]
    else:
        e = errors['Unknown']

    return e