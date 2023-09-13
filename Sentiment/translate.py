import os
import http.client
import urllib.parse
import json

textTranslationEndpoint = 'api.cognitive.microsofttranslator.com'
translationEndpoint = '/translate?'
translateKey = os.getenv('AZURE_TRANSLATE_TOKEN')

headers = {
    'Ocp-Apim-Subscription-Key': translateKey,
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Region': 'westeurope',
    'Content-type': 'application/json'
}

# Read the contents of sourceTrans.txt
with open('inputFiles/sourceTrans.txt', 'r', encoding='utf-8') as file:
    texts = file.readlines()

body = [{'text': texts[0]}]

params = urllib.parse.urlencode({
    'api-version': '3.0',
    'to': 'en'
})

def create_connection(textTranslationEndpoint):
    return http.client.HTTPSConnection(textTranslationEndpoint)

def send_request(conn, endPoint, params, body, headers):
    conn.request('POST', endPoint + params, json.dumps(body), headers)
    return conn.getresponse()

def get_json_data(response):
    response_data = response.read().decode('UTF-8')
    #print("Response:", response_data)  # Print the raw response
    return json.loads(response_data)

def print_translation(data):
    print('*' * 100)
    for document in data:
        print(f'Original: {document["text"]}')
        print(f'Translated: {document["translations"][0]["text"]}')
    print('*' * 100)
    
def close_connection(conn):
    conn.close()


def translate(body):
    try:
        conn = create_connection(textTranslationEndpoint)
        response = send_request(conn, translationEndpoint, params, body, headers)
        data = get_json_data(response)
        print_translation(data['documents'])
        close_connection(conn)
    except Exception as ex:
        print(ex)
    finally:
        return (data[0]['translations'][0]['text'])


