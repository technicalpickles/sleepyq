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
    >>> pprint(bed_family_status())

The API is undocumented, so this library does not make much attempt to structure the data from the API into objects.

Development Notes
-----------------

The SleepIQ API was `announced at CES 2016 <https://www.engadget.com/2016/01/04/sleep-numbers-new-bed-will-train-you-to-sleep-better/>`__ but there has yet to be any public documentation.

https://sleepiq.sleepnumber.com appears to use the SleepIQ API internally, and methods here were written based on observing use of the site with Chrome Developer Tools. There was also prior art at https://github.com/erichelgeson/sleepiq (the API has changed since then) and https://github.com/natecj/sleepiq-php

The first request to happen is to login. This returns a key (_k) that needs to be used on subsequent requests as a parameter. Subsequent requests also need to be part of the same 'session', since those calls expect some cookies to be set.

Todo
-----

- This is my first python thing, so there are probably plenty of improvements
- Error check response for non-200 code, or errors returned as JSON
- Automatically login if necessary, either at first request or when the session expires (if that can be detected)
- Testing?
- Explore API more. There are a few more API calls out there, like updating profile, modifying sleep for previous night, but they seem less immediately useful for automation.
