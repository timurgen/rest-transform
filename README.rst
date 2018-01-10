====================
sesam-rest-transform
====================

Microservice that calls a REST service (with optional payload) and stores the result in a configurable property.

.. image:: https://travis-ci.org/sesam-community/rest-transform.svg?branch=master
    :target: https://travis-ci.org/sesam-community/rest-transform

::

  $ URL="https://foo.bar/api/{{ _id }}" python3 service/transform-service.py
   * Running on http://0.0.0.0:5001/ (Press CTRL+C to quit)
   * Restarting with stat
   * Debugger is active!
   * Debugger pin code: 260-787-156

The service listens on port 5001.

JSON entities can be posted to 'http://localhost:5001/transform'. The result is streamed back to the client.

Example config:
Last example contains the filter flag.
::

    [{
      "_id": "my-rest-transform-system",
      "type": "system:microservice",
      "docker": {
        "environment": {
          "HEADERS": {
            "Accept": "application/json; version=2",
            "Authorization": "token my-travis-token"
          },
          "URL": "https://api.travis-ci.org/settings/env_vars?repository_id={{ repo_id }}"
          "SKIP_FILTERED": "true"
        },
        "image": "sesamcommunity/sesam-rest-transform",
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
        "system": "my-rest-transform-system",
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
    
In this case the entities passed to the transform require a p


Examples:

::

   $ curl -s -XPOST 'http://localhost:5001/transform' -H "Content-type: application/json" -d '[{ "_id": "jane", "name": "Jane Doe" }]' | jq -S .
   [
     {
       "_id": "jane",
       "response": "foo-response",
       "name": "Jane Doe"
     }
   ]

::

   $ curl -s -XPOST 'http://localhost:5001/transform' -H "Content-type: application/json" -d @sample.json |jq -S .
   [
     {
       "_id": "jane",
       "response": "foo-response",
       "name": "Jane Doe"
     },
     {
       "_id": "john",
       "response": "foo-response",
       "name": "John Smith"
     }
   ]

::

   $ curl -s -XPOST 'http://localhost:5001/transform' -H "Content-type: application/json" -d '[{ "_id":  "jane", "filtered": false, "name": "Jane Doe" },{ "_id": "john", "filtered": true, "name": "John Smith" }]' | jq -S .
   [
     {
       "_id": "jane",
       "response": "foo-response",
       "name": "Jane Doe"
     }
   ]

Note the example uses `curl <https://curl.haxx.se/>`_ to send the request and `jq <https://stedolan.github.io/jq/>`_ prettify the response.
