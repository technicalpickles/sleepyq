import requests
import inflection

from collections import namedtuple

RIGHT_NIGHT_STAND = 1
LEFT_NIGHT_STAND = 2
RIGHT_NIGHT_LIGHT = 3
LEFT_NIGHT_LIGHT = 4

BED_LIGHTS = [
        RIGHT_NIGHT_STAND,
        LEFT_NIGHT_STAND,
        RIGHT_NIGHT_LIGHT,
        LEFT_NIGHT_LIGHT
    ]

FAVORITE = 1
READ = 2
WATCH_TV = 3
FLAT = 4
ZERO_G = 5
SNORE = 6

BED_PRESETS = [
        FAVORITE,
        READ,
        WATCH_TV,
        FLAT,
        ZERO_G,
        SNORE
    ]

OFF = 0
LOW = 1
MEDIUM = 2
HIGH = 3

MASSAGE_SPEED = [
        OFF,
        LOW,
        MEDIUM,
        HIGH
    ]

SOOTHE = 1
REVITILIZE = 2
WAVE = 3

MASSAGE_MODE = [
        OFF,
        SOOTHE,
        REVITILIZE,
        WAVE
    ]

class APIobject(object):
    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        adjusted_name = inflection.camelize(name, False)
        return self.data[adjusted_name] if self.data is not None else None

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

class FavSleepNumber(APIobject):
    def __init__(self, data):
        super(FavSleepNumber, self).__init__(data)
        self.left = None
        self.right = None

class Status(APIobject):
    def __init__(self, data):
        super(Status, self).__init__(data)


class Sleepyq:
    def __init__(self, login, password):
        self._login = login
        self._password = password
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'})
        self._api = "https://prod-api.sleepiq.sleepnumber.com/rest"

    def __make_request(self, url, mode="get", data="", attempt=0):
        if attempt < 4:
            try:
                if mode == 'put':
                    r = self._session.put(self._api+url, json=data, timeout=2)
                else:
                    r = self._session.get(self._api+url, timeout=2)
                if r.status_code == 401: # HTTP error 401 Unauthorized
                    # Login
                    self.login()
                elif r.status_code == 404: # HTTP error 404 Not Found
                    # Login
                    self.login()
                elif r.status_code == 503:  # HTTP error 503 Server Error
                    r.raise_for_status()
                if r.status_code != 200: # If status code is not 200 OK
                    retry = self.__make_request(url, mode, data, attempt+1)
                    if type(retry) == requests.models.Response:
                        r = retry
                    r.raise_for_status()
                return r
            except requests.exceptions.ReadTimeout:
                retry = self.__make_request(url, mode, data, attempt+1)
                if type(retry) == requests.models.Response:
                    retry.raise_for_status()
                    return retry
                print('Request timed out to', url)

    def __feature_check(self, value, digit):
        return ((1 << digit) & value) > 0

    def login(self):
        if '_k' in self._session.params:
            del self._session.params['_k']
        if not self._login or not self._password:
            raise ValueError("username/password not set")
        data = {'login': self._login, 'password': self._password}
        r = self._session.put(self._api+'/login', json=data)
        if r.status_code == 401:
            raise ValueError("Incorect username or password")
        self._session.params['_k'] = r.json()['key']
        return True

    def sleepers(self):
        r=self.__make_request('/sleeper')
        sleepers = [Sleeper(sleeper) for sleeper in r.json()['sleepers']]
        return sleepers

    def beds(self):
        r=self.__make_request('/bed')
        beds = [Bed(bed) for bed in r.json()['beds']]
        return beds

    def beds_with_sleeper_status(self):
        beds = self.beds()
        sleepers = self.sleepers()
        family_statuses = self.bed_family_status()
        sleepers_by_id = {sleeper.sleeper_id: sleeper for sleeper in sleepers}
        bed_family_statuses_by_bed_id = {family_status.bed_id: family_status for family_status in family_statuses}
        for bed in beds:
            family_status = bed_family_statuses_by_bed_id.get(bed.bed_id)
            for side in ['left', 'right']:
                sleeper_key = 'sleeper_' + side + '_id'
                sleeper_id = getattr(bed, sleeper_key)
                if sleeper_id == "0": # if no sleeper
                    continue
                sleeper = sleepers_by_id.get(sleeper_id)
                status = getattr(family_status, side)
                status.sleeper = sleeper
                setattr(bed, side, status)
        return beds


    def bed_family_status(self):
        r=self.__make_request('/bed/familyStatus')
        statuses = [FamilyStatus(status) for status in r.json()['beds']]
        return statuses
        
    def default_bed_id(self, bedId):
        if not bedId:
            if len(self.beds()) == 1:
                bedId = self.beds()[0].data['bedId']
            else:
                raise ValueError("Bed ID must be specified if there is more than one bed")
        return bedId

    def set_light(self, light, setting, bedId = ''):
        #
        # light 1-4
        # setting False=off, True=on
        #
        if light in BED_LIGHTS:
            data = {'outletId': light, 'setting': 1 if setting else 0}
            r=self.__make_request('/bed/'+self.default_bed_id(bedId)+'/foundation/outlet', "put", data)
            return True
        else:
            raise ValueError("Invalid light")

    def get_light(self, light, bedId = ''):
        #
        # same light numbering as set_light
        #
        if light in BED_LIGHTS:
            self._session.params['outletId'] = light
            r=self.__make_request('/bed/'+self.default_bed_id(bedId)+'/foundation/outlet')
            del self._session.params['outletId']
            return Status(r.json())
        else:
            raise ValueError("Invalid light")

    def preset(self, preset, side, bedId = '', slowSpeed=False):
        #
        # preset 1-6
        # side "R" or "L"
        # slowSpeed False=fast, True=slow
        #
        if side.lower() in ('r', 'right'):
            side = "R"
        elif side.lower() in ('l', 'left'):
            side = "L"
        else:
            raise ValueError("Side mut be one of the following: left, right, L or R")
        if preset in BED_PRESETS:
            data = {'preset':preset,'side':side,'speed':1 if slowSpeed else 0}
            r=self.__make_request('/bed/'+self.default_bed_id(bedId)+'/foundation/preset', "put", data)
            return True
        else:
            raise ValueError("Invalid preset")

    def set_foundation_massage(self, footSpeed, headSpeed, side, timer=0, mode=0, bedId = ''):
        #
        # footSpeed 0-3
        # headSpeed 0-3
        # mode 0-3
        # side "R" or "L"
        #
        if mode in MASSAGE_MODE:
            if mode != 0:
                footSpeed = 0
                headSpeed = 0
            if all(speed in MASSAGE_SPEED for speed in [footSpeed, headSpeed]):
                data = {'footMassageMotor':footSpeed,'headMassageMotor':headSpeed,'massageTimer':timer,'massageWaveMode':mode,'side':side}
                r=self.__make_request('/bed/'+self.default_bed_id(bedId)+'/foundation/adjustment', "put", data)
                return True
            else:
                raise ValueError("Invalid head or foot speed")
        else:
            raise ValueError("Invalid mode")

    def set_sleepnumber(self, side, setting, bedId = ''):
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
        data = {'bed': self.default_bed_id(bedId), 'side': side, "sleepNumber": int(round(setting/5))*5}
        self._session.params['side']=side
        r=self.__make_request('/bed/'+self.default_bed_id(bedId)+'/sleepNumber', "put", data)
        del self._session.params['side']
        return True

    def set_favsleepnumber(self, side, setting, bedId = ''):
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
        r=self.__make_request('/bed/'+self.default_bed_id(bedId)+'/sleepNumberFavorite', "put", data)
        return True

    def get_favsleepnumber(self, bedId = ''):
        r=self.__make_request('/bed/'+self.default_bed_id(bedId)+'/sleepNumberFavorite')
        fav_sleepnumber = FavSleepNumber(r.json())
        for side in ['Left', 'Right']:
            side_key = 'sleepNumberFavorite'+ side
            fav_sleepnumber_side = fav_sleepnumber.data[side_key]
            setattr(fav_sleepnumber, side.lower(), fav_sleepnumber_side)
        return fav_sleepnumber

    def stop_motion(self, side, bedId = ''):
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
        r=self.__make_request('/bed/'+self.default_bed_id(bedId)+'/foundation/motion', "put", data)
        return True

    def stop_pump(self, bedId = ''):
        r=self.__make_request('/bed/'+self.default_bed_id(bedId)+'/pump/forceIdle', "put")
        return True

    def foundation_status(self, bedId = ''):
        r = self.__make_request('/bed/'+self.default_bed_id(bedId)+'/foundation/status')
        try:
            result = Status(r.json())
        except AttributeError:
            result = None
        return result

    def foundation_system(self, bedId = ''):
        r=self.__make_request('/bed/'+self.default_bed_id(bedId)+'/foundation/system')
        return Status(r.json())

    def foundation_features(self, bedId = ''):
        fs = self.foundation_system(self.default_bed_id(bedId))
        fs_board_features = getattr(fs, 'fsBoardFeatures')
        fs_bed_type = getattr(fs, 'fsBedType')

        feature = {}

        feature['single'] = feature['splitHead'] = feature['splitKing'] = feature['easternKing'] = False
        if fs_bed_type == 0:
            feature['single'] = True
        elif fs_bed_type == 1:
            feature['splitHead'] = True
        elif fs_bed_type == 2:
            feature['splitKing'] = True
        elif fs_bed_type == 3:
            feature['easternKing'] = True

        feature['boardIsASingle'] = self.__feature_check(fs_board_features, 0)
        feature['hasMassageAndLight'] = self.__feature_check(fs_board_features, 1)
        feature['hasFootControl'] = self.__feature_check(fs_board_features, 2)
        feature['hasFootWarming'] = self.__feature_check(fs_board_features, 3)
        feature['hasUnderbedLight'] = self.__feature_check(fs_board_features, 4)
        feature['leftUnderbedLightPMW'] = getattr(fs, 'fsLeftUnderbedLightPWM')
        feature['rightUnderbedLightPMW'] = getattr(fs, 'fsRightUnderbedLightPWM')

        if feature['hasMassageAndLight']:
            feature['hasUnderbedLight'] = True
        if feature['splitKing'] or feature['splitHead']:
            feature['boardIsASingle'] = False

        return Status(feature)
        
    def set_foundation_position(self, side, actuator, position, bedId = '', slowSpeed=False):
        #
        # side "R" or "L"
        # actuator "H" or "F" (head or foot)
        # position 0-100
        # slowSpeed False=fast, True=slow
        #
        if 0 > position or position > 100:
            raise ValueError("Invalid position, must be between 0 and 100")
        if side.lower() in ('r', 'right'):
            side = "R"
        elif side.lower() in ('l', 'left'):
            side = "L"
        else:
            raise ValueError("Side mut be one of the following: left, right, L or R")
        if actuator.lower() in ('h', 'head'):
            actuator = 'H'
        elif actuator.lower() in ('f', 'foot'):
            actuator = 'F'
        else:
            raise ValueError("Actuator must be one of the following: head, foot, H or F")
        data = {'position':position,'side':side,'actuator':actuator,'speed':1 if slowSpeed else 0}
        r=self.__make_request('/bed/'+self.default_bed_id(bedId)+'/foundation/adjustment/micro', "put", data)
        return True
