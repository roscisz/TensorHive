# Using tensorhive for running distributed trainings in PyTorch

This example is based on [this implementation](https://github.com/pytorch/examples/tree/master/dcgan)
```
git clone https://github.com/pytorch/examples.git
```

## Downloading the dataset

You can download the LSUN dataset by cloning [this repo](https://github.com/fyu/lsun) 

```
git clone https://github.com/fyu/lsun.git
```
and running
```
python download.py -c bedroom
```

For testing and/or benchmarking purposes it is also possible to the train the model on fake dataset. To do this, set the parameter `--dataset fake` when running the training program (ommit --dataroot parameter).


## Making the code parallel

It is actually very easy to allow PyTorch code to run on multiple GPUs

### Locally

All you need to do to make a data parallel model that can be run on multiple GPUs locally:
```
from torch import nn
<your code including creating the model>
model = nn.DataParallel(model)
```
That's it. After that you just control which GPUs you would like your code to run on by specifing their number in CUDA_VISIBLE_DEVICES before your command (tensorhive takes care of that for you when you specify the devices while creating the task).

### Distributed

To make the code distributed apply provided patch by running:

```
git apply distributed.patch
```

You might want to checkout commit 0c1654d6913f77f09c0505fb284d977d89c17c1a to make sure there are no conflicts before applying the patch.

To learn how to easily adapt PyTorch code for distributed learning please examine the patch. 

## Usage
```
# set accroding to your configuration
export GLOO_SOCKET_IFNAME=eth0 
```

```
CUDA_VISIBLE_DEVICES=0 python main.py --init-method tcp://127.0.0.1:20011 --rank 0 --world-size 2 --dataset lsun --dataroot <path to lsun dataset> --cuda
CUDA_VISIBLE_DEVICES=1 python main.py --init-method tcp://127.0.0.1:20011 --rank 1 --world-size 2 --dataset lsun --dataroot <path to lsun dataset> --cuda

For more details about the usage refer to the [original repo](https://github.com/pytorch/examples/tree/master/dcgan)
```

## Running without tensorhive

First export the `GLOO_SOCKET_IFNAME` environment variable on every node as shown in the Usage section. Next, find a port that is available on every node for communication. Then run separate commands as above on very node. Make sure to start with rank 0. Set world size to the number of nodes you want to run the code on. The training code and dataset needs to be available on every node.

## Running with tensorhive
Head to "Task Overview" (1) and click on "CREATE TASKS FROM TEMPLATE". Choose PyTorch from the drop-down list. 

![1](https://github.com/roscisz/TensorHive/tree/master/examples/PyTorch/img/1.png)

Choose host and resource to run the task on for the first node. Under command specify path to your pyhon and script to wish to run (as shown). Specify init-method. You don't need to fill in rank or world-size parameters as tensorhive will do that automatically for you.

![2](https://github.com/roscisz/TensorHive/tree/master/examples/PyTorch/img/2.png)

Add as many tasks as resources you wish the code to run on using "ADD TASK" button. You can see that every parameter filled is copied to newly created tasks to save time. Adjust Hostnames and resources on the added tasks as needed.

![3](https://github.com/roscisz/TensorHive/tree/master/examples/PyTorch/img/3.png)

Add GLOO_SOCKET_IFNAME envoirmental variable. By filling in the "Parameter name" below the tasks and clicking on "ADD AS ENV VARIABLE TO ALL TASKS" button. If you check the "Static" checkbox next to it you will be able to fill it only for one task and it will be copied to the rest of them. For most cases you will have the same connection configuration on all nodes so it can save you some effort. Fill the newly added env variable according to the configuration on your nodes. You can check the names of your internet interfaces by running `ifconfig` command on your nodes.

Click "CREATE ALL TASKS" button in the right bottom corner to create the tasks.

![4](https://github.com/roscisz/TensorHive/tree/master/examples/PyTorch/img/4.png)

After that you can control the tasks from "Task Overview". You can see avaiable actions on far right next to them. For now avaiable options are:
- Schedule (Choose when to run the task)
- Spawn (Run the task now)
- Terminate (Send terminate command to the task)
- Kill (Send kill command)
- Show log (Read output of the task)
- Edit 
- Remove

Having that high level control over all of the tasks from a single place can be extremely time-saving!
