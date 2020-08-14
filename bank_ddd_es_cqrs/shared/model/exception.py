class AppException(Exception):
    def __init__(self, msg, status):
        super(AppException, self).__init__(msg)
        self.status = status
