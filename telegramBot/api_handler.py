import requests

""" Handles API """


class RustelematicaAPI():
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://desk2.rustelematika.ru/api/asterix/masg.php"

    def get_data(self, cmd, panel_id, uuid_object=None, call_time_utc=None):
        result = requests.post(self.url,
                               params={"apikey": self.api_key, "cmd": cmd, "panelid": panel_id, "idobject": uuid_object,
                                       "calltime": call_time_utc}).json()
        return result

    def set_api(self, api_key):
        self.api_key = api_key
