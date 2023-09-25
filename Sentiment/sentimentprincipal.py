import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.identity import DefaultAzureCredential

endpoint = 'https://exoduscognitiveservices.cognitiveservices.azure.com/'
credential = DefaultAzureCredential()

documents = ["I hated the movie. It was so slow!", "The movie made it into my top ten favorites. What a great movie!"]

text_analytics_client = TextAnalyticsClient(endpoint= endpoint, credential=credential)

response = text_analytics_client.analyze_sentiment(documents)
successful_responses = [doc for doc in response if not doc.is_error]

print(successful_responses)