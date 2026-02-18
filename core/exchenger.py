from .models import *
import requests
import time
import datetime
import os 
import json

class Exchenger:
    def __init__(self) -> None:
        self.vaults = Vaults
        self.raw_json = {}
        self.vaults.refreshed_at = 0
        self.update()
        self.deserizalize()
    

    def _is_actual_data(self, data_ts:int) -> bool:
        dt = datetime.datetime.fromtimestamp(data_ts)
        dt = dt.replace(hour=18, minute=0, second=0, microsecond=0)
        targer_dt = dt.timestamp() + 60*60*24
        print(data_ts, dt.timestamp(), targer_dt, datetime.datetime.now().timestamp(), datetime.datetime.now().timestamp() < targer_dt)
        return datetime.datetime.now().timestamp() < targer_dt
    
    def _get_last_timestamp_in_dir(self, dirr = "cached") -> int:
        tmstamps = []
        for file in os.listdir("cached"):
            if file.startswith("curr_"):
                tstr = file[5:-5]
                if tstr.isnumeric():
                    tmstamps.append(int(tstr))
        return max(tmstamps) if len(tmstamps) != 0 else 0
    
    def _make_currency_filename(self, date_ts:int) -> str:
        return f"cached/curr_{date_ts}.json" if date_ts != 0 else f"cached/curr_{int(time.time())}.json"
    
    def _get_courses_from_web(self) -> dict:
        currency_timestamp = self._get_last_timestamp_in_dir()
        if not self._is_actual_data(currency_timestamp):
            # data isn't actual, getting fresh data
            currency_filename = self._make_currency_filename(0)
            resp = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
            self.vaults.refreshed_at = int(time.time())
            with open(currency_filename, "wb+") as f:
                f.write(resp.content)
            with open(currency_filename, "rb") as f:
                return json.load(f)
        else:
            # data is actual, loading from cache!
            currency_filename = self._make_currency_filename(currency_timestamp)
            self.vaults.refreshed_at = currency_timestamp
            with open(currency_filename, "rb") as f:
                return json.load(f)
        return {}
    
    def deserizalize(self):
        _vaults_names = ["RUB"]
        _vaults_array = {"RUB": Vault("Рубль", 1, 1, "RUB")}
        for vault in self.raw_json.get("Valute", {}):
            cur_val = Vault()
            current_val_json = self.raw_json.get("Valute", {}).get(vault, {}) 
            cur_val.nominal = current_val_json.get("Nominal", 0)
            cur_val.char_code = current_val_json.get("CharCode", "")
            cur_val.course = current_val_json.get("Value", 0)
            cur_val.name = vault
            _vaults_names.append(vault)
            _vaults_array.update({vault: cur_val})
        self.vaults.avaible_vaults = set(_vaults_names)
        self.vaults.vaults = _vaults_array
    
    def update(self):
        currency_timestamp = self._get_last_timestamp_in_dir()
        if not self._is_actual_data(currency_timestamp):
            self.raw_json = self._get_courses_from_web()
            self.deserizalize()
        
    def convert(self, 
                from_vault_name: str,
                from_vault_amount: float,
                to_vault_name:str):
        self.update()
        from_vault = self.vaults.vaults[from_vault_name]
        in_rubles = from_vault_amount * from_vault.course / from_vault.nominal
        if to_vault_name.upper() == "RUB": return in_rubles
        to_vault = self.vaults.vaults[to_vault_name]
        return in_rubles / to_vault.course / to_vault.nominal




