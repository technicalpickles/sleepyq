import requests

class Sleepyq:
    def __init__(self, login, password):
        self._login = login
        self._password = password
        self._session = requests.Session()

    def login(self):
        if '_k' in self._session.params:
            del self._session.params['_k']

        data = {'login': self._login, 'password': self._password}
        r = self._session.put('https://api.sleepiq.sleepnumber.com/rest/login', json=data)

        self._session.params['_k'] = r.json()['key']

    def sleepers(self):
        url = 'https://api.sleepiq.sleepnumber.com/rest/sleeper'
        r = self._session.get(url)
        return r.json()['sleepers']

    def beds(self):
        url = 'https://api.sleepiq.sleepnumber.com/rest/bed'
        r = self._session.get(url)
        return r.json()['beds']

    def bed_family_status(self):
        url = 'https://api.sleepiq.sleepnumber.com/rest/bed/familyStatus'
        r = self._session.get(url)
        return r.json()['beds']
