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
        base_url_access = f"https://accounts.zoho.com/oauth/v2/token?client_id={os.getenv("CRM_ID")}&client_secret={os.getenv("CRM_SECRET")}&grant_type=client_credentials&scope=ZohoCRM.modules.deals.ALL,ZohoCRM.modules.accounts.ALL,ZohoCRM.org.ALL&soid=ZohoCRM.{os.getenv("CRM_SOID")}"
        response = requests.post(base_url_access)
        
        return response.json().get("access_token")