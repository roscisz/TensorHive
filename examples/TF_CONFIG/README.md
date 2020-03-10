# Running distributed trainings through TensorHive using TF_CONFIG

This example shows how to use the TensorHive `task execution` module to
conveniently configure and execute distributed trainings using
the TF_CONFIG environment variable. 
[This MSG-GAN training application](https://github.com/roscisz/dnn_training_benchmarks/tree/master/TensorFlowV2_MSG-GAN_Fashion-MNIST)
was used for the example.

## Running the training without TensorHive

In order to run the training manually, a separate process `python train.py`
has to be run on each node with the appropriate values of parameters set as follows.

**TF_CONFIG**

The TF_CONFIG environment variable has to be appropriately configured depending
on the set of nodes taking part in the computations.
For example, a training on two nodes gl01 and gl02 would require the following
settings of TF_CONFIG:

gl01:
```bash
TF_CONFIG='{"cluster":{"worker":["gl01:2222", "gl02:2222"]}, "task":{"type": "worker", "index": 0}}'
```

gl02:
```bash
TF_CONFIG='{"cluster":{"worker":["gl01:2222", "gl02:2222"]}, "task":{"type": "worker", "index": 1}}'
```

**Other environment variables**

Depending on the environment, some other environment variables may have to be configured.
For example, in multi-GPU nodes, setting proper value of the CUDA_VISIBLE_DEVICES is useful
to prevent the process from needlessly utilizing GPU memory. In this example,
because the utilized TensorFlow compilation uses a custom MPI library, the LD_LIBRARY_PATH environment
variable has to be set for each process to /usr/mpi/gcc/openmpi-4.0.0rc5/lib/.

**Choosing the appropriate Python version**

In some cases, a specific Python binary has to be used for the training.
For example, in our environment, a python binary from a virtual environment
is used, so the python binary has to be defined as follows:

```
/home/roy/venv/p37avxmpitf2/bin/python
```

**Summary**

Finally, full commands required to launch the training in our exemplary environment will be as follows:

gl01:

```bash
export TF_CONFIG='{"cluster":{"worker":["gl01:2222", "gl02:2222"]}, "task":{"type": "worker", "index": 0}}'
export LD_LIBRARY_PATH='/usr/mpi/gcc/openmpi-4.0.0rc5/lib/'
/home/roy/venv/p37avxmpitf2/bin/python /home/roy/dnn_training_benchmarks/TensorFlowV2_MSG-GAN_Fashion-MNIST/train.py
```

gl02:

```
export TF_CONFIG='{"cluster":{"worker":["gl01:2222", "gl02:2222"]}, "task":{"type": "worker", "index": 1}}'
export LD_LIBRARY_PATH='/usr/mpi/gcc/openmpi-4.0.0rc5/lib/'
/home/roy/venv/p37avxmpitf2/bin/python /home/roy/dnn_training_benchmarks/TensorFlowV2_MSG-GAN_Fashion-MNIST/train.py
```


## Running the training with TensorHive

The TensorHive `task execution` module allows convenient orchestration of distributed trainings.
It is available in the Tasks Overview view. The `CREATE TASKS FROM TEMPLATE` button allows to
conveniently configure tasks supporting a specific framework or distribution method. In this
example we choose the Tensorflow - TF_CONFIG template, and click `GO TO TASK CREATOR`:

![choose_template](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/TF_CONFIG/img/choose_template.png)

In the task creator, we set the Command to
```
/home/roy/venv/p37avxmpitf2/bin/python /home/roy/dnn_training_benchmarks/TensorFlowV2_MSG-GAN_Fashion-MNIST/train.py
```

In order to add the LD_LIBRARY_PATH environment variable, we enter the parameter name,
select Static (the same value for all processes) and click `ADD AS ENV VARIABLE TO ALL TASKS`:

![env_var](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/TF_CONFIG/img/env_var.png)

Then, set the appropriate value of the environment variable (/usr/mpi/gcc/openmpi-4.0.0rc5/lib/).

The task creator allows also to conveniently specify other command-line arguments. For example,
to specify batch size, we enter parameter name --batch_size, again select Static and click
`ADD AS PARAMETER TO ALL TASKS` and set its value (in our case 32).

Select the required hostname and resource (CPU/GPU_N) for the specified training process. The resultant
command that will be executed by TensorHive on the selected node will be displayed above the process specification:

![single_process](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/TF_CONFIG/img/single_process.png)

Note that the TF_CONFIG and CUDA_VISIBLE_DEVICES variables are configured automatically. Now, use
the `ADD TASK` button to duplicate the processes and modify the required target hosts to create
your training processes. For example, this screenshot shows the configuration for training on 4
hosts: gl01, gl02, gl03, gl04:

![multi_process](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/TF_CONFIG/img/multi_process.png)

After clicking the `CREATE ALL TASKS` button, the processes will be available on the process list for future actions.
To run the processes, select them and use the `Spawn selected tasks` button. If TensorHive is configured properly,
the task status should change to `running`:

![running](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/TF_CONFIG/img/running.png)

Note, that the appropriate process PID will be displayed in the `pid` column. Task overview can
be used to schedule, spawn, stop, kill, edit the tasks, and see logs from their execution.
