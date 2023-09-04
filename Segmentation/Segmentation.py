import os
import pandas as pd
import json
from openpyxl import load_workbook
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient


def read_file_into_dataframe(file_path):
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Only CSV and Excel (XLSX) files are supported.")

def extract_rows_to_text_files(df):
    os.makedirs("documents", exist_ok=True)

    for index, row in df.iterrows():
        file_name = f"documents/row_{index}.txt"
        with open(file_name, "w") as file:
            for column, value in row.items():
                file.write(f"{column}: {value}\n")
        print(f"Created {file_name}")

def convert_labelled_data_to_json(df, language_code, container_name, project_name, class_column_name):
    json_data = {
        "projectFileVersion": "2022-05-01",
        "stringIndexType": "Utf16CodeUnit",
        "metadata": {
            "projectKind": "CustomSingleLabelClassification",
            "storageInputContainerName": container_name,
            "settings": {},
            "projectName": project_name,
            "multilingual": True,
            "description": "Project-description",
            "language": language_code
        },
        "assets": {
            "projectKind": "CustomSingleLabelClassification",
            "classes": [],
            "documents": []
        }
    }

    classes = set(df[class_column_name])
    json_data['assets']['classes'] = [{'category': c} for c in classes]

    for index, row in df.iterrows():
        document = {
            "location": f"row_{index}.txt",
            "language": language_code,
            "dataset": "Train",
            "class": {"category": row[class_column_name]}
        }
        json_data['assets']['documents'].append(document)

    with open('outputFiles/text_classification.json', 'w') as file:
        json.dump(json_data, file, indent=4)

def custom_text_classification(df, project_name, deployment_name):
    endpoint = 'https://exoduslanguage.cognitiveservices.azure.com/'
    key = os.environ.get("AZURE_LANGUAGE_KEY")

    if key is None or not isinstance(key, str):
        raise ValueError("Environment variable AZURE_LANGUAGE_KEY is not set or not a string.")

    document = df["Text"].tolist()
    text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    batch_size = 25
    num_batches = (len(document) - 1) // batch_size + 1
    categories = []

    for i in range(num_batches):
        start_index = i * batch_size
        end_index = min((i + 1) * batch_size, len(document))
        batch_document = document[start_index:end_index]

        poller = text_analytics_client.begin_single_label_classify(
            batch_document, project_name=project_name, deployment_name=deployment_name
        )

        batch_results = poller.result()

        for doc, classification_result in zip(batch_document, batch_results):
            if classification_result.kind == "CustomDocumentClassification":
                classification = classification_result.classifications[0]
                print(f"The document text '{doc}' was classified as '{classification.category}' with confidence score {classification.confidence_score}.")
                categories.append(classification.category)

        df["Categories"] = categories
        df.to_excel('outputFiles/Segmentation_classification_Analyzed.xlsx', index=False)

if __name__ == '__main__':
    try:
        file_path = "inputFiles/Segmentation.xlsx"
        df = read_file_into_dataframe(file_path)

        extract_rows_to_text_files(df)
        convert_labelled_data_to_json(df, "en-us", "exodus", "exodusSingle_json_label", "Categories")
        custom_text_classification(df, 'exodusSingle', 'exodus')

    except Exception as e:
        print(f"An error occurred: {str(e)}")
