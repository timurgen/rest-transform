from flask import Flask, request, Response
import json
import os
import requests
from urllib.parse import parse_qs
from jinja2 import Template
import logging

app = Flask(__name__)

prop = os.environ.get("PROPERTY", "response")
method = os.environ.get("METHOD", "get")
#required property
url_template = Template(os.environ["URL"])
headers = json.loads(os.environ.get("HEADERS", "{}"))
guid_str = os.environ.get("BOOKING_GUID_KEY", "creditcard-booking:guid")
iata_str = os.environ.get("IATA_KEY", "creditcard-booking:iata")
api_keys = parse_qs(os.environ.get("API_KEYS", ""))

# set logging
log_level = logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO'))  # default log level = INFO
logging.basicConfig(level=log_level)  # dump log to stdout


@app.route('/transform', methods=['POST'])
def receiver():
    def generate(entities):
        yield "["
        for index, entity in enumerate(entities):
            logging.debug("processing entity : %s" % entity) if logging.getLogger().isEnabledFor(
                logging.DEBUG) else logging.info("processing entity : %s" % entity.get(guid_str))
            if index > 0:
                yield ","
            booking_guid = entity.get(guid_str)
            iata = entity.get(iata_str)
            api_key = resolve_api_key(api_keys, iata)

            if not isinstance(api_key, str):
                entity[prop] = []
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
    logging.debug("Processing %i entities" % len(entities))
    return Response(generate(entities), mimetype='application/json')


def resolve_api_key(keys, iata_code):
    logging.debug("Trying to resolve API key for " + iata_code)
    api_key_arr = keys.get(iata_code.upper())
    if isinstance(api_key_arr, list) and len(api_key_arr):
        logging.debug("Found %i API key(s)" % len(api_key_arr))
    else:
        logging.warning("Didn't found API key for %s, current entity will not be processed" % iata_code)
        return api_key_arr
    return api_key_arr[0]


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
