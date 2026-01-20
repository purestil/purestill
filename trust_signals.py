import json

TRUST = {
    "editorial_policy": True,
    "source_transparency": True,
    "corrections_policy": True,
    "contact_page": True,
    "about_page": True,
    "consistent_authorship": True
}

with open("signals/trust_signals.json", "w") as f:
    json.dump(TRUST, f, indent=2)

print("🛡️ Trust signals locked")
