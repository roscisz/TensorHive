# Using TensorHive for running distributed trainings in PyTorch

## Detailed example description

In this example we show how the TensorHive `task execution` module can be
used for convenient configuration and execution of distributed trainings
implemented in PyTorch. For this purpose, we run
[this PyTorch DCGAN sample application](https://github.com/roscisz/dnn_training_benchmarks/tree/master/PyTorch_dcgan_lsun/README.md)
in a distributed setup consisting of a NVIDIA DGX Station server `ai` and NVIDIA DGX-1 server `dl`,
equipped with 4 and 8 NVIDIA Tesla V100 GPUs respectively.

In the presented scenario, the servers were shared by a group of users using TensorHive
and at the moment we were granted reservations for GPUs 1 and 2 on `ai` and GPUs 1 and 7 on `dl`.
The python environment and training code were available on both nodes and
fake training dataset was used.


## Running without TensorHive

In order to enable networking, we had to set the `GLOO_SOCKET_IFNAME`
environment variable to proper network interface names on both nodes.
We selected the 20011 TCP port for communication. 

For our 4 GPU scenario, the following 4 processes had to be executed,
taking into account setting consecutive `rank` parameters starting from 0 and the `world-size`
parameter to 4:

worker 0 on `ai`:
```
export CUDA_VISIBLE_DEVICES=1
export GLOO_SOCKET_IFNAME=enp2s0f1
./dnn_training_benchmarks/PyTorch_dcgan_lsun/examples/dcgan/venv/bin/python dnn_training_benchmarks/PyTorch_dcgan_lsun/examples/dcgan/main.py --init-method tcp://ai.eti.pg.gda.pl:20011 --backend=gloo --rank=0 --world-size=4 --dataset fake --cuda
``` 

worker 1 on `ai`:
```
export CUDA_VISIBLE_DEVICES=2
export GLOO_SOCKET_IFNAME=enp2s0f1
./dnn_training_benchmarks/PyTorch_dcgan_lsun/examples/dcgan/venv/bin/python dnn_training_benchmarks/PyTorch_dcgan_lsun/examples/dcgan/main.py --init-method tcp://ai.eti.pg.gda.pl:20011 --backend=gloo --rank=1 --world-size=4 --dataset fake --cuda
```
 
worker 2 on `dl`:
```
export CUDA_VISIBLE_DEVICES=1
export GLOO_SOCKET_IFNAME=enp1s0f0
./dnn_training_benchmarks/PyTorch_dcgan_lsun/examples/dcgan/venv/bin/python dnn_training_benchmarks/PyTorch_dcgan_lsun/examples/dcgan/main.py --init-method tcp://ai.eti.pg.gda.pl:20011 --backend=gloo --rank=2 --world-size=4 --dataset fake --cuda
``` 

worker 3 on ai:
```
export CUDA_VISIBLE_DEVICES=7
export GLOO_SOCKET_IFNAME=enp1s0f0
./dnn_training_benchmarks/PyTorch_dcgan_lsun/examples/dcgan/venv/bin/python dnn_training_benchmarks/PyTorch_dcgan_lsun/examples/dcgan/main.py --init-method tcp://ai.eti.pg.gda.pl:20011 --backend=gloo --rank=3 --world-size=4 --dataset fake --cuda
``` 


## Running with TensorHive

Because running the distributed training required in our scenario means
logging into distributed nodes, configuring environments and running processes
with multiple, similar parameters, differing only slightly, it is a good
use case for the TensorHive `task execution` module.

To use it, first head to "Task Overview" and click on "CREATE TASKS FROM TEMPLATE". Choose PyTorch from the drop-down list: 

![choose_template](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/PyTorch/img/choose_template.png)

Fill the PyTorch process template with your specific python command, command-line
parameters and environment variables. 
You don't need to fill in rank or world-size parameters as TensorHive will do that automatically for you:

![parameters](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/PyTorch/img/parameters.png)

Add as many tasks as resources you wish the code to run on using "ADD TASK" button. You can see that every parameter filled is copied to newly created tasks to save time. Adjust hostnames and resources on the added tasks as needed.

![full_conf](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/PyTorch/img/full_conf.png)


Click "CREATE ALL TASKS" button in the right bottom corner to create the tasks.
Then, select them in the process table and use the "Spawn selected tasks" button,
to run them on the appropriate nodes:

![running](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/PyTorch/img/running.png)

After that, the tasks can be controlled from "Task Overview". 
The following actions are currently available:
- Schedule (Choose when to run the task)
- Spawn (Run the task now)
- Terminate (Send terminate command to the task)
- Kill (Send kill command)
- Show log (Read output of the task)
- Edit 
- Remove

Having that high level control over all of the tasks from a single place can be extremely time-saving!
