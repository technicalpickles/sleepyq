import requests
import os
from IPython import embed

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
        return r.json()

    def beds(self):
        url = 'https://api.sleepiq.sleepnumber.com/rest/bed'
        r = self._session.get(url)
        return r.json()

    def bed_family_status(self):
        url = 'https://api.sleepiq.sleepnumber.com/rest/bed/familyStatus'
        r = self._session.get(url)
        #embed()
        return r.json()

if __name__ == "__main__":
    from pprint import pprint
    import dotenv

    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    dotenv.load_dotenv(dotenv_path)

    client = Sleepyq(os.environ['SLEEPIQ_LOGIN'], os.environ['SLEEPIQ_PASSWORD'])

    client.login()
    beds = client.beds()
    pprint(beds)
