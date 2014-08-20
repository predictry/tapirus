__author__ = 'guilherme'


def ent(x):
    if x is None:
        return ''
    else:
        return x + ' '


def error(err, object=None, property=None):

    errors = {
        'ResourceDoesNotExist': dict(error="Resource " + ent(object) + "not found",
                                     message="Resource " + ent(object) + "with given properties does not exist.", status=404),
        'ResourceIdNotProvided': dict(error="Resource " + ent(object) + "{id} property not provided",
                                      message="Resource " + ent(object) + "{id} property must be specified.",
                                      status=400),
        'ResourceAlreadyExists': dict(error="Resource already exists",
                                      message="Resource " + ent(object) + "with that ID already exists.", status=400),
        'UndefinedParameter': dict(error="Undefined parameter value.",
                                   message="The parameter " + ent(property) + "must have a value.", status=400),
        'MissingParameter': dict(error="Missing parameter",
                                       message="The parameter " + ent(property) + "is missing from your request.", status=400),
        'Unknown': dict(error="An unknown error has occurred",
                        message="For unknown reasons, the transaction has failed.", status=500)

    }

    if err in errors:
        e = errors[err]
    else:
        e = errors['Unknown']

    return e