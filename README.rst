===============================
TourInFrance to GeoJSON
===============================

.. image:: https://badge.fury.io/py/tif2geojson.png
    :target: http://badge.fury.io/py/tif2geojson

.. image:: https://travis-ci.org/makinacorpus/tif2geojson.png?branch=master
        :target: https://travis-ci.org/makinacorpus/tif2geojson

.. image:: https://pypip.in/d/tif2geojson/badge.png
        :target: pypi.python.org/pypi/tif2geojson

Install
-------

::

    pip install tif2geojson


Features
--------

* Read XML TourInFrance V3 and converts to GeoJSON
* Take profit of `title`, `description`, `category`, `pictures`, `website`
  and `phone` attributes
* Select language for title and description
* Converts from command-line


Usage
-----

.. code-block:: python

    from tif2geojson import tif2geojson

    geojson = tif2geojson(xmlcontent)


If you have `geojsonio-cli <https://github.com/mapbox/geojsonio-cli>`__
installed, you can shoot TourInFrance URLs straight to `geojson.io
<http://geojson.io/>`__ for lightning-fast visualization and editing.

.. code-block:: console

    $ curl "http://sit.com/flux.xml" | tif2geojson.py | geojsonio


Authors
-------

* `Mathieu Leplatre <http://mathieu-leplatre.info>`_


|makinacom|_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com


License
-------

* Free software BSD - Copyright Makina Corpus
