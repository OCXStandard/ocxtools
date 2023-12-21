# docker CLI

## Introduction
The docker CLI provides the user with simple commands to manage the [OCX validator](https://github.com/OCXStandard/ocx-validator) container without the need for the detailed knowledge of how to pull  the OCX validator image from the Docker Hub and start the container.
A prerequisite is to have a docker service installed and accessible from your computer.
Currently, the docker CLI only supports [Docker Desktop on Windows]( https://docs.docker.com/desktop/).

## Installing the docker environment

Follow the [installation instructions](https://docs.docker.com/desktop/install/windows-install/) to install the docker runtime environment.
The OCX Validator will require more resources than the default set-up. After the Docker Desktop installation,
increase the available memory resources for docker from the default 2024 MB to 8192 MB by changing the value of the ``memoryMiB``
key in the JSON settings file:

```
C:\Users\[USERNAME]\AppData\Roaming\Docker\settings.json.
```

Save the file and restart the Docker Desktop.

## Usage

From the command line prompt, type the help command for the docker CLI to obtain the information of the available commands:

```
ocxtools >: docker --help

 Usage:  [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                              │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.       │
│ --help                        Show this message and exit.                                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ check        Check the status of the docker validator container.                                                     │
│ run          Start the docker validator container.                                                                   │
│ start        Start the docker Desktop (Windows only).                                                                │
│ stop         Stop and remove the validator container.                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

ocxtools >:
```
### check

The ``check`` command will check if the docker runtime is up:

```commandline
ocxtools >: docker check
❌     Command failed with error:
error during connect: this error may indicate that the docker daemon is not running: Get
"http://%2F%2F.%2Fpipe%2Fdocker_engine/v1.24/containers/json?all=1": open //./pipe/docker_engine: The system cannot find
the file specified.
```
If the check fails as shown above, issue the ``start`` command to start the Docker Desktop

### start

The ``start`` command wil start the Docker Desktop:

````commandline
ocxtools >: docker start
0
ocxtools >:
````
Wait for the desktop to start before running the OCX Validator container.

### run
The ``run`` command wil start the OCX Validator container:
````commandline
ocxtools >: docker run
❌     Command failed with error:
3.0.0b5: Pulling from 3docx/validator
Digest: sha256:a40bb70875081c4bc613f797991966d71772f7d54958fe471d7015ec0f893ced
Status: Image is up to date for 3docx/validator:3.0.0b5
docker: Error response from daemon: Conflict. The container name "/validator" is already in use by container "ee7c6abc5271797b6e1c28f543d461d6b29d3fa503dfc1680777261533c05b44". You have to remove (or rename) that container to be able to reuse that name.
See 'docker run --help'.

ℹ     Command output:
CONTAINER ID   IMAGE                     COMMAND                  CREATED       STATUS                       PORTS                    NAMES
ee7c6abc5271   3docx/validator:3.0.0b5   "java -XX:+ExitOnOut…"   2 hours ago   Exited (255) 3 minutes ago   0.0.0.0:8080->8080/tcp   validator

````
The above result shows us two things happening in the background:
1. The ``run`` command will pull the latest docker image from the repository on Docker Hub. In the case above, there is an uptodate version already available in the runtime environment. This is perfectly fine.
2. The next response is an error message when the command tries to create the ``validator`` container from the pulled image. Since there is already a container named ``validator`` the command fails.

In order to come around this problem, you need to remove the container first.

## stop
The ``stop`` command will do two things:
1. stop a running ``validator`` container
2. remove the container

````commandline
ocxtools >: docker stop
ℹ     Command output:
validator

ℹ     Command output:
validator

ocxtools >:
````

After running the ``stop`` command, issue the ``run`` command to pull a fresh image (if available) and run the validator:

````commandline
ocxtools >: docker run
ℹ     Command output:
d0c1409927be662249f8350c0c8dc20bd451c17a780e3239d1c23c58e964108d

ℹ     Command output:
CONTAINER ID   IMAGE                     COMMAND                  CREATED        STATUS                  PORTS                    NAMES
d0c1409927be   3docx/validator:3.0.0b5   "java -XX:+ExitOnOut…"   1 second ago   Up Less than a second   0.0.0.0:8080->8080/tcp   validator

ocxtools >:
````
Now the OCX Validator is ready. See the ``validator`` commands for how to validate the 3Docx models.
