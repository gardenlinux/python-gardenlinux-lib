Python Library - Command-Line Interface
=======================================

Available command-line tools provided by the Garden Linux Python Library

Features Commands
-----------------

gl-features-parse
~~~~~~~~~~~~~~~~~

Parse and extract information from Garden Linux features.

.. autoprogram:: gardenlinux.features.__main__:get_parser()

gl-features-metadata
~~~~~~~~~~~~~~~~~~~~

Provides Garden Linux release metadata file handling.

.. autoprogram:: gardenlinux.features.metadata_main:get_parser()

Flavors Commands
----------------

gl-flavors-parse
~~~~~~~~~~~~~~~~

Parse flavors.yaml and generate combinations.

.. autoprogram:: gardenlinux.flavors.__main__:get_parser()

OCI Commands
------------

gl-oci
~~~~~~

Push OCI artifacts to a registry and manage manifests.

.. autoprogram:: gardenlinux.oci.__main__:get_parser()

S3 Commands
-----------

gl-s3
~~~~~

Upload and download artifacts from S3 buckets.

.. autoprogram:: gardenlinux.s3.__main__:get_parser()

GitHub Commands
---------------

gl-gh-release
~~~~~~~~~~~~~~

Create and manage GitHub releases.

.. autoprogram:: gardenlinux.github.release.__main__:get_parser()
