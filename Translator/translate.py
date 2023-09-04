import requests
import json

def translate_text_to_english(text, subscription_key):
    endpoint = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=en"
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Content-type": "application/json",
        "Ocp-Apim-Subscription-Region": "westeurope"  # Use the region where you have created the Azure Translator service
    }
    body = [{"text": text}]
    response = requests.post(endpoint, headers=headers, json=body)
    result = response.json()
    
    if response.status_code != 200:
        raise Exception(f"Translation failed: {result}")
    
    return result[0]['translations'][0]['text']

# Usage example
try:
    translated_text = translate_text_to_english("Bonjour", "my_token")
    print(translated_text)  # Should output "Hello"
except Exception as e:
    print(e)
