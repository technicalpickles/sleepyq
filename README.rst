==========
Sleepyq
==========

Sleepyq is an library for accessing the SleepIQ API from Python. `SleepIQ <http://www.sleepnumber.com/sn/en/sleepiq-sleep-tracker>`__ is an addon for `SleepNumber beds <http://www.sleepnumber.com/>`__.

To install:

.. code:: bash

    python3 -m pip install sleepyq

To get started using the library, here's the full usage:

    >>> from sleepyq import Sleepyq
    >>> from pprint import pprint
    >>>
    >>> client = Sleepyq('your-login', 'your-password')
    >>> client.login()
    >>> pprint(client.sleepers())
    >>> pprint(client.beds())
    >>> pprint(client.bed_family_status())
    >>> client.set_lights(bedNumber, lightNumber, setting)
    >>> pprint(client.get_lights(bedNumber, lightNumber))
    >>> client.preset(bedNumber, preset, side, slowSpeed=False)
    >>> client.set_sleepnumber(bedNumber, side, sleepnumber)
    >>> client.set_favsleepnumber(bedNumber, side, sleepnumber)
    >>> pprint(client.get_favsleepnumber(bedNumber))
    >>> client.stop_motion(bedNumber, side)
    >>> client.stop_pump(bedNumber)
    >>> pprint(client.foundation_status(bedNumber))
    >>> pprint(client.foundation_system(bedNumber))
    >>> pprint(client.foundation_features(bedNumber))

The API is undocumented, so this library does not make much attempt to structure the data from the API into objects.

Development Notes
-----------------

The SleepIQ API was `announced at CES 2016 <https://www.engadget.com/2016/01/04/sleep-numbers-new-bed-will-train-you-to-sleep-better/>`__ but there has yet to be any public documentation.

https://sleepiq.sleepnumber.com appears to use the SleepIQ API internally, and methods here were written based on observing use of the site with Chrome Developer Tools and by running the Android app through a proxy. There was also prior art at https://github.com/erichelgeson/sleepiq (the API has changed since then) and https://github.com/natecj/sleepiq-php

The first request to happen is to login. This returns a key (_k) that needs to be used on subsequent requests as a parameter. Subsequent requests also need to be part of the same 'session', since those calls expect some cookies to be set.

Todo
-----

- Error check response for non-200 code, or errors returned as JSON
- Explore API more. There are a few more API calls out there, like updating profile, modifying sleep for previous night, but they seem less immediately useful for automation.
