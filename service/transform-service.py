from flask import Flask, request, Response
import json
import os
import requests
from urllib.parse import parse_qs
from jinja2 import Template

app = Flask(__name__)

prop = os.environ.get("PROPERTY", "response")
method = os.environ.get("METHOD", "get")
url_template = Template(os.environ["URL"])
headers = json.loads(os.environ.get("HEADERS", "{}"))
guid_str = os.environ.get("BOOKING_GUID_KEY", "creditcard-booking:guid")
iata_str = os.environ.get("IATA_KEY", "creditcard-booking:iata")
api_keys = parse_qs(os.environ.get("API_KEYS", ""))


@app.route('/transform', methods=['POST'])
def receiver():
    def generate(entities):
        yield "["
        for index, entity in enumerate(entities):
            if index > 0:
                yield ","
            booking_guid = entity.get(guid_str)
            iata = entity.get(iata_str)
            api_key = resolve_api_key(api_keys, iata)

            if not isinstance(api_key, str):
                entity[prop] = "API key for " + iata + " not found"
                yield json.dumps(entity)
                continue
            url = url_template.render(entity) + booking_guid + "?api_key=" + api_key
            if method == "get":
                entity[prop] = requests.get(url, headers=headers).json()
            else:
                entity[prop] = requests.request(method, url, data=entity.get("payload"),
                                                headers=headers).json()
            yield json.dumps(entity)
        yield "]"

    # get entities from request
    entities = request.get_json()

    # create the response
    return Response(generate(entities), mimetype='application/json')


def resolve_api_key(keys, iata_code):
    api_key_arr = keys.get(iata_code.upper())
    return api_key_arr[0]


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
