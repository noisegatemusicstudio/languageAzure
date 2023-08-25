import azure.cognitiveservices.speech as speechsdk
import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Set up Azure Speech API credentials
speech_key = os.getenv('AZURE_SPEECH_KEY')
service_region = "westeurope"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Creates a recognizer with the given settings
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

# Set up Azure Text Analytics API credentials
text_analytics_key = os.environ.get("AZURE_LANGUAGE_KEY")
text_analytics_endpoint = 'https://exoduslanguage.cognitiveservices.azure.com/'
text_analytics_client = TextAnalyticsClient(text_analytics_endpoint, AzureKeyCredential(text_analytics_key))

print("Say something...")

# List to store all recognized text
recognized_text_list = []

# Starts speech recognition, and returns after a single utterance is recognized.
# The end of a single utterance is determined by listening for silence at the end
# or until a maximum of 15 seconds of audio is processed. The task returns the recognition text as result.
# Note: Since recognize_once() returns only a single utterance, it is suitable only for single
# shot recognition like command or query.
# For long-running multi-utterance recognition, use start_continuous_recognition() instead.

# Flag to indicate if scanning should continue
continue_scanning = True

while continue_scanning:
    result = speech_recognizer.recognize_once()

    # Check result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        recognized_text = result.text.lower()
        print("Recognized: {}".format(recognized_text))

        # Check if the recognized text contains the stop phrase
        if "susan, stop recording" in recognized_text:
            continue_scanning = False
            print("Scanning stopped.")
        elif "susan, stopped recording" in recognized_text:
            continue_scanning = False
            print("Scanning stopped.")
        else:
            recognized_text_list.append(recognized_text)

    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))

    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))

        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

poller = text_analytics_client.begin_extract_summary(recognized_text_list)
extract_summary_results = poller.result()

summary_sentences = []

for result in extract_summary_results:
    if result.kind == "ExtractiveSummarization":
        summary_sentences.extend([sentence.text for sentence in result.sentences])
    elif result.is_error is True:
        print("...Is an error with code '{}' and message '{}'".format(
            result.error.code, result.error.message
        ))

# Format the summary sentences as bullet points
summary_bullet_points = "\n".join(["- " + sentence for sentence in summary_sentences])

# Print the summarized text as bullet points
print("Summary:")
print(summary_bullet_points)
