from subprocess import call
import requests
import json
from datetime import timezone
import datetime

""" Handles API """


class RustelematicaAPI():
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://desk2.rustelematika.ru/api/asterix/masg.php"
    
    def make_request(self, cmd, panel_id: int, uuid_object=None, call_time_utc=None):
        result = requests.post(self.url,
                               data={"apikey": self.api_key, "cmd": cmd, "panelid": panel_id, "idobject": uuid_object,
                                     "calltime": call_time_utc})
        
        try:
                        
            return result.json()
        
        except Exception as e:
            return None
            
    def validate_user_data(self, panel_id, codechkts, codechstate):
        data = self.check_panel_id(panel_id)
        return self.check_codechkts(panel_id, codechkts, data) != None and self.check_codechstate(panel_id, codechstate, data) != None
        

    def get_data(self, cmd, panel_id: int, uuid_object=None, call_time_utc=None):
        result = self.make_request(cmd, panel_id, uuid_object, call_time_utc)
        if result:
            return result[0]
        
    
    def set_test_mode(self, panel_id: int, uuid_object, phone, mode:bool):
        result = requests.post(self.url,
                               data={"apikey": self.api_key, "cmd": 2, "mode": mode, "phone": phone, "panelid": panel_id, "idobject": uuid_object,})

        try:
                        
            return result.json()
        
        except Exception as e:
            return {}
    
    
    def check_test(self, cmd, panel_id: int, uuid_object, call_time_utc, expected_code):
        data = self.make_request(cmd, panel_id, uuid_object, int(call_time_utc.timestamp()))
        
        if data is None:
            return False
    
        for result in data:
            if result.get("messagecode") == expected_code:
                return True
        
        return False


    def set_api(self, api_key):
        self.api_key = api_key

    def check_panel_id(self, panel_id):
        if not str(panel_id).isnumeric():
            return None
        
        return self.get_data(1, int(str(panel_id)))

    def check_codechkts(self, panel_id: int, codechkts, data=None):
        
        if data is None:
            data = self.check_panel_id(panel_id)
        if data is None:
            return None

        if str(data.get("codechkts")) == codechkts:
            return data

        return None

    def check_codechstate(self, panel_id: int, codechstate, data=None):
        if data is None:
            data = self.check_panel_id(panel_id)
        if data is None:
            return None

        if str(data.get("codechstate")) == codechstate:
            return data

        return None
