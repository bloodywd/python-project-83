from bs4 import BeautifulSoup


class Parser():
    def __init__(self, text):
        self.html = BeautifulSoup(text, 'html.parser')

    def parse_h1(self):
        h1_element = self.html.find('h1')
        return h1_element.text if h1_element else ''

    def parse_title(self):
        title_element = self.html.find('title')
        return title_element.text if title_element else ''

    def parse_description(self):
        description = ''
        meta_tag = self.html.find("meta", {'name': 'description'})
        if meta_tag:
            description = meta_tag.get("content", '')
        return description

    def get_args(self):
        return self.parse_h1(), self.parse_title(), self.parse_description()

