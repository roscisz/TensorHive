# TensorHive

TensorHive is a work in progress project with the objective to develop
a lightweight computing resource management tool for executing
machine learning applications in distributed
[TensorFlow](https://github.com/tensorflow/tensorflow).
The first planned feature of TensorHive is a resource reservation
module supporting sharing scarce computing resources (GPUs in particular)
by a group of users.
The planned core feature of TensorHive is to allow easy execution of
distributed trainings without the need for manual logging in to every
worker node or installing and configuring resource management daemons.
Further planned features include task queuing and hardware and library
version selection based on application requirements, as well as supporting
machine learning applications in frameworks other than TensorFlow.

In the current version, TensorHive can be used for monitoring utilization and process owners of GPUs in a cluster.
~~Beta version enabling executing distributed TensorFlow applications is a milestone planned for 31.12.2017.~~
Due to funding delays, the milestones have been modified:  
Beta version of the resource reservation module - 30.06.2018  
Beta version enabling executing distributed TensorFlow applications - 30.09.2018

TensorHive includes code initially developed for the management module in [KernelHive](https://github.com/roscisz/KernelHive).

## Requirements

* cluster nodes should be accessible by SSH without password
* GPUs should support utilization monitoring through nvidia-smi

## Installation

```shell
$ pip install tensorhive
```

## Usage

1. Run TensorHive:
```shell
$ tensorhive
```

2. Browse to http://localhost:31333

3. Add managed nodes by inserting their hostnames and clicking "Add node"

4. Watch GPU utilization and process owners on an interactive dashboard
