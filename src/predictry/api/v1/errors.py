__author__ = 'guilherme'


def error(err, e=None, property=None):

    def append(x):
        if x is None:
            return ''
        else:
            return x + ' '

    errors = {
        'ResourceDoesNotExist': dict(error="Resource " + append(e) + "not found",
                                     message="Resource " + append(e) + "with given properties does not exist.", status=404),
        'ResourceIdNotProvided': dict(error="Resource " + append(e) + "{id} property not provided",
                                      message="Resource " + append(e) + "{id} property must be specified.",
                                      status=400),
        'ResourceAlreadyExists': dict(error="Resource already exists",
                                      message="Resource " + append(e) + "with that ID already exists.", status=400),
        'UndefinedParameter': dict(error="Undefined parameter value.",
                                   message="The parameter " + append(property) + "must have a value.", status=400),
        'MissingParameter': dict(error="Missing parameter",
                                       message="The parameter " + append(property) + "is missing from your request.", status=400),
        'InvalidParameter': dict(error="Invalid parameter",
                                       message="The parameter " + append(property) + "is invalid.", status=400),
        'Unknown': dict(error="An unknown error has occurred",
                        message="For unknown reasons, the transaction has failed.", status=500)
    }



    if err in errors:
        e = errors[err]
    else:
        e = errors['Unknown']

    return e