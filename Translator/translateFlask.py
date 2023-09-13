import os
import http.client
import urllib.parse
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

textTranslationEndpoint = 'api.cognitive.microsofttranslator.com'
translationEndpoint = '/translate?'
translateKey = os.getenv('AZURE_TRANSLATE_TOKEN')

headers = {
    'Ocp-Apim-Subscription-Key': translateKey,
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Region': 'westeurope'
}


@app.route('/translate', methods=['POST'])
def translate_text():
    try:
        input_data = request.json
        print(input_data)
        if "text" not in input_data:
            return jsonify({"error": "Missing 'text' in the request data"}), 400

        text_to_translate = input_data["text"]
        body = [{'text': text_to_translate}]
        print(text_to_translate)
        print(body)

        params = urllib.parse.urlencode({
            'api-version': '3.0',
            'to': 'fr'
        })

        conn = create_connection(textTranslationEndpoint)
        response = send_request(conn, translationEndpoint, params, body, headers)
        data = get_json_data(response)
        translations = data[0]['translations'][0]['text']
        close_connection(conn)

        return jsonify({"translations": translations})
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500


def create_connection(textTranslationEndpoint):
    return http.client.HTTPSConnection(textTranslationEndpoint)


def send_request(conn, endPoint, params, body, headers):
    conn.request('POST', endPoint + params, json.dumps(body), headers)
    return conn.getresponse()


def get_json_data(response):
    response_data = response.read().decode('UTF-8')
    return json.loads(response_data)


def close_connection(conn):
    conn.close()


if __name__ == '__main__':
    app.run(debug=True)
