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
    >>> client.set_light(lightNumber, setting, bedId='')
    >>> pprint(client.get_light(lightNumber, bedId=''))
    >>> client.preset(preset, side, bedId='', slowSpeed=False)
    >>> client.set_foundation_position(bedNumber, actuator, position, side, bedId='', slowSpeed=False)
    >>> client.set_foundation_massage(bedNumber, footSpeed, headSpeed, side, timer=0, mode=0, bedId='')
    >>> client.set_sleepnumber(side, sleepnumber, bedId='')
    >>> client.set_favsleepnumber(side, sleepnumber, bedId='')
    >>> pprint(client.get_favsleepnumber(bedId=''))
    >>> client.stop_motion(bedId='', side)
    >>> client.stop_pump(bedId='')
    >>> pprint(client.foundation_status(bedId=''))
    >>> pprint(client.foundation_system(bedId=''))
    >>> pprint(client.foundation_features(bedId=''))

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
