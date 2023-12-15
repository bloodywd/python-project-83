from urllib.parse import urlparse
from validators import url as validate


def normalize_url(url):
    normalized = urlparse(url)
    return f'{normalized.scheme}://{normalized.hostname}'


def validate_url(url):
    if not url:
        return url, 'URL обязателен'
    normalized = normalize_url(url)
    if not validate(normalized):
        return url, 'Некорректный url'
    if len(normalized) > 255:
        return normalized, 'URL превышает 255 символов'
    return normalized, None


def parse_h1(soup):
    try:
        h1 = soup.h1.text
    except (TypeError, AttributeError):
        h1 = ''
    return h1


def parse_title(soup):
    try:
        title = soup.title.text
    except (TypeError, AttributeError):
        title = ''
    return title


def parse_description(soup):
    try:
        description = soup.find("meta", {'name': 'description'})["content"]
    except (TypeError, AttributeError):
        description = ''
    return description
