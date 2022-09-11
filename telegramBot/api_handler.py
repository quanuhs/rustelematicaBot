import requests
import json

""" Handles API """


class RustelematicaAPI():
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://desk2.rustelematika.ru/api/asterix/masg.php"

    def get_data(self, cmd, panel_id: int, uuid_object=None, call_time_utc=None):
        result = requests.post(self.url,
                               data={"apikey": self.api_key, "cmd": cmd, "panelid": panel_id, "idobject": uuid_object,
                                     "calltime": call_time_utc})

        try:
            return result.json()[0]
        except json.decoder.JSONDecodeError:
            return None

    def set_api(self, api_key):
        self.api_key = api_key

    def check_panel_id(self, panel_id: int):
        return self.get_data(1, panel_id)

    def check_codechkts(self, panel_id: int, codechkts):
        data = self.check_panel_id(panel_id)
        if data is None:
            return None

        if str(data.get("codechkts")) == codechkts:
            return data

        return None

    def check_codechstate(self, panel_id: int, codechstate):
        data = self.check_panel_id(panel_id)
        if data is None:
            return None

        if str(data.get("codechstate")) == codechstate:
            return data

        return None
