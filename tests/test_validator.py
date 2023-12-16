from page_analyzer.validate import Validator


def test_normalize():
    url = 'https://ru.hexlet.io/projects/83/members/35668/reviews'
    validation = Validator(url)
    validation.normalize()
    assert validation.get_url() == 'https://ru.hexlet.io'


def test_has_symbols():
    url = ''
    validation = Validator(url)
    validation.has_symbols()
    assert not validation.is_valid()
    assert validation.get_error() == 'URL обязателен'


def test_is_not_too_long():
    url = 'https://ru.hexlet.io//83/members/35668/reviews' + 'a' * 255
    validation = Validator(url)
    validation.is_not_too_long()
    assert not validation.is_valid()
    assert validation.get_error() == 'URL превышает 255 символов'


def test_is_correct():
    url = 'ru.hexlet.io//83/members/35668/reviews'
    validation = Validator(url)
    validation.is_correct()
    assert not validation.is_valid()
    assert validation.get_error() == 'Некорректный url'
