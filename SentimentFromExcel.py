import pandas as pd
from openpyxl import load_workbook
import urllib.parse, http.client, urllib.request, urllib.error, json
import os

textAnalyticsEndpoint = 'exodus-language.cognitiveservices.azure.com'
sentimentEndpoint = '/text/analytics/v3.0/sentiment'
languageEndpoint = '/text/analytics/v3.0/languages'
keyPhrasesEndpoint = '/text/analytics/v3.0/keyPhrases'
textAnalyticsKey = os.getenv('AZURE_LANGUAGE_TOKEN')

headers = {
    'Content-Type' : 'application/json',
    'Ocp-Apim-Subscription-Key' : textAnalyticsKey,
    'Accept' : 'application/json'
}

params = urllib.parse.urlencode({})

def create_connection(textAnalyticsEndpoint):
    return http.client.HTTPSConnection(textAnalyticsEndpoint)

def send_request(conn, endPoint, params, body, headers):
    conn.request('POST', endPoint + params, str(body).encode('utf-8'), headers)
    return conn.getresponse()

def get_json_data(response):
    jsonData = response.read().decode('UTF-8')
    return json.loads(jsonData)

def get_sentiment(data):
    sentiment = data['documents'][0]['sentiment']
    # if mixed, get the highest score
    if sentiment == 'mixed':
        scores = data['documents'][0]['confidenceScores']
        max_score = max(scores, key=scores.get)
        sentiment = max_score
    return sentiment

def close_connection(conn):
    conn.close()

# Load the Excel file
df = pd.read_excel('Feedback.xlsx')

# Initialize an empty list to store the results
sentiments = []
key_phrases = []

# Iterate over the rows in the DataFrame
for index, row in df.iterrows():
    # Update the body with the current row's text
    body = {
        'documents': [
            {
                'id': str(index),
                'text': row['Text']  # replace 'your_column_name' with the name of your column
            }
        ]
    }

    try:
        conn = create_connection(textAnalyticsEndpoint)
        response = send_request(conn, sentimentEndpoint, params, body, headers)
        data = get_json_data(response)
        print(f"Sentiment response for document {index}: {data}")  # print the response
        sentiment = get_sentiment(data)
        print(f"Sentiment for document {index}: {sentiment}")  # print the sentiment
        sentiments.append(sentiment)
        close_connection(conn)
    except Exception as ex:
        print(ex)
        sentiments.append('error')  # append a default value in case of an exception

    try:
        conn = create_connection(textAnalyticsEndpoint)
        response = send_request(conn, keyPhrasesEndpoint, params, body, headers)
        data = get_json_data(response)
        print(f"Key phrases response for document {index}: {data}")  # print the response
        phrases = data['documents'][0]['keyPhrases']
        key_phrases.append(', '.join(phrases))
        close_connection(conn)
    except Exception as ex:
        print(ex)
        key_phrases.append('error')  # append a default value in case of an exception

# Add the results to the DataFrame
df['Sentiment'] = sentiments
df['Key Phrases'] = key_phrases

# Save the DataFrame to a new Excel file
with pd.ExcelWriter('Feedback_Analyzed.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, index=False)
