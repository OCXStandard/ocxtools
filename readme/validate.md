# validate CLI

## Introduction
The ``validate`` CLI provides the user with CLI commands to validate 3Docx models using the docker OCX validator service.

## Usage

From the command line prompt, type the help command to obtain the information of the available sub-commands:

````commandline
ocxtools >: help validate

 Usage:  [OPTIONS] COMMAND [ARGS]...

 Validation of 3Docx models.

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                    │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.             │
│ --help                        Show this message and exit.                                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ details      List validation detail results.                                                                               │
│ info         Verify that the Docker validator is alive and obtain the available validation options.                        │
│ many         Validate many 3Docx XML files with the docker validator.                                                      │
│ one          Validate one 3Docx XML file with the docker validator.                                                        │
│ readme       Show the validate html page with usage examples.                                                              │
│ summary      List validation summary results.                                                                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

ocxtools >:
````

### ``info``

The ``info`` sub-command will print the current validator resources:

````commandline
ocxtools >: validate info
=============================================== Validator Information ===============================================

                                       Validator server: http://localhost:8080
                       ┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                       ┃ Domain     ┃ Validation type     ┃ Description                      ┃
                       ┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
                       │ ocx        │ ocx.v2.8.6          │ OCX XSD validation - v2.8.6      │
                       │ ocx        │ ocx.v3.0.0b3        │ OCX XSD validation - v3.0.0b3    │
                       │ ocx        │ ocx.v3.0.0b4        │ OCX XSD validation - v3.0.0b4    │
                       │ ocx        │ ocx.v3.0.0b5        │ OCX XSD validation - v3.0.0b5    │
                       │ schematron │ schematron.v2.8.6   │ Schematron validation - v2.8.6   │
                       │ schematron │ schematron.v3.0.0b3 │ Schematron validation - v3.0.0b3 │
                       │ schematron │ schematron.v3.0.0b4 │ Schematron validation - v3.0.0b4 │
                       │ schematron │ schematron.v30.0b5  │ Schematron validation - v30.0b5  │
                       └────────────┴─────────────────────┴──────────────────────────────────┘
                                The validation domains and supported schema versions


ocxtools >:
````

The table displays the available validation domains and the supported schema versions.

### ``validate one``

The ``validate one`` sub-command will accept on 3dDocx file as input with optional options:
````commandline
ocxtools >: validate one --help

 Usage: one [OPTIONS] MODEL

 Validate one 3Docx XML file with the docker validator.

╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    model      TEXT  [default: None] [required]                                                                                           │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --domain                          [ocx|schematron]     The validator domain. [default: ocx]                                                │
│ --schema-version                  TEXT                 Input schema version. [default: 3.0.0]                                              │
│ --embedding                       [STRING|URL|BASE64]  The embedding method. [default: BASE64]                                             │
│ --force             --no-force                         Validate against the input schema version. [default: no-force]                      │
│ --save              --no-save                          Save the validation xml to the report folder. [default: no-save]                    │
│ --help                                                 Show this message and exit.                                                         │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
````
 - The ``domain`` option allows the specification of the validation domain supported by the validator, see the ``validate info``.
 - The ``schema-version`` allows for specifying a specific schema version. If combined with the ``force``flag, the validator will use the specified schema version for the validation. If the ``force`` flag is not given, the schema version will be based on the schema version in the 3Docx header in the XML file.
 - The ``embedding`` option specifies how the 3Docx file is embedded in the call to the validator. Use the dfault value.
 - The ``save`` option will save tha validation XML report in a ``report`` subdirectory. You don't want to look at it.
#### Example
Validate the ``m1.3docx`` using default options:
````commandline
ocxtools >: validate one models/m1.3docx
================================================================ Validate One ================================================================
ℹ     Created validation report for model 'models/m1.3docx'
❌     FAILURE


                                                              Validation results
┏━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃               ┃         ┃ Number of     ┃ Number of      ┃ Number of     ┃                ┃ Validator     ┃ Validation     ┃               ┃
┃ Source        ┃ Result  ┃ errors        ┃ warnings       ┃ assertions    ┃ Validator name ┃ version       ┃ type           ┃ Date          ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ models/m1.3d… │ FAILURE │ 5             │ 0              │ 0             │ ocx-validator  │ 3.0.0b5       │ ocx.v3.0.0b4   │ 2024-01-04    │
│               │         │               │                │               │                │               │                │ 20:25:13+00:… │
└───────────────┴─────────┴───────────────┴────────────────┴───────────────┴────────────────┴───────────────┴────────────────┴───────────────┘
````
The above command validates the model ``m1.3docx`` in the folder ``models`` and prints the summary table.

### ``validate many``
The ``validate many`` command will validate several models in one step. The command accepts a directory as input and gives the possibility to select models in the directory:
````commandline
validate many --help

 Usage: many [OPTIONS] DIRECTORY

 Validate many 3Docx XML files with the docker validator.

╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    directory      TEXT  [default: None] [required]                                                                                       │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --filter                                TEXT                 Filter models to validate. [default: *.3docx]                                 │
│ --domain                                [ocx|schematron]     The validator domain. [default: ocx]                                          │
│ --schema-version                        TEXT                 Input schema version. [default: 3.0.0]                                        │
│ --embedding                             [STRING|URL|BASE64]  The embedding method. [default: BASE64]                                       │
│ --force             --no-force                               Validate against the input schema version. [default: no-force]                │
│ --interactive       --no-interactive                         Interactive mode [default: interactive]                                       │
│ --help                                                       Show this message and exit.                                                   │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
````
The options are the same as for the ``validate one`` command except for the ``filter`` option which gives the possibility to filter the files to be validated.

#### Example
````commandline
ocxtools >: validate many models
Select models (give a list of indexes, separated by spaces): [(0, 'BT118-CH3.3docx'), (1, 'M1.3docx'), (2, 'M2.3docx'), (3, 'M3.3docx'), (4, 'M4.3docx'), (5, 'M4_NURBS.3docx'), (6, 'M5.3docx'), (7, 'M6.3docx'), (8, 'M7.3docx'), (9, 'M8.3docx'), (10, 'M9.3docx')]?: 1 2 3
Selected files: ['C:\\DNV\\ocxtools\\models\\M1.3docx', 'C:\\DNV\\ocxtools\\models\\M2.3docx', 'C:\\DNV\\ocxtools\\models\\M3.3docx'] [y/N]:y

=============================================================== Validate Many ================================================================
ℹ     Selected files: ['C:\\DNV\\ocxtools\\models\\M1.3docx', 'C:\\DNV\\ocxtools\\models\\M2.3docx', 'C:\\DNV\\ocxtools\\models\\M3.3docx']
ℹ     Created validation report for model 'C:\\DNV\\ocxtools\\models\\M1.3docx'
ℹ     Created validation report for model 'C:\\DNV\\ocxtools\\models\\M2.3docx'
ℹ     Created validation report for model 'C:\\DNV\\ocxtools\\models\\M3.3docx'


                                                              Validation results
┏━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃               ┃         ┃ Number of     ┃ Number of      ┃ Number of     ┃                ┃ Validator     ┃ Validation     ┃               ┃
┃ Source        ┃ Result  ┃ errors        ┃ warnings       ┃ assertions    ┃ Validator name ┃ version       ┃ type           ┃ Date          ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ C:\DNV\ocxto… │ FAILURE │ 5             │ 0              │ 0             │ ocx-validator  │ 3.0.0b5       │ ocx.v3.0.0b4   │ 2024-01-04    │
│               │         │               │                │               │                │               │                │ 20:49:30+00:… │
│ C:\DNV\ocxto… │ FAILURE │ 4             │ 0              │ 0             │ ocx-validator  │ 3.0.0b5       │ ocx.v3.0.0b4   │ 2024-01-04    │
│               │         │               │                │               │                │               │                │ 20:49:31+00:… │
│ C:\DNV\ocxto… │ FAILURE │ 14            │ 0              │ 0             │ ocx-validator  │ 3.0.0b5       │ ocx.v3.0.0b4   │ 2024-01-04    │
│               │         │               │                │               │                │               │                │ 20:49:36+00:… │
└───────────────┴─────────┴───────────────┴────────────────┴───────────────┴────────────────┴───────────────┴────────────────┴───────────────┘

ocxtools >:
````
The above command validates the 3 selected models in the folder ``models`` and prints the summary table.

### validate summary
The ``validate summary`` command will print the summary validation results for all models that has been validated during this session.

#### Example

````commandline
ocxtools >: validate summary
============================================================= Validation Summary =============================================================


                                                              Validation results
┏━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃               ┃         ┃ Number of     ┃ Number of      ┃ Number of     ┃                ┃ Validator     ┃ Validation     ┃               ┃
┃ Source        ┃ Result  ┃ errors        ┃ warnings       ┃ assertions    ┃ Validator name ┃ version       ┃ type           ┃ Date          ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ models/m1.3d… │ FAILURE │ 5             │ 0              │ 0             │ ocx-validator  │ 3.0.0b5       │ ocx.v3.0.0b4   │ 2024-01-04    │
│               │         │               │                │               │                │               │                │ 20:25:13+00:… │
│ C:\DNV\ocxto… │ FAILURE │ 5             │ 0              │ 0             │ ocx-validator  │ 3.0.0b5       │ ocx.v3.0.0b4   │ 2024-01-04    │
│               │         │               │                │               │                │               │                │ 20:49:30+00:… │
│ C:\DNV\ocxto… │ FAILURE │ 4             │ 0              │ 0             │ ocx-validator  │ 3.0.0b5       │ ocx.v3.0.0b4   │ 2024-01-04    │
│               │         │               │                │               │                │               │                │ 20:49:31+00:… │
│ C:\DNV\ocxto… │ FAILURE │ 14            │ 0              │ 0             │ ocx-validator  │ 3.0.0b5       │ ocx.v3.0.0b4   │ 2024-01-04    │
│               │         │               │                │               │                │               │                │ 20:49:36+00:… │
└───────────────┴─────────┴───────────────┴────────────────┴───────────────┴────────────────┴───────────────┴────────────────┴───────────────┘


ocxtools >:
````

### ``validate details``
The ``validate details`` command will print the detailed validation results for all models that has been validated during this session.

#### Example

````commandline
ocxtools >: validate details
============================================================= Validation Details =============================================================


                                                  Error Details for model: 'models/m1.3docx'
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━┓
┃ Description                                                                                                                ┃ Line ┃ Column ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━┩
│ cvc-complex-type.4: Attribute 'license' must appear on element 'ocx:Header'.                                               │ 12   │ 65     │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'NURBSproperties'. One of 'Description, Length' is │ 164  │ 53     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'NURBSproperties'. One of 'Description, Length' is │ 229  │ 59     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'Origin'. One of 'Description, Area' is expected.  │ 315  │ 56     │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'NURBSproperties'. One of 'Description, Length' is │ 323  │ 56     │
│ expected.                                                                                                                  │      │        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴──────┴────────┘




                                        Error Details for model: 'C:\\DNV\\ocxtools\\models\\M1.3docx'
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━┓
┃ Description                                                                                                                ┃ Line ┃ Column ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━┩
│ cvc-complex-type.4: Attribute 'license' must appear on element 'ocx:Header'.                                               │ 12   │ 65     │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'NURBSproperties'. One of 'Description, Length' is │ 164  │ 53     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'NURBSproperties'. One of 'Description, Length' is │ 229  │ 59     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'Origin'. One of 'Description, Area' is expected.  │ 315  │ 56     │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'NURBSproperties'. One of 'Description, Length' is │ 323  │ 56     │
│ expected.                                                                                                                  │      │        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴──────┴────────┘




                                        Error Details for model: 'C:\\DNV\\ocxtools\\models\\M2.3docx'
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━┓
┃ Description                                                                                                                ┃ Line ┃ Column ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━┩
│ cvc-complex-type.4: Attribute 'license' must appear on element 'ocx:Header'.                                               │ 12   │ 65     │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'NURBSproperties'. One of 'Description, Length' is │ 160  │ 54     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'NURBSproperties'. One of 'Description, Length' is │ 2114 │ 60     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'NURBSproperties'. One of 'Description, Length' is │ 4082 │ 63     │
│ expected.                                                                                                                  │      │        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴──────┴────────┘




                                        Error Details for model: 'C:\\DNV\\ocxtools\\models\\M3.3docx'
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━┓
┃ Description                                                                                                                ┃ Line ┃ Column ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━┩
│ cvc-complex-type.4: Attribute 'license' must appear on element 'ocx:Header'.                                               │ 12   │ 65     │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'NURBSproperties'. One of 'Description, Length' is │ 266  │ 53     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'NURBSproperties'. One of 'Description, Length' is │ 330  │ 59     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.b: The content of element 'ocx:SectionRef' is not complete. One of 'OffsetU, OffsetV' is expected.    │ 424  │ 63     │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'StartPoint'. One of 'Description, Length' is      │ 427  │ 69     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.b: The content of element 'ocx:SectionRef' is not complete. One of 'OffsetU, OffsetV' is expected.    │ 450  │ 63     │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'StartPoint'. One of 'Description, Length' is      │ 453  │ 69     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.b: The content of element 'ocx:SectionRef' is not complete. One of 'OffsetU, OffsetV' is expected.    │ 476  │ 63     │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'StartPoint'. One of 'Description, Length' is      │ 479  │ 69     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.b: The content of element 'ocx:SectionRef' is not complete. One of 'OffsetU, OffsetV' is expected.    │ 514  │ 33     │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'StartPoint'. One of 'Description, Length' is      │ 517  │ 69     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'StartPoint'. One of 'Description, Length' is      │ 546  │ 69     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'StartPoint'. One of 'Description, Length' is      │ 575  │ 69     │
│ expected.                                                                                                                  │      │        │
│ cvc-complex-type.2.4.a: Invalid content was found starting with element 'StartPoint'. One of 'Description, Length' is      │ 604  │ 69     │
│ expected.                                                                                                                  │      │        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴──────┴────────┘


ocxtools >:
````
The detailed report lists each error, assertion or warning found and its location in the XML file.

### ``validation readme``
The ``validation readme`` command displays this page in the browser.
