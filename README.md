# TensorHive

Resource management tool for executing distributed [TensorFlow](https://github.com/tensorflow/tensorflow) based on [KernelHive](https://github.com/roscisz/KernelHive) manager libraries.

GPU monitoring example:

0. Install KernelHive python libraries:

pip install kernelhive

1. Run the monitoring daemon:

python gpu_monitoring.py

2. Add nodes that should be monitored:

cd scripts
./add_node.sh <hostname>
