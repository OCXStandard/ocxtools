# ``ocxtools``: Changelog

All notable changes to the ``ocxtools`` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to the Python [PEP 440 versioning recommendations](https://peps.python.org/pep-0440/).

### Types of changes
* ``Added`` for new features.
* ``Changed`` for changes in existing functionality.
* ``Deprecated`` for soon-to-be removed features.
* ``Removed`` for now removed features.
* ``Fixed`` for any bug fixes.
* ``Security`` in case of vulnerabilities.



## [1.4.0] - 2024.04.11

Bump to version [1.5.0]((https://github.com/OCXStandard/ocxtools/tree/v1.5.0))

### Changed
 - Updated tests to support schema release 3.0.0rc3
 - Update GitHub workflows to latest action versions


## [1.4.0] - 2024.03.11

Bump to version [1.4.0]((https://github.com/OCXStandard/ocxtools/tree/v1.4.0))

### Changed
 - Downgrade to Python 3.10
 - Add general docker run options to CLI command  ``docker run``

[Release tag](https://github.com/OCXStandard/ocxtools/tree/v1.3.0)

## [1.3.0] - 2024.01.12

### Changed
 - Add support for docker validator v3.0.0b6
 - Docker run will always pull :latest image as default
 - Add saving of detail validation report to csv file

[Release tag](https://github.com/OCXStandard/ocxtools/tree/v1.3.0)

## [1.2.1] - 2024.01.08

### Changed
* Fix missing printout of stdout when running a sub process.


## [1.2.0] - 2024.01.08

### Changed
* Add a docker UI validation command to the docker CLI.

[Release tag](https://github.com/OCXStandard/ocxtools/tree/v1.2.0)

## [1.1.0] - 2024.01.05

### 1st release

Provides a command line interface for managing the Windows Docker Desktop running the [OCX Validator](https://github.com/OCXStandard/ocx-validator) and validating 3Docx models.

[Release tag](https://github.com/OCXStandard/ocxtools/tree/v1.1.0)
