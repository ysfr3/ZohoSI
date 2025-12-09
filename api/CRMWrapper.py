# =============================================================================
# CRMWrapper.py
# Author: Aidan Lelliott
# Organization: ASW
# Date: 10/08/2025
# Version: 1.0.0
#
# Description:
#   Python wrapper for Zoho CRM API. Provides methods for deal creation,
#   updating, note addition, and retrieval via RESTful endpoints.
#
# License: Proprietary - For internal use only. Do not distribute.
# =============================================================================

import os
import requests
from dotenv import load_dotenv

class CRMWrapper:
    def __init__(self, base_url: str = 'https://www.zohoapis.com/crm/v8/Deals/'):
        self.url = base_url if base_url.endswith('/') else f'{base_url}/'
        self._headers = {
            "Authorization": f"Zoho-oauthtoken ",
            "Content-Type": "application/json"
        }

    def push_new_deal_data(self, dealId: int, data: dict) -> dict:
        """
        Push new data to existing deal in Zoho CRM

        Args:
            dealId (int): dealId of deal to update
            data (dict): New data to push to deal

        Returns:
            dict: Response from Zoho CRM API
        """
        self._headers["Authorization"] = f"Zoho-oauthtoken {self._gen_crm_token()}"
        response = requests.patch(f'{self.url}{dealId}', json=data, headers=self._headers)
        return response.json()
    
    def add_note(self, dealId: int, note_content: str) -> dict:
        """
        Add note to existing deal in Zoho CRM

        Args:
            dealId (int): dealId of deal to update
            note_content (str): Content of note to add

        Returns:
            dict: Response from Zoho CRM API
        """
        self._headers["Authorization"] = f"Zoho-oauthtoken {self._gen_crm_token()}"
        response = requests.post(f'{self.url}{dealId}/Notes', json={
            "data": [
                {
                    "Parent_Id": {
                        "module": {
                            "api_name": "Deals"
                        },
                        "id": f"{dealId}"
                    },
                    "Note_Content": f"{note_content}"
                }
            ]
        }, headers=self._headers)

        res = response.json()
        print(res)

        return res
    
    def get_deal(self, dealId: int) -> dict:
        """
        Get deal from Zoho CRM

        Args:
            dealId (int): dealId of deal to get
        """
        self._headers["Authorization"] = f"Zoho-oauthtoken {self._gen_crm_token()}"
        response = requests.get(f'{self.url}{dealId}', headers=self._headers)
        return response.json()

    def _gen_crm_token(self) -> str:
        """
        Get new CRM token from Zoho

        Returns:
            str: access token
        """
        load_dotenv()
        print(os.getenv("CRM_ID"))
        print(os.getenv("CRM_SECRET"))
        base_url_access = f"https://accounts.zoho.com/oauth/v2/token?client_id={os.getenv("CRM_ID")}&client_secret={os.getenv("CRM_SECRET")}&grant_type=client_credentials&scope=ZohoCRM.modules.deals.ALL,ZohoCRM.modules.accounts.ALL,ZohoCRM.org.ALL,ZohoCRM.modules.notes.CREATE&soid=ZohoCRM.{os.getenv("CRM_SOID")}"
        response = requests.post(base_url_access)
        
        return response.json().get("access_token")
    
    def _test(self):
        """
        Test function to check if CRMWrapper is working
        """
        token = self._gen_crm_token()
        print(token)

if __name__=="__main__":
    CRM = CRMWrapper()
    CRM._test()
