.. image:: https://ucf-open-slackin.herokuapp.com/badge.svg
    :alt: UCFOpen Slack Channel
    :target: https://ucf-open-slackin.herokuapp.com
.. image:: https://img.shields.io/pypi/v/vast.svg
    :alt: VAST PyPI version
    :target: https://pypi.python.org/pypi/vast
.. image:: https://img.shields.io/travis/ucfopen/vast.svg
    :alt: VAST build status on Travis CI
    :target: https://travis-ci.org/ucfopen/vast

Free software: GNU General Public License v3

VAST (Video Accessibility Scanning Tool)
========================================

VAST is a Python script that searches an Instructure Canvas course for media and returns results in a CSV file.

Requirements
------------

* Python 3
* YouTube API Key
* Vimeo API Key
* System permission to install python libraries

Installation
------------

First install Vast using pip::

    pip install vast

Check to make sure VAST is properly installed by running::

    vast --version
    vast --help

Next you must provide VAST with all the configuration variables. You can do this by setting environment variables, providing each key and value as a parameter, or by using the config command to create a config file:: 

    vast config

The config command will ask you to set the following.
    - **canvas_api_url** - Canvas URL and API e.g. `https://example.instructure.com`
    - **canvas_api_key** - Canvas API Key (To scan a course you're not enrolled in, you'll needs a sub-account or admin level key).
    - **youtube_api_key** - See instructions below.
    - **vimeo_access_token** - See instructions below.

YouTube API Key
^^^^^^^^^^^^^^^

In order for VAST to scan YouTube videos for closed captioning, you will need to create a YouTube Data API key.  Follow the instructions below:

1. Go to the `Google Developer Console <https://console.developers.google.com>`_.
2. Create a project.
3. Enable ***YouTube Data API V3***
4. Create an ***API key*** credential.

Vimeo API Key
^^^^^^^^^^^^^

In order for VAST to scan Vimeo videos for closed captioning, you will need to create a Vimeo access token. Follow the instructions below:

1. `Create a new App on Vimeo Developer API <https://developer.vimeo.com/apps/new?source=getting-started>`_, please note you must have a Vimeo Developer account.
2. On your application's "Authentication" page, Generate a new Access Token.  (Select the `Public` and `Private` checkboxes for Scopes.)

Types of Media
--------------

VAST will identify the following types of media:

- YouTube videos
- Vimeo videos
- Video files linked from the Rich Content Editor
- Audio files linked from the Rich Content Editor
- SWF files linked from the Rich Content Editor
- Media comments in the Rich Content Editor
- Embedded Canvas Video and Audio in the Rich Content Editor
- Links from video providers:
    - Films on Demand
    - Alexander Street Press
    - Kanopy
- Custom links can be added/removed to the `lib_media_urls` list in the `parser.py`

Limitations
-----------

- VAST does not check the Quizzes tool.
- VAST can not determine if captions exist on video files, audio files, flash files, or video providers. The report will list the location of the file to check manually and provide a download link. Make sure to be logged into Canvas first; unless the download link will not work.
- VAST may not be able to check all YouTube or Vimeo videos for captions. If it can't, the report will note so.

Testing
-------

A testing course is available in `Canvas Commons <https://lor.instructure.com/>`_. Use the search term `Vast Test Course`.

Usage
-----

1. Open up a terminal window
2. Type `vast -c analyze` ('-c' indicates you are reading the configuration file instead of manually entering them)
3. Enter the Canvas course id number e.g.(1234567 from `https://example.instructure.com/courses/1234567`)
4. The report will be saved in the same directory as the `vast.py` script

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
