import os

textAnalyticsEndpoint = 'exodus-language.cognitiveservices.azure.com'
sentimentEndpoint = '/text/analytics/v3.0/sentiment'
keyPhrasesEndpoint = '/text/analytics/v3.0/keyPhrases'
textAnalyticsKey = os.getenv('AZURE_LANGUAGE_TOKEN')

import urllib.parse, http.client, urllib.request, urllib.error, json
import pandas as pd
from openpyxl import load_workbook

headers = {
    'Content-Type' : 'application/json',
    'Ocp-Apim-Subscription-Key' : textAnalyticsKey,
    'Accept' : 'application/json'
}

body = {
    'documents' : [
      {
          'language' : 'en',
          'id' : '1',
          'text' : "I can't stop listening to this song. It's my new favorite!"
      },
      {
          'language' : 'zh-Hant',
          'id' : '2',
          'text' : '這門課程現在對我來說不適用。'
      }         
    ]
}

params = urllib.parse.urlencode({})

import http.client
import json

def create_connection(textAnalyticsEndpoint):
    return http.client.HTTPSConnection(textAnalyticsEndpoint)

def send_request(conn, endPoint, params, body, headers):
    conn.request('POST', endPoint + params, str(body).encode('utf-8'), headers)
    return conn.getresponse()

def get_json_data(response):
    jsonData = response.read().decode('UTF-8')
    return json.loads(jsonData)

def print_sentiment(data):
    print('*' * 100)
    for document in data['documents']:
        sentiment = document['sentiment']
        print(f'Document {document["id"]} has a {sentiment} sentiment.')
    print('*' * 100)

def print_key_phrases(data):
    print('*' * 100)
    for document in data['documents']:
        print(f'Document {document["id"]} key phrases:')
        for phrase in document['keyPhrases']:
            print(f'\t{phrase}')        
    print('*' * 100)
    
def close_connection(conn):
    conn.close()

try:
    conn = create_connection(textAnalyticsEndpoint)
    response = send_request(conn, sentimentEndpoint, params, body, headers)
    data = get_json_data(response)
    print(data)
    print_sentiment(data)
    close_connection(conn)
except Exception as ex:
    print(ex)

try:
    conn = create_connection(textAnalyticsEndpoint)
    response = send_request(conn, keyPhrasesEndpoint, params, body, headers)
    data = get_json_data(response)
    print(data)
    print_key_phrases(data)
    close_connection(conn)
except Exception as ex:
    print(ex)