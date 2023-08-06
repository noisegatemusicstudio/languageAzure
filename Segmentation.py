import os
import pandas as pd
from openpyxl import load_workbook
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
        
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
        

# Provide the path to your Excel file
csv_file_path = "labelled_feedback.csv"

# Call the function to extract rows to text files
#extract_rows_to_text_files(csv_file_path)

def custom_text_classification():    
    # [START single_label_classify]
    try:
        endpoint = 'https://exoduslanguage.cognitiveservices.azure.com/'
        key = os.environ.get("AZURE_LANGUAGE_KEY")
        data = pd.read_excel('Segmentation.xlsx')
        document=data["Text"].tolist()
            
        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )
        
        poller = text_analytics_client.begin_single_label_classify(document, project_name='exodusSingle', deployment_name='exodus')

        document_results = poller.result()
        categories=[]        
        for doc, classification_result in zip(document, document_results):
            if classification_result.kind == "CustomDocumentClassification":
                classification = classification_result.classifications[0]
                print("The document text '{}' was classified as '{}' with confidence score {}.".format(
                    doc, classification.category, classification.confidence_score)
                )
                categories.append(classification.category)
            elif classification_result.is_error is True:
                print("Document text '{}' has an error with code '{}' and message '{}'".format(
                    doc, classification_result.error.code, classification_result.error.message
                ))
            # Print the classification result
            print(classification_result.classifications)
            print()  # Print an empty line for readability
        df=pd.read_excel("Segmentation.xlsx")
        df["Categories"]=categories
        with pd.ExcelWriter('Segmentation_Analyzed.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, index=False)  
    except Exception as e:
        print(f"An error occurred: {str(e)}")
            
custom_text_classification()