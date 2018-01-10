from flask import Flask, request, Response
import json
import os
import requests
from jinja2 import Template
import logging

app = Flask(__name__)
logger = None
format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger('rest-transform')

# Log to stdout
stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(logging.Formatter(format_string))
logger.addHandler(stdout_handler)
logger.setLevel(logging.INFO)

prop = os.environ.get("PROPERTY", "response")
method = os.environ.get("METHOD", "get")
url_template = Template(os.environ["URL"])
headers = json.loads(os.environ.get("HEADERS", "{}"))
error_prop = os.environ.get("ERROR_PROPERTY", "error")
filter_prop = os.environ.get("FILTER_PROPERTY")


@app.route('/transform', methods=['POST'])
def receiver():

    def generate(entities):
        yield "["
        for index, entity in enumerate(entities):
            if index > 0:
                yield ","
            url = url_template.render(entity)
            if method == "get":
                response = requests.get(url, headers=headers)
            else:
                response = requests.request(method, url, data=entity.get("payload"), headers=headers)
            if response.status_code >= 200 and response.status_code < 300:
                entity[prop] = response.json()
            else:
                entity[error_prop] = {'status_code': response.status_code, 'reason': response.reason,
                                      'text': response.text}


            yield json.dumps(entity)
        yield "]"

    # get entities from request
    entities = request.get_json()

    logger.info("Received %s entities from Sesam", len(entities))
    if filter_prop:
        logger.info("Filter flag is set - filtering out entities")
        filtered = []
        for entity in entities:
            if not entity[filter_prop]:
                filtered.append(entity)
        # create the response
        logger.info("Amount of entities after filter %s", len(filtered))
        return Response(generate(filtered), mimetype='application/json')
    else:
        return Response(generate(entities), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

