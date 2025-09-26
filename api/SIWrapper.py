import requests

class SIWrapper:
    def __init__(self, token: str, base_url: str = 'https://api.d-tools.com/SI/'):
        self.url = base_url if base_url.endswith('/') else f'{base_url}/'
        self.token = token
        self._headers = {
            "X-DTSI-ApiKey": self.token,
            "Content-Type": "application/json"
        }

    def create_project(self, data: dict) -> dict:
        response = requests.post(f'{self.url}Publish/Projects', json=data, headers=self._headers)
        return response.json()
    
    def get_project(self, project_id: int) -> dict:
        response = requests.get(f'{self.url}Subscribe/Projects?id={project_id}', headers=self._headers)
        return response.json()