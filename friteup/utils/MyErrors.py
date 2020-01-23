class RequiredAtLeastOne(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class GenericError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)