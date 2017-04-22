from flask import Flask, request, Response
import json
import os
import requests
from jinja2 import Template

app = Flask(__name__)

prop = os.environ.get("PROPERTY", "response")
method = os.environ.get("METHOD", "get")
url_template = Template(os.environ["URL"])
headers = os.environ.get("HEADERS", {})


@app.route('/transform', methods=['POST'])
def receiver():

    def generate(entities):
        yield "["
        for index, entity in enumerate(entities):
            if index > 0:
                yield ","
            url = url_template.render(entity)
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

