import requests

payload = {
    "title": "Cool Team",
    "author": "BotUser",
    "notes": "Uploaded via API",
    "paste": "Pikachu @ Light Ball\nAbility: Static\n- Thunderbolt\n- Volt Tackle\n",
    "competitive_mode": True
}

r = requests.post("https://paste.tropimon.fr/api/create", json=payload)
print(r.json())
