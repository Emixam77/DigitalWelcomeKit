import os
import requests
from dotenv import load_dotenv

load_dotenv()

class BrevoManager:
    """
    Gestionnaire pour l'API Brevo (v3) afin de piloter la collecte de leads.
    """
    def __init__(self):
        self.api_key = os.getenv("BREVO_API_KEY")
        self.base_url = "https://api.brevo.com/v3"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self.api_key
        }

    def add_contact(self, email, list_ids=None):
        """
        Ajoute un contact à une ou plusieurs listes Brevo.
        """
        if list_ids is None:
            list_ids = [int(os.getenv("BREVO_LIST_ID", 12))]
        
        url = f"{self.base_url}/contacts"
        payload = {
            "email": email,
            "listIds": list_ids,
            "updateEnabled": True
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"❌ Erreur Brevo: {err.response.text}")
            return None
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return None

if __name__ == "__main__":
    # Test simple synchronisation
    manager = BrevoManager()
    result = manager.add_contact("test_antigravity@example.com")
    print(f"Résultat test: {result}")
