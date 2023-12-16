from page_analyzer.parser import get_args
import os
import pytest


PATH = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.mark.parametrize(
    "file,h1,title,description",
    [
        ('parser_test1.html', 'Header', 'Title', 'content description'),
        ('parser_test2.html', '', '', ''),
    ],
)
def test_get_args(file, h1, title, description):
    html = os.path.join(PATH, file)
    with open(html, 'r') as f:
        result_h1, result_title, result_description = get_args(f)
    assert result_h1 == h1
    assert result_title == title
    assert result_description == description
