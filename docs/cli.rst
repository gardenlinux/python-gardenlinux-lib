Command-Line Interface
======================

This page documents all available command-line tools provided by python-gardenlinux-lib.

Features Commands
-----------------

gl-cname
~~~~~~~~

Generate a canonical name (cname) from feature sets.

.. autoprogram:: gardenlinux.features.cname_main:get_parser()

gl-features-parse
~~~~~~~~~~~~~~~~~

Parse and extract information from GardenLinux features.

.. autoprogram:: gardenlinux.features.__main__:get_parser()

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

.. click:: gardenlinux.oci.__main__:cli
   :prog: gl-oci
   :show-nested:

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
