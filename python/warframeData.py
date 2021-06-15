import requests

data = requests.get("https://wf.snekw.com/warframes-wiki").json()['data']['Warframes']


class Warframe:
    wf = ""

    def __init__(self, name):
        try:
            self.wf = data[name]
        except KeyError:
            self.wf = {}

    def isValid(self):
        if self.wf != {}:
            return True
        else:
            return False

    def getData(self):
        try:
            return self.wf
        except KeyError:
            return "error"

    def getHealth(self):
        try:
            return self.wf['Health']
        except KeyError:
            return "error"

    def getEnergy(self):
        try:
            return self.wf['Energy']
        except KeyError:
            return "error"

    def getArmor(self):
        try:
            return self.wf['Armor']
        except KeyError:
            return "error"

    def getShield(self):
        try:
            return self.wf['Shield']
        except KeyError:
            return "error"

    def getSprint(self):
        try:
            return self.wf['Sprint']
        except KeyError:
            return "error"

    def getAuraPol(self):
        try:
            return self.wf['AuraPolarity']
        except KeyError:
            return "error"

    def getPol(self):
        try:
            return self.wf['Polarities']
        except KeyError:
            return "error"

    def getThemes(self):
        try:
            return self.wf['Themes']
        except KeyError:
            return "error"

    def getElement(self):
        try:
            return self.wf['Subsumed']
        except KeyError:
            return "error"

    def isVaulted(self):
        try:
            return self.wf['Vaulted']
        except KeyError:
            return False