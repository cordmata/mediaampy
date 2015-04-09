MediaAmp/MPX HTTP API Client
============================

This is a fairly low-level wrapper around the MediaAmp/MPX `endpoints
<http://help.theplatform.com/display/trc/Alphabetical+list+of+endpoints>`_
provided by theplatform.com. It primarily handles token authentication
and provides HTTP methods with configurable default parameters (e.g. schema)
for the service endpoints. Currently it only supports the JSON (and cJSON)
forms.

Usage
-----

.. code-block:: python

    import mediaamp
    mediaamp.username = 'example@example.com'
    mediaamp.password = 'very_very_secret'

    # if you have a non-expired authentication token you can supply it as well
    mediaamp.current_token = 'YOUR_TOKEN'

    services = mediamp.services.for_account('{{ ACCOUNT ID }}')
    media = services.Media['Media']
    stuff = media.get('byCategory', params={'categoryId': 'Something'})

You can specify your own defaults

Installation
------------

.. code-block:: bash

    pip install mediaampy

