# import libraries
import os
import pandas as pd
import json
from openpyxl import load_workbook
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

def convert_labelled_data_to_utterance_file(file_path, language_code):
    try:
        # Read CSV file or Excel file and convert it to a Pandas DataFrame
        if file_path.endswith('.csv'):  # Check if the file has a CSV extension
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):  # Check if the file has an XLSX extension
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Only CSV and Excel (XLSX) files are supported.")

        # Convert each row to a JSON object
        data = []
        unique_utterances = set()  # Set to store unique utterances
        
        for index, row in df.iterrows():
            utterance = row['Customer Feedback']
            intent = row['Categories']
            
            # Skip if utterance is duplicated
            if utterance in unique_utterances:
                continue
            
            # Create a JSON object for each row
            json_obj = {
                "text": utterance,
                "language": language_code,
                "dataset": "Train",
                "intent": intent,
                "entities": []
            }
            
            # Add entities if needed
            # json_obj["entities"].append({
            #     "category": "{entity}",
            #     "offset": offset_value,
            #     "length": length_value
            # })
            
            data.append(json_obj)
            unique_utterances.add(utterance)  # Add utterance to set
            
        # Convert the data list to JSON
        json_data = json.dumps(data, indent=4)

        # Print or save the JSON data
        with open('utterance_file.json', 'w') as outfile:
            outfile.write(json_data)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
#convert_labelled_data_to_utterance_file("labelled_training_data.csv", "en-us")

def convert_labelled_data_to_json(file_path, language_code, project_name, text_data_column, class_column_name):
    try:
        # Read CSV file or Excel file and convert it to a Pandas DataFrame
        if file_path.endswith('.csv'):  # Check if the file has a CSV extension
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):  # Check if the file has an XLSX extension
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Only CSV and Excel (XLSX) files are supported.")

        # Create the JSON structure
        json_data = {
            "projectFileVersion": "2022-10-01-preview",
            "stringIndexType": "Utf16CodeUnit",
            "metadata": {
                "projectKind": "Conversation",
                "projectName": project_name,
                "multilingual": True,
                "description": "DESCRIPTION",
                "language": language_code,
                "settings": {
                    "confidenceThreshold": 0
                }
            },
            "assets": {
                "projectKind": "Conversation",
                "intents": [],
                "entities": [],
                "utterances": []
            }
        }

        # Add intents from the data
        intents = set(df[class_column_name])
        json_data['assets']['intents'] = [{'category': i} for i in intents]

        # Add entities, if needed
        # json_data['assets']['entities'] = [...]

        unique_utterances = set()  # Set to store unique utterances

        # Add utterances from the data
        for index, row in df.iterrows():
            utterance = row[text_data_column]
            intent = row[class_column_name]

            # Skip if utterance is duplicated
            if utterance in unique_utterances:
                continue

            utterance_obj = {
                "text": utterance,
                "intent": intent,
                "language": language_code,
                "dataset": "Train",
                "entities": []
            }

            # Add entities if needed
            # utterance_obj["entities"].append({
            #     "category": "{ENTITY1}",
            #     "offset": 6,
            #     "length": 4
            # })

            json_data['assets']['utterances'].append(utterance_obj)
            unique_utterances.add(utterance)  # Add utterance to set

        # Convert the JSON data to a string
        json_string = json.dumps(json_data, indent=4)

        # Save the JSON data to a file
        with open('language_understanding.json', 'w') as file:
            file.write(json_string)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
convert_labelled_data_to_json("labelled_training_data.csv", "en-us", "exodus_conversation_json","Customer Feedback", "Categories")

def conversational_language_understanding():
    try:
        # get secrets
        clu_endpoint = 'https://exoduslanguage.cognitiveservices.azure.com/'
        clu_key = os.environ.get("AZURE_LANGUAGE_KEY")
        project_name = "exodus_language_understanding"
        deployment_name = "exodus_conversational"

        # Read the Excel file
        df = pd.read_excel('Segmentation.xlsx')
        categories = []

        # analyze queries
        client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))
        with client:
            for index, row in df.iterrows():
                query = row['Text']
                result = client.analyze_conversation(
                    task={
                        "kind": "Conversation",
                        "analysisInput": {
                            "conversationItem": {
                                "participantId": "1",
                                "id": "1",
                                "modality": "text",
                                "language": "en",
                                "text": query
                            },
                            "isLoggingEnabled": False
                        },
                        "parameters": {
                            "projectName": project_name,
                            "deploymentName": deployment_name,
                            "verbose": True
                        }
                    }
                )

                # view result
                print("query: {}".format(result["result"]["query"]))
                print("project kind: {}\n".format(result["result"]["prediction"]["projectKind"]))

                print("top intent: {}".format(result["result"]["prediction"]["topIntent"]))
                print("category: {}".format(result["result"]["prediction"]["intents"][0]["category"]))
                print("confidence score: {}\n".format(result["result"]["prediction"]["intents"][0]["confidenceScore"]))
                
                categories.append(result["result"]["prediction"]["intents"][0]["category"])
            
            # Add the categories to the data
            df["Categories"] = categories    
            
            # Save the analyzed data to a new Excel file
            with pd.ExcelWriter('Segmentation_conversational_Analyzed.xlsx', engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

#conversational_language_understanding()