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

This only really provides HTTP methods against known service endpoint URLs
with some common default parameters applied. Because of the multitude of
available parameters available at each endpoint this package is intended to
be used by your application to build your own abstractions on top of the
request and response data.

To get started, supply your credentials.

.. code-block:: python

    import mediaamp
    mediaamp.username = 'example@example.com'
    mediaamp.password = 'very_very_secret'

    # if you have a non-expired authentication token you can supply it as well
    mediaamp.current_token = 'YOUR_TOKEN'

To initialize the services, you will need to supply an account identifier
for an account available to your login-user. This is a URL and can be found
on the "About" screen in the MPX console.

.. code-block:: python

    services = mediamp.services.for_account('{{ ACCOUNT ID }}')

Once initialized, you can obtain endpoints from the services available on
the service object. Each endpoint has get(), put(), post(), and delete()
methods you can use depending on the actions you are taking.

.. code-block:: python

    media = services.MediaData['Media']
    stuff = media.get('byCategory', params={'categoryId': 'Something'})

You can specify your own defaults per-endpoint by calling the endpoint
object.

.. code-block:: python

    media = services.MediaData['Media'](my_new_param='hello')

If you prefer the read-only version of an endpoint (if available) you can
specify that when obtaining the service.

.. code-block:: python

    services.Feeds(read_only=True)['Feed']

Installation
------------

We're currently taking this around the block so it isn't on pypi just yet.
You can install master (*cough* into a virtualenv) with:

.. code-block:: bash

    pip install https://github.com/cordmata/mediaampy/archive/master.zip

Or you can clone the source and run:

.. code-block:: bash

    make init

