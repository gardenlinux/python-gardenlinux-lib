Garden Linux Python Library Documentation
==========================================

Welcome to the Garden Linux Python Library documentation. This library provides
Python tools and utilities for working with Garden Linux features, flavors,
OCI artifacts, S3 buckets, and GitHub releases.

.. image:: _static/gardenlinux-logo.svg
   :alt: Garden Linux Logo
   :class: logo
   :align: center

Overview
--------

The Garden Linux Python Library is a comprehensive toolkit for managing and
interacting with Garden Linux components. It includes:

* **Feature Management**: Parse and work with Garden Linux features and generate canonical names
* **Flavor Processing**: Parse flavors.yaml and generate combinations
* **OCI Operations**: Push OCI artifacts to registries and manage manifests
* **S3 Integration**: Upload and download artifacts from S3 buckets
* **GitHub Integration**: Create and manage GitHub releases with release notes

Quick Start
-----------

Command-Line Interface
~~~~~~~~~~~~~~~~~~~~~~

The library provides several command-line tools for common operations. See the
:doc:`Command-Line Interface documentation <cli>` for detailed information about
all available commands.

Release Management
~~~~~~~~~~~~~~~~~~

For information about versioning and release procedures, see the
:doc:`Release documentation <release>`.

API Reference
~~~~~~~~~~~~~

For detailed Python API documentation, including all modules, classes, and
functions, see the :doc:`API Reference <api>`.

Documentation Sections
----------------------

.. toctree::
   :maxdepth: 3
   :caption: Documentation:

   cli
   release
   api

Additional Resources
--------------------

* :ref:`genindex` - Complete index of all functions, classes, and modules
* :ref:`modindex` - Index of all modules
* :ref:`search` - Search the documentation
