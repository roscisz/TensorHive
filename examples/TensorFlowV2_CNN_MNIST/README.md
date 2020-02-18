
# Using TensorHive for running distributed trainings in TensorFlow
Running distributed training in TensorFlow in multi-node environment requires spawning and managing processes on multiple machines.

This example shows how to make this task much easier using TensorHive. 

## Application
In this example we will use a very simple [CNN](https://github.com/roscisz/dnn_training_benchmarks/tree/master/TensorFlowV2_CNN_MNIST) implemented in TensorFlow . File `train_multi_worker_mirrored_strategy.py` contains model prepared for multi-node training. (For more distributed deep networks training examples please check out our [benchmark repository](https://github.com/roscisz/dnn_training_benchmarks)).

### Installation

**Clone the repository**
```bash
git clone https://github.com/roscisz/dnn_training_benchmarks.git
cd dnn_training_benchmarks/TensorFlowV2_CNN_MNIST/
```
**Install requirements**
```bash
pip install -r requirements.txt
```

## Running the training without TensorHive
For the sake of example let's assume that:

 - we have a cluster of two nodes: gl01 and gl02
 - on each of them Python binary location is `/path/to/python`
 - training file location is `/path/to/train_multi_worker_mirrored_strategy.py`

### TF_CONFIG
On each node we need to specify the **TF_CONFIG** environment variable, which is responsible for configuration of distributed training in TensorFlow.

Exaple settings of **TF_CONFIG** in our cluster:

gl01:
```json
{
   "cluster":{
      "worker":[
         "gl01:2222",
         "gl02:2222"
      ]
   },
   "task":{
      "type":"worker",
      "index":0
   }
}
```


gl02:
```json
{
   "cluster":{
      "worker":[
         "gl01:2222",
         "gl02:2222"
      ]
   },
   "task":{
      "type":"worker",
      "index":1
   }
}
```

### Training parameters
Usually we can adjust training settings via command line parameters. In our example we will use `--batch_size` parameter to set batch size to 32.

### Summary
In order to start distributed training on our cluster we will need to run following command line:

gl01:
```bash
export TF_CONFIG='{"cluster":{"worker":["gl01:2222", "gl02:2222"]}, "task":{"type": "worker", "index": 0}}'
```
```bash
/path/to/python /path/to/train_multi_worker_mirrored_strategy.py --batch_size 32
```
gl02:
```bash
export TF_CONFIG='{"cluster":{"worker":["gl01:2222", "gl02:2222"]}, "task":{"type": "worker", "index": 1}}'
```
```bash
/path/to/python /path/to/train_multi_worker_mirrored_strategy.py --batch_size 32
```