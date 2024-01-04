# validate CLI

## Introduction
The ``validate`` CLI provides the user with CLI commands to validate 3Docx models using the docker OCX validator service.

## Usage

From the command line prompt, type the help command for the docker CLI to obtain the information of the available commands:

````commandline
ocxtools >: help validate

 Usage:  [OPTIONS] COMMAND [ARGS]...

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                           │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                    │
│ --help                        Show this message and exit.                                                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ info                                     Verify that the Docker validator is alive and obtain the available validation options.   │
│ list-reports                             List validated models with summary results..                                             │
│ many-models                              Validate many 3Docx XML files with the docker validator.                                 │
│ one-model                                Validate one 3Docx XML file with the docker validator.                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

ocxtools >:
````

### info

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

### validate one

The ``validate-one`` sub-command will validate one model:

````commandline

````
