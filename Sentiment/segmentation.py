import os
import pandas as pd
import json
from openpyxl import load_workbook
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient


# Load the Excel file
df = pd.read_excel('inputFiles/Feedback.xlsx')

def extract_rows_to_text_files(file_path):
    try:
        # Create a new folder called "documents"
        os.makedirs("documents", exist_ok=True)

        # Read the file
        if file_path.endswith('.csv'):  # Check if the file has a CSV extension
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):  # Check if the file has an XLSX extension
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Only CSV and Excel (XLSX) files are supported.")

        # Iterate over each row and create a text file for each row
        for index, row in df.iterrows():
            # Create a new text file
            file_name = f"documents/row_{index}.txt"
            with open(file_name, "w") as file:
                # Write the column names and row data to the text file
                for column, value in row.items():
                    file.write(f"{column}: {value}\n")
            print(f"Created {file_name}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Call the function to extract rows to text files
#extract_rows_to_text_files("inputFiles/labelled_training_data.csv")

def convert_labelled_data_to_json(file_path, language_code, cointainer_name, project_name, class_column_name):
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
            "projectFileVersion": "2022-05-01",
            "stringIndexType": "Utf16CodeUnit",
            "metadata": {
                "projectKind": "CustomMultiLabelClassification",
                "storageInputContainerName": cointainer_name,
                "settings": {},
                "projectName": project_name,
                "multilingual": True,
                "description": "Project-description",
                "language": language_code
            },
            "assets": {
                "projectKind": "CustomMultiLabelClassification",
                "classes": [],
                "documents": []
            }
        }

        # Add classes from the data
        classes = set(df[class_column_name])
        json_data['assets']['classes'] = [{'category': c} for c in classes]

        # Add documents from the data
        for index, row in df.iterrows():
            document = {
                "location": f"row_{index}.txt",
                "language": language_code,
                "dataset": "Train",
                "classes": [{"category": row[class_column_name]}]
            }
            json_data['assets']['documents'].append(document)

        # Convert the JSON data to a string
        json_string = json.dumps(json_data, indent=4)

        # Save the JSON data to a file
        with open('outputFiles/text_classification.json', 'w') as file:
            file.write(json_string)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
convert_labelled_data_to_json("inputFiles/labelled_training_data.csv", "en-us", "classificationcontainer", "langProject", "Categories")

categories = []

def custom_text_classification(file_path, project_name, deployment_name):

    try:
        # Azure Cognitive Services endpoint and key
        endpoint = 'https://langservicenew.cognitiveservices.azure.com/'
        key = os.environ.get("AZURE_LANGUAGE_KEY")

        # Read CSV file or Excel file and convert it to a Pandas DataFrame
        #if file_path.endswith('.csv'):  # Check if the file has a CSV extension
            #data = pd.read_csv(file_path)
        #elif file_path.endswith('.xlsx'):  # Check if the file has an XLSX extension
            #data = pd.read_excel(file_path)
        #else:
            #raise ValueError("Unsupported file format. Only CSV and Excel (XLSX) files are supported.")

        document = file_path
        
        # Initialize Text Analytics client
        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )

        batch_size = 10
        num_batches = (len(document) - 1) # batch_size + 1
        print(num_batches)

        for i in range(num_batches):
            start_index = i * batch_size
            end_index = min((i + 1) * batch_size, len(document))

            if end_index < start_index:
                break
    
            batch_document = document[start_index:end_index]

            #print(batch_document)

            print('avirag1')

            # Perform single-label classification on the batch
            poller = text_analytics_client.begin_multi_label_classify(
                batch_document, project_name=project_name, deployment_name=deployment_name
            )

            print('avirag2')

            # Get classification results for each document in the batch
            document_results = poller.result()

            print('avirag3')
            
            for doc, classification_result in zip(document, document_results):
                if classification_result.kind == "CustomDocumentClassification":
                    classifications = classification_result.classifications
                    category = []
                    print(f"\nThe review '{doc}' was classified as the following category:\n")
                    for classification in classifications:
                        print("'{}' with confidence score {}.".format(
                            classification.category, classification.confidence_score
                        ))
                        category.append(str(classification.category))
                    if(len(category) > 0):
                        categories.append(' '.join(category))
                    else:
                        categories.append('null')
                    
                elif classification_result.is_error is True:
                    print("The review '{}' has an error with code '{}' and message '{}'".format(
                        doc, classification_result.error.code, classification_result.error.message
                    ))
                    categories.append('null')
                
                # Print the classification result
                print(classification_result.classifications)
                print()  # Print an empty line for readability


        # Add the categories to the data
        #data["Categories"] = categories
        #df['Categories'] = categories

        # Save the DataFrame to a new Excel file
        #with pd.ExcelWriter('outputFiles/Feedback_Analyzed.xlsx', engine='openpyxl') as writer:
            #df.to_excel(writer, index=False)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        return categories
            
#custom_text_classification(df['Negative comment'], 'langProject', 'classDeployment')