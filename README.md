## Pre-requisites
install Python 3.x

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/yourproject.git

cd yourproject

pip install -r requirements.txt

## For module import (to leverage config manager)
pip install -e .

## Update cntlm configuration
Go to cntlm.conf file and update NoProxy as below
NoProxy <existing_values>, *.openai.azure.com, *.cognitiveservices.azure.com

Run the application:
python myQRScanner.py

To make the executable run `pyinstaller --onefile myQRScanner.py`
```

# Azure Language Resource (including Sentiment, Segmentation)

## Pre-requisites
install Python 3.x

Deploy the Azure Language Resource

Update the environment variables of the Language Resource API key "AZURE_LANGUAGE_TOKEN" and API Endpoint in your local environment

Create the model (custom text classification / conversational language understanding)

Update the project name and deployment name
