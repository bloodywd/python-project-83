class FakeClient():
    fake_data = [
        ('value1', 'value2', 'value3', 'value4', 'value5', 'value6', 'value7')
    ]
    def connect(self):
        print('Connected')

    def disconnect(self):
        print('Disconnected')

    def select(self, query):
        print(query)
        if query == "SELECT * from urls WHERE name = 'unique'":
            return None
        return self.fake_data

    def insert(self, query):
        return query
