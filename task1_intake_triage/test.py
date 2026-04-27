from .utils import load_client_profiles
from .config import CLIENTS_FILE

try:
    client_profiles = load_client_profiles(CLIENTS_FILE)
    print(client_profiles)
except Exception as e:
    print(f"Error loading clients: {e}")
