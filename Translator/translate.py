# FIXME
import os
import http.client
import urllib.parse
import json

textAnalyticsEndpoint = 'api.cognitive.microsofttranslator.com'
translationEndpoint = '/translate?api-version=3.0'
textAnalyticsKey = os.getenv('AZURE_LANGUAGE_TOKEN')

headers = {
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': textAnalyticsKey,
    'Accept': 'application/json'
}

# Read the contents of sourceTrans.txt
with open('inputFiles/sourceTrans.txt', 'r', encoding='utf-8') as file:
    texts = file.readlines()

body = {
    'documents': [{'text': text.strip()} for text in texts]
}

params = urllib.parse.urlencode({
    'to': 'fr'  # Target language, e.g., bengali
})

def create_connection(textAnalyticsEndpoint):
    return http.client.HTTPSConnection(textAnalyticsEndpoint)

def send_request(conn, endPoint, params, body, headers):
    conn.request('POST', endPoint + params, json.dumps(body), headers)
    return conn.getresponse()

def get_json_data(response):
    response_data = response.read().decode('UTF-8')
    print("Response:", response_data)  # Print the raw response
    return json.loads(response_data)

def print_translation(data):
    print('*' * 100)
    for document in data:
        print(f'Original: {document["text"]}')
        print(f'Translated: {document["translations"][0]["text"]}')
    print('*' * 100)
    
def close_connection(conn):
    conn.close()

try:
    conn = create_connection(textAnalyticsEndpoint)
    response = send_request(conn, translationEndpoint, params, body, headers)
    data = get_json_data(response)
    print_translation(data['documents'])
    close_connection(conn)
except Exception as ex:
    print(ex)
