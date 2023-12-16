from page_analyzer.parser import Parser
import os
import pytest


PATH = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.mark.parametrize(
    "file,h1,title,description",
    [
        ('parser_test1.html', 'Header', 'Title', 'content description'),
        ('parser_test2.html', None, None, None),
    ],
)
def test_get_args(file, h1, title, description):
    html = os.path.join(PATH, file)
    with (open(html, 'r') as f):
        parser = Parser(f)
    assert parser.get_h1() == h1
    assert parser.get_title() == title
    assert parser.get_description() == description
