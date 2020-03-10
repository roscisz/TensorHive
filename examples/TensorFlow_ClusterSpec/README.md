# Running distributed trainings through TensorHive using ClusterSpec

This example shows how to use the TensorHive `task execution` module to
conveniently configure and execute distributed trainings configured using
standard TensorFlowV1 parameters for the [ClusterSpec](https://www.tensorflow.org/api_docs/python/tf/train/ClusterSpec)
cluster configuration class. 
[This DeepSpeech training application](https://github.com/roscisz/dnn_training_benchmarks/tree/master/TensorFlowV1_DeepSpeech_ldc93s1)
was used for the example.

## Running the training without TensorHive

In order to run the training manually, a separate worker process `python DeepSpeech.py`
on each node and a separate parameter server process have to be run 
with the appropriate parameter values set as follows:

**Application-specific parameters**

The training application used in this example requires specifying train, dev and
test data sets through the `train_files`, `dev_files` and `test_files` parameters.

**ClusterSpec parameters**

The `ps_hosts`, `worker_hosts`, `job_name` and `task_index` parameters
have to be appropriately configured depending
on the set of nodes taking part in the computations.
For example, a training on two nodes 172.17.0.3 and 172.17.0.4 would require the following
parameter values:

worker on 172.17.0.3:
```bash
--ps_hosts=172.17.0.3:2224
--worker_hosts=172.17.0.3:2222,172.17.0.4:2223
--job_name=worker
--task_index=0
```

worker on 172.17.0.4:
```bash
--ps_hosts=172.17.0.3:2224
--worker_hosts=172.17.0.3:2222,172.17.0.4:2223
--job_name=worker
--task_index=1
```
parameter server on 172.17.0.3:
```bash
--ps_hosts=172.17.0.3:2224
--worker_hosts=172.17.0.3:2222,172.17.0.4:2223
--job_name=ps
--task_index=0
```

**Other environment variables**

Depending on the environment, some other environment variables may have to be configured.
For example, in multi-GPU nodes, setting proper value of the CUDA_VISIBLE_DEVICES is useful
to prevent the process from needlessly utilizing GPU memory.
In this example, because the Mozilla DeepSpeech native client libraries are used, the
LD_LIBRARY_PATH environment variable has to be set for each process to `native_client/`. 

**Choosing the appropriate Python version**

In some cases, a specific Python binary has to be used for the training.
For example, in our environment, a python binary from a virtual environment
is used, so the python binary has to be defined as follows:

```
./venv/bin/python
```

**Summary**

Finally, full commands required to launch the training in our exemplary environment will be as follows:

worker on 172.17.0.3:
```bash
export LD_LIBRARY_PATH=native_client/
./venv/bin/python ./DeepSpeech.py --train_files=ldc93s1/ldc93s1.csv --dev_files=ldc93s1/ldc93s1.csv --test_files=ldc93s1/ldc93s1.csv --ps_hosts=172.17.0.3:2224 --worker_hosts=172.17.0.3:2222,172.17.0.4:2223 --job_name=worker --task_index=0
```

worker on 172.17.0.4: 
```bash
export LD_LIBRARY_PATH=native_client/
./venv/bin/python ./DeepSpeech.py --train_files=ldc93s1/ldc93s1.csv --dev_files=ldc93s1/ldc93s1.csv --test_files=ldc93s1/ldc93s1.csv --ps_hosts=172.17.0.3:2224 --worker_hosts=172.17.0.3:2222,172.17.0.4:2223 --job_name=worker --task_index=1
```

parameter server on 172.17.0.3:
```bash
export LD_LIBRARY_PATH=native_client/
./venv/bin/python ./DeepSpeech.py --train_files=ldc93s1/ldc93s1.csv --dev_files=ldc93s1/ldc93s1.csv --test_files=ldc93s1/ldc93s1.csv --ps_hosts=172.17.0.3:2224 --worker_hosts=172.17.0.3:2222,172.17.0.4:2223 --job_name=ps --task_index=0
```

## Running the training with TensorHive

The TensorHive `task execution` module allows convenient orchestration of distributed trainings.
It is available in the Tasks Overview view. The `CREATE TASKS FROM TEMPLATE` button allows to
conveniently configure tasks supporting a specific framework or distribution method. In this
example we choose the Tensorflow - cluster parameters template, and click `GO TO TASK CREATOR`:

![choose_template](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/TensorFlow_ClusterSpec/img/choose_template.png)

In the task creator, we set the Command to
```
./venv/bin/python ./DeepSpeech.py --train_files=ldc93s1/ldc93s1.csv --dev_files=ldc93s1/ldc93s1.csv --test_files=ldc93s1/ldc93s1.csv
```

In order to add the LD_LIBRARY_PATH environment variable, we enter the parameter name,
select Static (the same value for all processes) and click `ADD AS ENV VARIABLE TO ALL TASKS`.
Then, set the appropriate value of the environment variable (native_client/):


![env_var](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/TensorFlow_ClusterSpec/img/env_var.png)


The task creator allows also to conveniently specify other command-line arguments. For example,
should the `train_files`, `dev_files` and `test_files` parameters change throughout the training
processes, they could be handled by `ADD AS PARAMETER TO ALL TASKS`.

Use `ADD TASK` to create as many copies of the defined process as required and
select the appropriate hostname and resource (CPU/GPU_N) for the specified training process. Change
`job_name` to `ps` for the parameter server process. The resultant
command that will be executed by TensorHive on the selected node will be displayed above the process specification.
Note that the cluster parameters and CUDA_VISIBLE_DEVICES variable are configured automatically:
 
![ready](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/TensorFlow_ClusterSpec/img/ready.png)

After clicking the `CREATE ALL TASKS` button, the processes will be available on the process list for future actions.
To run the processes, select them and use the `Spawn selected tasks` button. If TensorHive is configured properly,
the task status should change to `running`:

![running](https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/TensorFlow_ClusterSpec/img/running.png)

Note, that the appropriate process PID will be displayed in the `pid` column. Task overview can
be used to schedule, spawn, stop, kill, edit the tasks, and see logs from their execution.
