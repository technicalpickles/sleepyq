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

class Sleepyq:
    def __init__(self, login, password):
        self._login = login
        self._password = password
        self._session = requests.Session()
        self._api = "https://api.sleepiq.sleepnumber.com/rest"


    def makeRequest(self, url, mode="get", data=""):
        if mode == 'put':
            r = self._session.put(url, json=data)
        else:
            r = self._session.get(url)
        if r.status_code == 401:
            self.login()
            if mode == 'put':
                r = self._session.put(url, json=data)
            else:
                r = self._session.get(url)
        if r.status_code != 200:
            r.raise_for_status()

        return r

    def login(self):
        if '_k' in self._session.params:
            del self._session.params['_k']

        data = {'login': self._login, 'password': self._password}
        r = self._session.put(self._api+'/login', json=data)
        if r.status_code == 401:
            return False

        self._session.params['_k'] = r.json()['key']

        return True


    def sleepers(self):
        url = self._api+'/sleeper'
        r=self.makeRequest(url)

        sleepers = [Sleeper(sleeper) for sleeper in r.json()['sleepers']]
        return sleepers


    def beds(self):
        url = self._api+'/bed'
        r=self.makeRequest(url)

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
                if sleeper_id == "0":
                    continue
                sleeper = sleepers_by_id[sleeper_id]

                status = getattr(family_status, side)
                status.sleeper = sleeper

                setattr(bed, side, status)
        return beds


    def bed_family_status(self):
        url = self._api+'/bed/familyStatus'
        r=self.makeRequest(url)

        statuses = [FamilyStatus(status) for status in r.json()['beds']]
        return statuses


    def set_lights(self, bednum, light, setting):
        #
        # light 1-4
        # setting 0=off, 1=on
        #
        url = self._api+'/bed/'+self.beds()[bednum].data['bedId']+'/foundation/outlet'
        data = {'outletId': light, 'setting': setting}
        r=self.makeRequest(url, "put", data)

        return True


#    def get_lights(self, bednum, light):
#        url = self._api+'/bed/'+self.beds()[bednum].data['bedId']+'/foundation/outlet'
#        self._session.params['outletId'] = light
#        r=self.makeRequest(url)
#
#        del self._session.params['outletId']
#
#        #beds = [Bed(bed) for bed in r.json()['beds']]
#        return r.json()#beds


    def preset(self, bednum, preset, side, speed):
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
        url = self._api+'/bed/'+self.beds()[bednum].data['bedId']+'/foundation/preset'
        data = {'preset':preset,'side':side,'speed':speed}
        r=self.makeRequest(url, "put", data)

        return True


    def set_sleepnumber(self, bednum, side, setting):
        #
        # side "R" or "L"
        # setting 0-100 (increments of 5)
        #
        url = self._api+'/bed/'+self.beds()[bednum].data['bedId']+'/sleepNumber'
        data = {'bed': self.beds()[bednum].data['bedId'], 'side': side, "sleepNumber":setting}
        self._session.params['side']=side
        r=self.makeRequest(url, "put", data)

        del self._session.params['side']

        return True


    def set_favsleepnumber(self, bednum, side, setting):
        #
        # side "R" or "L"
        # setting 0-100 (increments of 5)
        #
        url = self._api+'/bed/'+self.beds()[bednum].data['bedId']+'/sleepNumberFavorite'
        data = {'side': side, "sleepNumberFavorite":setting}
        r=self.makeRequest(url, "put", data)

        return True


#    def get_favsleepnumber(self, bednum):
#        url = self._api+'/bed/'+self.beds()[bednum].data['bedId']+'/sleepNumberFavorite'
#        r=self.makeRequest(url)
#
#        #beds = [Bed(bed) for bed in r.json()['beds']]
#        return r.json()


#    def motion(self, bednum, side, foot, head, massage):
#        #
#        # side "R" or "L"
#        # 
#        #
#        url = self._api+'/bed/'+self.beds()[bednum].data['bedId']+'/foundation/motion'
#        data = {"footMotion":foot, "headMotion":head, "massageMotion":massage, "side":side}
#        r=self.makeRequest(url, "put", data)
#
#        return True

