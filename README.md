CrossPM
=======

[![build](https://travis-ci.org/devopshq/crosspm2.svg?branch=master)](https://travis-ci.org/devopshq/crosspm2)
[![pypi](https://img.shields.io/pypi/v/crosspm2.svg)](https://pypi.python.org/pypi/crosspm2)
[![license](https://img.shields.io/pypi/l/crosspm2.svg)](https://github.com/devopshq/crosspm2/blob/master/LICENSE)

Documentation
-------------
Actual version always here: https://devopshq.github.io/crosspm2/

Introduction
------------

CrossPM2 (Cross Package Manager 2) is a universal extensible package manager.
It lets you download and as a next step - manage packages of different types from different repositories.

Out-of-the-box modules:

- Adapters
  - Artifactory
  - [Artifactory-AQL](https://www.jfrog.com/confluence/display/RTF/Artifactory+Query+Language) (supported since artifactory 3.5.0):
  - files (simple repository on your local filesystem)

- Package file formats
  - zip
  - tar.gz
  - nupkg (treats like simple zip archive for now)

Modules planned to implement:

- Adapters
  - git
  - smb
  - sftp/ftp

- Package file formats
  - nupkg (nupkg dependencies support)
  - 7z

We also need your feedback to let us know which repositories and package formats do you need,
so we could plan its implementation.

The biggest feature of CrossPM is flexibility. It is fully customizable, i.e. repository structure, package formats,
packages version templates, etc.

To handle all the power it have, you need to write configuration file (**crosspm.yaml**)
and manifest file with the list of packages you need to download.

Configuration file format is YAML, as you could see from its filename, so you free to use yaml hints and tricks,
as long, as main configuration parameters remains on their levels :)
