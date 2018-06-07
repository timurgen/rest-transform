====================
sesam-rest-transform
====================

Microservice that calls a altitude reservation booking service finds parking data for given guuid's and stores the result in a configurable property.

.. image:: https://travis-ci.org/timurgen/rest-transform.svg?branch=master
    :target: https://travis-ci.org/timurgen/rest-transform

::

  $ URL="https://foo.bar/api/" python service/transform-service.py

The service listens on port 5001.

JSON entities can be posted to 'http://localhost:5001/transform'. The result is streamed back to the client.
Attribute API_KEYS must be encoded as HTTP query string.

Example config:

::

    [{
      "_id": "altitude-rest-transform-system",
      "type": "system:microservice",
      "docker": {
        "environment": {
          "API_KEYS": "$SECRET(altitude_api_keys_arr)",
          "BOOKING_GUID_KEY": "creditcard-booking:guid",
          "HEADERS": {
            "Accept": "application/json; version=2"
          },
          "IATA_KEY": "creditcard-booking:iata",
          "PROPERTY": "altitude",
          "URL": "$ENV(altitude-api-url)"
        },
        "image": "ohuenno/altitude-rest-transform",
        "port": 5001
      }
    },
    {
      "_id": "my-transform-pipe",
      "type": "pipe",
      "source": {
        "type": "dataset",
        "dataset": "my-source"
      },
      "transform": [{
        "type": "dtl",
        "rules": {
          "default": [
            ["copy", "*"],
            ["add", "::repo_id", "_S.id"]
          ]
        }
      }, {
        "type": "http",
        "system": "altitude-rest-transform-system",
        "url": "/transform"
      }, {
        "type": "dtl",
        "rules": {
          "default": [
            ["add", "details", "_S.response"],
            ["add", "_id", "_S.name"],
            ["add", "name", "_S.name"]
          ]
        }
      }]
    }]
    
