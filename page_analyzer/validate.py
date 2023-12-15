from urllib.parse import urlparse
from validators import url as validate


def normalize_url(url):
    normalized = urlparse(url)
    return f'{normalized.scheme}://{normalized.hostname}'


def validate_url(url):
    if not url:
        return 'URL обязателен'
    normalized = normalize_url(url)
    print(normalized)
    if not validate(normalized):
        return 'Некорректный url'
    if len(normalized) > 255:
        return 'URL превышает 255 символов'
