import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

print("GEMINI KEY FOUND:", bool(api_key))
print("MODEL:", model)
print()

url = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{model}:generateContent?key={api_key}"
)

payload = {
    "contents": [
        {
            "role": "user",
            "parts": [
                {
                    "text": "Reply with exactly: GEMINI_OK"
                }
            ]
        }
    ],
    "generationConfig": {
        "temperature": 1.0,
        "maxOutputTokens": 20
    }
}

print("Sending minimal Gemini request...")
print("URL:", url.split("?")[0])

try:
    response = requests.post(
        url,
        json=payload,
        timeout=(15, 120),
    )

    print()
    print("HTTP STATUS:", response.status_code)
    print("RESPONSE:")
    print(response.text[:5000])

except requests.exceptions.Timeout as e:
    print()
    print("TIMEOUT:", repr(e))

except requests.exceptions.RequestException as e:
    print()
    print("REQUEST ERROR:", repr(e))

except Exception as e:
    print()
    print("UNEXPECTED ERROR:", repr(e))