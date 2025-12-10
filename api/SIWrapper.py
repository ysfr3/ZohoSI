# =============================================================================
# SIWrapper.py
# Author: Aidan Lelliott
# Organization: ASW
# Date: 10/08/2025
# Version: 1.0.0
#
# Description:
#   Python wrapper for D-Tools SI API. Provides methods for project creation,
#   retrieval, and listing via RESTful endpoints.
#
# License: Proprietary - For internal use only. Do not distribute.
# =============================================================================

import requests
import os
import json
from dotenv import load_dotenv

class SIWrapper:
    def __init__(self, base_url: str = 'https://api.d-tools.com/SI/'):
        self.url = base_url if base_url.endswith('/') else f'{base_url}/'
        load_dotenv()
        _token = os.getenv("SI_TOKEN")
        if _token is None:
            raise ValueError("SI TOKEN NOT SET")
        print(_token)
        self._headers = {
            "X-DTSI-ApiKey": _token,
            "Content-Type": "application/json"
        }

    def create_project(self, data: dict) -> dict:
        response = requests.post(f'{self.url}Publish/Projects', json=data, headers=self._headers)
        return response.json()
    
    def get_project(self, project_id: str, co_number: int = None) -> dict:
        project_co = self.get_project_current_co(project_id)
        fdurl = (f'{self.url}Subscribe/Projects?id={project_id}&coNumber={project_co}') if project_co is not None else (f'{self.url}Subscribe/Projects?id={project_id}')

        response = requests.get(fdurl, headers=self._headers)
        return response.json()
    
    def get_project_current_co(self, project_id: str) -> int:
        project_list = self.get_project_list()
        
        for i, project in enumerate(project_list):
            if project.get("Id") == project_id:
                project_object = project_list[i]
        
        return project_object.get("CONumber")
    
    def get_project_list(self) -> dict:
        response = requests.get(f'{self.url}Subscribe/Projects', headers=self._headers)
        return response.json().get("Projects")
