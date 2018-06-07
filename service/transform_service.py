"""This micro service can get data from altitude reservation system for multiple entities
based on their guid and provide support for multiple API keys"""
import logging
import json
import os
from urllib.parse import parse_qs

import requests
from jinja2 import Template
from flask import Flask, request, Response


APP = Flask(__name__)

PROP = os.environ.get("PROPERTY", "response")
METHOD = os.environ.get("METHOD", "get")
# required property
URL_TEMPLATE = Template(os.environ["URL"])
HEADERS = json.loads(os.environ.get("HEADERS", "{}"))
GUID_STR = os.environ.get("BOOKING_GUID_KEY", "creditcard-booking:guid")
IATA_STR = os.environ.get("IATA_KEY", "creditcard-booking:iata")
API_KEYS = parse_qs(os.environ.get("API_KEYS", ""))

# set logging
LOG_LEVEL = logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO'))  # default log level = INFO
logging.basicConfig(level=LOG_LEVEL)  # dump log to stdout


@APP.route('/transform', methods=['POST'])
def receiver():
    """Micro service end point"""
    def generate(entities_to_proceed):
        """Process list of entities populating them with altitude data"""
        yield "["
        for index, entity in enumerate(entities_to_proceed):
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug("processing entity : %s", entity)
            else:
                logging.info("processing entity : %s", entity.get(GUID_STR))

            if index > 0:
                yield ","
            booking_guid = entity.get(GUID_STR)
            iata = entity.get(IATA_STR)
            api_key = resolve_api_key(API_KEYS, iata)

            if not isinstance(api_key, str):
                entity[PROP] = []
                yield json.dumps(entity)
                continue
            url = URL_TEMPLATE.render(entity) + booking_guid + "?api_key=" + api_key
            if METHOD == "get":
                entity[PROP] = requests.get(url, headers=HEADERS).json()
            else:
                entity[PROP] = requests.request(METHOD, url, data=entity.get("payload"),
                                                headers=HEADERS).json()
            yield json.dumps(entity)
        yield "]"

    # get entities from request
    entities = request.get_json()

    # create the response
    logging.debug("Processing %i entities", len(entities))
    return Response(generate(entities), mimetype='application/json')


def resolve_api_key(keys, iata_code):
    """Function tries to find API key for given IATA airport code"""
    logging.debug("Trying to resolve API key for %s", iata_code)
    api_key_arr = keys.get(iata_code.upper())
    if isinstance(api_key_arr, list) and api_key_arr:
        logging.debug("Found %i API key(s)", len(api_key_arr))
    else:
        logging.warning("Didn't found API key for %s, entity will not be processed", iata_code)
        return api_key_arr
    return api_key_arr[0]


if __name__ == '__main__':
    APP.run(debug=True, host='0.0.0.0', port=5001)
