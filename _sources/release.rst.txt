python-gardenlinux-lib release documentation
============================================

*python-gardenlinux-lib* strictly follow syntax and intention of `Semantic Versioning <https://www.semver.org>`. Each release reflects the intention and expected impact therefore.

A new release is done by tagging a commit with a valid version. This will create a GitHub pre-release for proof-reading. Once done a new release can be published using GitHub CLI or UI.

Newly added docstrings should contain the first version supporting the new API / command line.

Step by step guide
------------------

#. *python-gardenlinux-lib* version files:

   *python-gardenlinux-lib* versioning needs to be set in:

   - ``pyproject.toml``
   - ``.github/actions/setup/action.yml``

   Additionally at the moment (removal pending):

   - ``.github/actions/features_parse/action.yml``
   - ``.github/actions/flavors_parse/action.yml``

#. ``git tag <tag>``
#. Review the generated pre-release changelog by visiting the GitHub project release page and publish it if applicable.
#. Projects consuming the *python-gardenlinux-lib* may use the following git URL for dependency definition:
   ``gardenlinux @ git+https://github.com/gardenlinux/python-gardenlinux-lib.git@1.0.0``
