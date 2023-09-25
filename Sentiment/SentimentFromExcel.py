import pandas as pd
from openpyxl import load_workbook
import urllib.parse, http.client, urllib.request, urllib.error, json
import os

from translate import *
from segmentation import *

textAnalyticsEndpoint = 'exoduscognitiveservices.cognitiveservices.azure.com'
sentimentEndpoint = '/text/analytics/v3.0/sentiment'
languageEndpoint = '/text/analytics/v3.0/languages'
keyPhrasesEndpoint = '/text/analytics/v3.0/keyPhrases'
textAnalyticsKey = 'e683ed8e943d4c45be7bf2e42f155ab2' #os.getenv('AZURE_LANGUAGE_TOKEN')

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
df = pd.read_excel('inputFiles/Feedback.xlsx')

# Initialize an empty list to store the results
sentimentsPos = []
sentimentsNeg = []
confidenceScoresPos = []
confidenceScoresNeg = []
translationPos = []
translationNeg = []
key_phrases_pos = []
key_phrases_neg = []
reviewCombined = []
translationPosSingle = ''
translationNegSingle = ''
categories = []

# Iterate over the rows in the DataFrame
for index, row in df.iterrows():
    # Update the body with the current row's text
    bodyPos = {
        'documents': [
            {
                'id': str(index),
                'text': row['Positive comment']  # replace 'your_column_name' with the name of your column
            }
        ]
    }

        # Update the body with the current row's text
    bodyNeg = {
        'documents': [
            {
                'id': str(index),
                'text': row['Negative comment']  # replace 'your_column_name' with the name of your column
            }
        ]
    }

    # Below block for positive review translation
    try:
        body = [{'text': bodyPos['documents'][0]['text']}]
        translationPosSingle = translate(body)
        translationPos.append(translationPosSingle)
    except Exception as ex:
        print(ex)
        translationPos.append('error')  # append a default value in case of an exception

    # Below block for negative review translation
    try:
        body = [{'text': bodyNeg['documents'][0]['text']}]
        translationNegSingle = translate(body)
        translationNeg.append(translationNegSingle)
    except Exception as ex:
        print(ex)
        translationNeg.append('error')  # append a default value in case of an exception
    
    reviewCombined.append('pos:'+translationPosSingle+'; neg:'+translationNegSingle)

df['Review combined'] = reviewCombined

# Iterate over the rows in the DataFrame
for index, row in df.iterrows():
    # Update the body with the current row's text
    bodyPos = {
        'documents': [
            {
                'id': str(index),
                'text': row['Review combined']  # replace 'your_column_name' with the name of your column
            }
        ]
    }

        # Update the body with the current row's text
    bodyNeg = {
        'documents': [
            {
                'id': str(index),
                'text': row['Review combined']  # replace 'your_column_name' with the name of your column
            }
        ]
    }

    # Below block for positive review sentiment
    try:
        conn = create_connection(textAnalyticsEndpoint)
        response = send_request(conn, sentimentEndpoint, params, bodyPos, headers)
        data = get_json_data(response)
        print(f"Sentiment response for document {index}: {data}")  # print the response
        sentiment = get_sentiment(data)
        print(f"Sentiment for document {index}: {sentiment}")  # print the sentiment
        sentimentsPos.append(sentiment)
        confidenceScoresPos.append(data['documents'][0]['confidenceScores'])
        close_connection(conn)
    except Exception as ex:
        print(ex)
        sentimentsPos.append('error')  # append a default value in case of an exception

    # Below block for negative review sentiment
    try:
        conn = create_connection(textAnalyticsEndpoint)
        response = send_request(conn, sentimentEndpoint, params, bodyNeg, headers)
        data = get_json_data(response)
        print(f"Sentiment response for document {index}: {data}")  # print the response
        sentiment = get_sentiment(data)
        print(f"Sentiment for document {index}: {sentiment}")  # print the sentiment
        sentimentsNeg.append(sentiment)
        confidenceScoresNeg.append(data['documents'][0]['confidenceScores'])
        close_connection(conn)
    except Exception as ex:
        print(ex)
        sentimentsNeg.append('error')  # append a default value in case of an exception

    # Below block for positive review key phrase
    try:
        conn = create_connection(textAnalyticsEndpoint)
        response = send_request(conn, keyPhrasesEndpoint, params, bodyPos, headers)
        data = get_json_data(response)
        print(f"Key phrases response for document {index}: {data}")  # print the response
        phrases = data['documents'][0]['keyPhrases']
        key_phrases_pos.append(', '.join(phrases))
        close_connection(conn)
    except Exception as ex:
        print(ex)
        key_phrases_pos.append('error')  # append a default value in case of an exception

    # Below block for negative review key phrase
    try:
        conn = create_connection(textAnalyticsEndpoint)
        response = send_request(conn, keyPhrasesEndpoint, params, bodyNeg, headers)
        data = get_json_data(response)
        print(f"Key phrases response for document {index}: {data}")  # print the response
        phrases = data['documents'][0]['keyPhrases']
        key_phrases_neg.append(', '.join(phrases))
        close_connection(conn)
    except Exception as ex:
        print(ex)
        key_phrases_neg.append('error')  # append a default value in case of an exception



# Add the results to the DataFrame

df['Positive comment Translation'] = translationPos
df['Negative comment Translation'] = translationNeg

df['Positive comment Sentiment'] = sentimentsPos
df['Positive comment Confidence'] = confidenceScoresPos

df['Negative comment Sentiment'] = sentimentsNeg
df['Negative comment Confidence'] = confidenceScoresNeg


df['Key Phrases Positive'] = key_phrases_pos
df['Key Phrases Negative'] = key_phrases_neg


df['Categories'] = custom_text_classification(reviewCombined, 'langProject', 'classDeployment')


# Save the DataFrame to a new Excel file
with pd.ExcelWriter('outputFiles/Feedback_Analyzed.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, index=False)
