import requests
import inflection

from collections import namedtuple

class APIobject(object):
    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        adjusted_name = inflection.camelize(name, False)
        return self.data[adjusted_name]

class Bed(APIobject):
    def __init__(self, data):
        super(Bed, self).__init__(data)
        self.left = None
        self.right = None

class FamilyStatus(APIobject):
    def __init__(self, data):
        super(FamilyStatus, self).__init__(data)
        self.bed = None

        self.left = SideStatus(data['leftSide'])
        self.right = SideStatus(data['rightSide'])

class SideStatus(APIobject):
    def __init__(self, data):
        super(SideStatus, self).__init__(data)
        self.bed = None
        self.sleeper = None

class Sleeper(APIobject):
    def __init__(self, data):
        super(Sleeper, self).__init__(data)
        self.bed = None

class Light(APIobject):
    def __init__(self, data):
        super(Light, self).__init__(data)
        self.bed = None

class FavSleepNumber(APIobject):
    def __init__(self, data):
        super(FavSleepNumber, self).__init__(data)
        self.bed = None
        self.left = None
        self.right = None

class Sleepyq:
    def __init__(self, login, password):
        self._login = login
        self._password = password
        self._session = requests.Session()
        self._api = "https://api.sleepiq.sleepnumber.com/rest"

    def __makeRequest(self, url, mode="get", data=""):
        if mode == 'put':
            r = self._session.put(self._api+url, json=data)
        else:
            r = self._session.get(self._api+url)
        if r.status_code == 401: # HTTP error 401 Unauthorized
            # Login
            self.login()
            # Retry Request
            if mode == 'put':
                r = self._session.put(self._api+url, json=data)
            else:
                r = self._session.get(self._api+url)
        if r.status_code != 200: # If status code is not 200 OK
            # Raise error
            r.raise_for_status()
        return r

    def login(self):
        if '_k' in self._session.params:
            del self._session.params['_k']
        data = {'login': self._login, 'password': self._password}
        r = self._session.put(self._api+'/login', json=data)
        if r.status_code == 401:
            raise ValueError("Incorect username or password")
        self._session.params['_k'] = r.json()['key']
        return True

    def sleepers(self):
        r=self.__makeRequest('/sleeper')
        sleepers = [Sleeper(sleeper) for sleeper in r.json()['sleepers']]
        return sleepers

    def beds(self):
        r=self.__makeRequest('/bed')
        beds = [Bed(bed) for bed in r.json()['beds']]
        return beds

    def beds_with_sleeper_status(self):
        beds = self.beds()
        sleepers = self.sleepers()
        family_statuses = self.bed_family_status()
        sleepers_by_id = {sleeper.sleeper_id: sleeper for sleeper in sleepers}
        bed_family_statuses_by_bed_id = {family_status.bed_id: family_status for family_status in family_statuses}
        for bed in beds:
            family_status = bed_family_statuses_by_bed_id[bed.bed_id]
            for side in ['left', 'right']:
                sleeper_key = 'sleeper_' + side + '_id'
                sleeper_id = getattr(bed, sleeper_key)
                if sleeper_id == "0": # if no sleeper
                    continue
                sleeper = sleepers_by_id[sleeper_id]
                status = getattr(family_status, side)
                status.sleeper = sleeper
                setattr(bed, side, status)
        return beds


    def bed_family_status(self):
        r=self.__makeRequest('/bed/familyStatus')
        statuses = [FamilyStatus(status) for status in r.json()['beds']]
        return statuses

    def set_light(self, bedId, light, setting):
        #
        # light 1-4
        ### 1=Right Night Stand
        ### 2=Left Night Stand
        ### 3=Right Night Light
        ### 4=Left Night Light
        # setting False=off, True=on
        #
        if 1 <= light <= 4:
            data = {'outletId': light, 'setting': 1 if setting else 0}
            r=self.__makeRequest('/bed/'+bedId+'/foundation/outlet', "put", data)
            return True
        else:
            raise ValueError("Invalid light")

    def get_light(self, bedId, light):
        #
        # same light numbering as set_light
        #
        if 1 <= light <= 4:
            self._session.params['outletId'] = light
            r=self.__makeRequest('/bed/'+bedId+'/foundation/outlet')
            del self._session.params['outletId']
            light = Light(r.json())
            return light
        else:
            raise ValueError("Invalid light")

    def preset(self, bedId, preset, side, speed):
        #
        # preset 1-6
        ### 1=fav?
        ### 2=read
        ### 3=watch tv
        ### 4=flat
        ### 5=zero g
        ### 6=snore
        # side "R" or "L"
        # Speed 0=fast, 1=slow
        #
        if side.lower() in ('r', 'right'):
            side = "R"
        elif side.lower() in ('l', 'left'):
            side = "L"
        else:
            raise ValueError("Side mut be one of the following: left, right, L or R")
        if 1 <= preset <= 6:
            data = {'preset':preset,'side':side,'speed':1 if speed else 0}
            r=self.__makeRequest('/bed/'+bedId+'/foundation/preset', "put", data)
            return True
        else:
            raise ValueError("Invalid preset")

    def set_sleepnumber(self, bedId, side, setting):
        #
        # side "R" or "L"
        # setting 0-100 (rounds to nearest multiple of 5)
        #
        if 0 > setting or setting > 100 :
            raise ValueError("Invalid SleepNumber, must be between 0 and 100")
        if side.lower() in ('r', 'right'):
            side = "R"
        elif side.lower() in ('l', 'left'):
            side = "L"
        else:
            raise ValueError("Side mut be one of the following: left, right, L or R")
        data = {'bed': bedId, 'side': side, "sleepNumber": int(round(setting/5))*5}
        self._session.params['side']=side
        r=self.__makeRequest('/bed/'+bedId+'/sleepNumber', "put", data)
        del self._session.params['side']
        return True

    def set_favsleepnumber(self, bedId, side, setting):
        #
        # side "R" or "L"
        # setting 0-100 (rounds to nearest multiple of 5)
        #
        if 0 > setting or setting > 100:
            raise ValueError("Invalid SleepNumber, must be between 0 and 100")
        if side.lower() in ('r', 'right'):
            side = "R"
        elif side.lower() in ('l', 'left'):
            side = "L"
        else:
            raise ValueError("Side mut be one of the following: left, right, L or R")
        data = {'side': side, "sleepNumberFavorite": int(round(setting/5))*5}
        r=self.__makeRequest('/bed/'+bedId+'/sleepNumberFavorite', "put", data)
        return True

    def get_favsleepnumber(self, bedId):
        r=self.__makeRequest('/bed/'+bedId+'/sleepNumberFavorite')
        favsleepnumber = FavSleepNumber(r.json())
        return favsleepnumber

    def stopmotion(self, bedId, side):
        #
        # side "R" or "L"
        #
        if side.lower() in ('r', 'right'):
            side = "R"
        elif side.lower() in ('l', 'left'):
            side = "L"
        else:
            raise ValueError("Side mut be one of the following: left, right, L or R")
        data = {"footMotion":1, "headMotion":1, "massageMotion":1, "side":side}
        r=self.__makeRequest('/bed/'+bedId+'/foundation/motion', "put", data)
        return True

    def stoppump(self, bedId):
        r=self.__makeRequest('/bed/'+bedId+'/pump/forceIdle', "put")
        return True
