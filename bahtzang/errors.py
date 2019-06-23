class Error(Exception):
    pass

class InactiveCamper(Error):
    def __init__(self, camper_name):
        self.camper_name = camper_name

    def __str__(self):
        return '%s is not an active camper' % (self.camper_name)

class RegistrationAlreadyExists(Error):
    def __init__(self, camper_name, camp_year):
        self.camper_name = camper_name
        self.camp_year = camp_year

    def __str__(self):
        return '%s registration for %s already exists' % (self.camp_year, self.camper_name)
