from .utils import load_client_profiles, build_prompt, call_groq
from .config import CLIENTS_FILE

try:
    client_profiles = load_client_profiles(CLIENTS_FILE)
    # print(client_profiles)
except Exception as e:
    print(f"Error loading clients: {e}")


for i, client in enumerate(client_profiles, 1):
    print(f"\n[{i}/{len(client_profiles)}] Processing: {client['name']}...")

    prompt = build_prompt(client)

    try:
        result = call_groq(prompt)
        print(result)
    except Exception as e:
        print(f"LLM call failed: {e}")
        continue
