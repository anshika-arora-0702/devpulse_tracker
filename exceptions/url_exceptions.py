class UrlException(Exception):
    pass

class InvalidHttpsUrl(UrlException):

    def __init__(self, url:str):
        super().__init__(f"{url} is not a valid https url")
