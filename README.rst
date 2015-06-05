MediaAmp/MPX HTTP API Client
============================

This is a fairly low-level wrapper around the MediaAmp/MPX `endpoints
<http://help.theplatform.com/display/trc/Alphabetical+list+of+endpoints>`_
provided by theplatform.com. It primarily handles token authentication and
provides HTTP methods with configurable default parameters (e.g. schema) for the
service endpoints. Because of the multitude of available parameters available at
each endpoint this package is intended to be used by your application to build
your own abstractions on top of the request and response data. Currently it only
supports the JSON (and cJSON) forms.

.. image:: https://travis-ci.org/cordmata/mediaampy.svg?branch=master
    :target: https://travis-ci.org/cordmata/mediaampy

Usage
-----

To get started, supply your credentials: username, password, account id (This is
a URL and can be found on the "About" screen in the MPX console). You can
optionally supply an authentication token if you have one.

.. code-block:: python

    import mediaamp
    session = mediaamp.Session(
        'example@example.com',
        'very_very_secret',
        'http://access.auth.theplatform.com/data/Account/{{YOURID}}',
        auth_token='YOUR_TOKEN',
    )


Once initialized, you can obtain services by key lookup:

.. code-block:: python

    media_data = session['Media Data Service']

The endpoints on the service have get(), put(), post(), and delete()
methods you can use depending on the actions you are taking.

.. code-block:: python

    media_item = media_data.Media.get('{{MEDIA_ID}}')
    media_item['description']

You can specify your own defaults per-endpoint by calling the endpoint
object.

.. code-block:: python

    media = media_data.Media(schema='1.8', form='cjson')


Installation
------------

.. code-block:: bash

    pip install mediaampy

Or you can clone the source and run:

.. code-block:: bash

    make init
