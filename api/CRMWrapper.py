import requests

class CRMWrapper:
    def __init__(self, token: str, base_url: str = 'https://www.zohoapis.com/crm/v8/Deals/'):
        self.url = base_url if base_url.endswith('/') else f'{base_url}/'
        self.token = token
        self._headers = {
            "Authorization": f"Zoho-oauthtoken {self.token}",
            "Content-Type": "application/json"
        }

    def push_new_deal_data(self, dealId: int, data: dict) -> dict:
        response = requests.post(f'{self.url}{dealId}', json=data, headers=self._headers)
        return response.json()