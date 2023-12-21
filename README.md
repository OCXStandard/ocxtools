# ocxtools
> ### A python CLI to work with 3Docx models.

``ocxtools`` is a configurable Python CLI shell with pluggable subcommands. The CLI combines features from [``click``](https://click.palletsprojects.com/en/8.1.x/),
[``click-shell``](https://click-shell.readthedocs.io/en/latest/), [``typer``](https://typer.tiangolo.com/) and [``Rich``](https://rich.readthedocs.io/en/stable/introduction.html)
with emphasis on **Typer** and **Rich** to make a good-looking CLI.

## Installation

# Usage
## The main CLI

````commandline

             ,----..
            /   /   \    ,----..   ,--,     ,--,
           /   .     :  /   /   \  |'. \   / .`|
          .   /   ;.  \|   :     : ; \ `\ /' / ;
         .   ;   /  ` ;.   |  ;. / `. \  /  / .'          ______   ___    ___   _     _____
         ;   |  ; \ ; |.   ; /--`   \  \/  / ./          |      | /   \  /   \ | |   / ___/
         |   :  | ; | ';   | ;       \  \.'  /     _____ |      ||     ||     || |  (   \_
         .   |  ' ' ' :|   : |        \  ;  ;     |     ||_|  |_||  O  ||  O  || |___\__  |
         '   ;  \; /  |.   | '___    / \  \  \    |_____|  |  |  |     ||     ||     /  \ |
          \   \  ',  / '   ; : .'|  ;  /\  \  \            |  |  |     ||     ||     \    |
           ;   :    /  '   | '/  :./__;  \  ;  \           |__|   \___/  \___/ |_____|\___|
            \   \ .'   |   :    / |   : / \  \  ;
             `---`      \   \ .'  ;   |/   \  ' |
                         `---`    `---'     `--`

Version: 0.1.0
Copyright (c) 2023. OCX Consortium (https://3docx.org)

Starting ocxtools...
ocxtools >: help

Documented commands (type help <topic>):
========================================
clear  docker  render  report  serialize  show-log  validate  version

Undocumented commands:
======================
exit  help  quit

ocxtools >:

````

## Sub-commands
[### docker](ocxtools/docker/readme.md)
