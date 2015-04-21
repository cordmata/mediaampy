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

Once initialized, you can obtain services from the registry by key lookup or
attribute lookup. The following are equivalent:

.. code-block:: python

    media_data = services['Media Data Service']
    media_data = services.media_data_service
    media_data = services.Media_Data_Service
    media_data = services.MEDIA_DATA_SERVICE

The endpoints can be obtained from the services in the same manner from
the service object, except they are case sensitive .
Each endpoint has get(), put(), post(), and delete()
methods you can use depending on the actions you are taking.

.. code-block:: python

    all_media = media_data.Media.get()
    all_media = media_data['Media'].get()

You can specify your own defaults per-endpoint by calling the endpoint
object.

.. code-block:: python

    media = services.Media_Data_Service.Media(my_new_param='hello')


Installation
------------

We're currently taking this around the block so it isn't on pypi just yet.
You can install master (*cough* into a virtualenv) with:

.. code-block:: bash

    pip install https://github.com/cordmata/mediaampy/archive/master.zip

Or you can clone the source and run:

.. code-block:: bash

    make init

