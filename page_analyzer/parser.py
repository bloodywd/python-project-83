from bs4 import BeautifulSoup


def get_args(text):
    html = BeautifulSoup(text, 'html.parser')

    h1_tag = html.find('h1')
    h1 = h1_tag.text if h1_tag else None

    title_tag = html.find('title')
    title = title_tag.text if title_tag else None

    description = None
    meta_tag = html.find("meta", {'name': 'description'})
    if meta_tag:
        description = meta_tag.get("content", '')

    return h1, title, description
