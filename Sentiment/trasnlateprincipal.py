from azure.ai.translation.text.models import (
    InputTextItem
)
from azure.identity import DefaultAzureCredential
from azure.ai.translation.text import TextTranslationClient

endpoint = 'https://api.cognitive.microsofttranslator.com/'
credential = DefaultAzureCredential()

documents = "I hated the movie. It was so slow!"

text_translate_client = TextTranslationClient(endpoint= endpoint, credential=credential)

response = text_translate_client.translate(
                content=[InputTextItem(text = documents)],
                to=["fr"]
            )
        
translation = response[0] if response else None
successful_responses = [doc for doc in response if not doc.is_error]

print(successful_responses)