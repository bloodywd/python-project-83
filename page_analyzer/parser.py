from bs4 import BeautifulSoup


class Parser():
    def __init__(self, text):
        self.html = BeautifulSoup(text, 'html.parser')

    def get_h1(self):
        h1_tag = self.html.find('h1')
        return h1_tag.text if h1_tag else None

    def get_title(self):
        title_tag = self.html.find('title')
        return title_tag.text if title_tag else None

    def get_description(self):
        description = None
        meta_tag = self.html.find("meta", {'name': 'description'})
        if meta_tag:
            description = meta_tag.get("content", '')
        return description
