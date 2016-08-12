import requests
import os

class Sleepyq:
    def __init__(self, login, password):
        self._login = login
        self._password = password

    def login(self):
        data = {'login': self._login, 'password': self._password}
        r = requests.put('https://api.sleepiq.sleepnumber.com/rest/login', json=data)

        self.key = r.json()['key']
        self.cookies = r.cookies

    def sleepers(self):
        url = 'https://api.sleepiq.sleepnumber.com/rest/sleeper?_k=' + self.key
        r = requests.get(url, cookies=self.cookies)
        return r.json()

if __name__ == "__main__":
    from pprint import pprint
    import dotenv
    from IPython import embed

    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    dotenv.load_dotenv(dotenv_path)

    client = Sleepyq(os.environ['SLEEPIQ_LOGIN'], os.environ['SLEEPIQ_PASSWORD'])

    client.login()
    sleepers = client.sleepers()
    pprint(sleepers)
