from urllib.parse import urlparse
from validators import url as validate


class Validator():
    def __init__(self, url):
        self.url = url
        self.valid = True
        self.errors = []

    def normalize(self):
        normalized = urlparse(self.url)
        self.url = f'{normalized.scheme}://{normalized.hostname}'
        return self

    def has_symbols(self):
        if not self.url:
            self.valid = False
            self.errors.append('URL обязателен')
        return self

    def is_not_too_long(self):
        if len(self.url) > 255:
            self.valid = False
            self.errors.append('URL превышает 255 символов')
        return self

    def is_correct(self):
        if not validate(self.url):
            self.valid = False
            self.errors.append('Некорректный url')
        return self

    def is_valid(self):
        return self.valid

    def get_error(self):
        return self.errors[0]

    def get_url(self):
        return self.url
