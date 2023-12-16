from fake_client import FakeClient
from page_analyzer.database import select_url, select_urls, get_url_id, insert_to_db, select_checks


def test_select_url():
    id = 0
    result = select_url(id, FakeClient)
    assert result == {
        'id': 0,
        'name': 'value1',
        'created_at': 'value2'
    }


def test_select_urls():
    result = select_urls(FakeClient)
    assert result == [
        {
            'id': 'value1',
            'name': 'value2',
            'created_at': 'value3',
            'last_check': 'value4',
            'status_code': 'value5'
        }
    ]


def test_get_url_id():
    url = 'url'
    result = get_url_id(url, FakeClient)
    assert result == 'value1'


def test_insert_to_db():
    url1 = 'value1'
    url2 = 'unique'
    result1 = insert_to_db(url1, FakeClient)
    result2 = insert_to_db(url2, FakeClient)
    assert result1 == 'Страница уже существует'
    assert result2 == 'Успешно добавлено'


def test_select_checks():
    id = 0
    result = select_checks(id, FakeClient)
    assert result == [
        {
            'id': 'value1',
            'url_id': 'value2',
            'status_code': 'value3',
            'h1': 'value4',
            'title': 'value5',
            'description': 'value6',
            'created_at': 'value7',
        }
    ]
