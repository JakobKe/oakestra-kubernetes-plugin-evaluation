This repository serves as an evaluation and measurement repository for the Kubernetes Oakestra Plugin.

In addition to other configuration files, the folder contains a file named only-root.yaml. This file is a Docker-compose file used to start the Oakestra Root. The evaluations were conducted using the versions of the images specified in this file.

The structure is as follows:

In /tests, all test scripts can be found. It should be noted that the measurement of overhead must be started manually.

In /results, all results of each test run are stored.

In /metrics, the scripts for the measurements can be found.

In /evaluation, the results are processed to extract information and graphs from them.


