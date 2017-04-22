====================
sesam-rest-transform
====================

Microservice that calls a REST service (with optional payload) and stores the result in a configurable property.

::

  $ URL="https://foo.bar/api/{{ _id }}" python3 service/transform-service.py
   * Running on http://0.0.0.0:5001/ (Press CTRL+C to quit)
   * Restarting with stat
   * Debugger is active!
   * Debugger pin code: 260-787-156

The service listens on port 5001.

JSON entities can be posted to 'http://localhost:5001/transform'. The result is streamed back to the client.


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

Note the example uses `curl <https://curl.haxx.se/>`_ to send the request and `jq <https://stedolan.github.io/jq/>`_ prettify the response.
