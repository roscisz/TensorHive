# T2T Transformer benchmarks

In this example we provide experimental results and steps to reproduce for benchmarking performance of training the
Transformer model (from [Attention is All You Need](https://arxiv.org/abs/1706.03762) paper) for automatic language translation.

The example is based on [Tensor2Tensor](https://github.com/tensorflow/tensor2tensor) (T2T), which is an open-source library,
that implements various models for various problems using TensorFlow background. We benchmark its Transformer implementation
for single-machine as well as in distributed training scenario.

## Table of contents
- [x] [Installation instructions](#installation)
- [ ] [Instructions for running the benchmarks](#running-the-benchmarks)
  - [x] [Manually](#running-manually)
  - [ ] [Using TensorHive](#running-using-tensorhive)
- [ ] [Experimental results](#experimental-results):
  - [x] [Batch size influence on training performance on various GPUs](#batch-size)
  - [ ] Scalability on multiple GPUs
  - [ ] Scalability on multiple nodes
- [x] [Kubernetes](#kubernetes)  

## Installation

In this section we describe installation steps for T2T Transformer that we used in our setup.
For detailed instructions for training this or other T2T models, go to
[Tensor2Tensor](https://github.com/tensorflow/tensor2tensor) project.

### Prerequisites

* GNU/Linux, kernel v. 4.4
* Python 3, Pip3
* CUDA 9.0 with CuDNN 7
* TensorFlow 1.10.0
* git
* wget

**Running on nvidia-docker**
```bash
nvidia-docker pull nvidia/cuda:9.0-cudnn7-devel
nvidia-docker run -it nvidia/cuda:9.0-cudnn7-devel
apt-get update
apt-get install -y python3 python3-pip git wget
pip3 install 'tensorflow-gpu==1.10.0'
```

### Installing Tensor2Tensor with the benchmarking patch


**Clone the proper version of tensor2tensor**
```bash
git clone https://github.com/tensorflow/tensor2tensor.git
cd tensor2tensor
git checkout 178738d
```

**Apply the benchmarking patch**

```bash
wget https://raw.githubusercontent.com/roscisz/TensorHive/feature/t2t_transformer_example/examples/t2t_transformer/tensor2tensor_benchmarking.patch
git apply tensor2tensor_benchmarking.patch
```

**Installing tensor2tensor with pip3**

(from tensor2tensor directory)
```bash
pip3 install .
```


### Download a dataset

For benchmarking purposes, you can download a minimal subset of the original
dataset for English-German translation task:

```bash
cd $HOME
wget https://raw.githubusercontent.com/roscisz/TensorHive/feature/t2t_transformer_example/examples/t2t_transformer/t2t_data.tar.gz
tar xzf t2t_data.tar.gz
rm t2t_data.tar.gz
```

If you need the whole `translate_ende_wmt32k` dataset, you can obtain it with the following
(takes some time):

```bash
PROBLEM=translate_ende_wmt32k
DATA_DIR=$HOME/t2t_data
TMP_DIR=/tmp/t2t_datagen

mkdir -p $DATA_DIR $TMP_DIR

# Generate data
t2t-datagen \
  --data_dir=$DATA_DIR \
  --tmp_dir=$TMP_DIR \
  --problem=$PROBLEM
```


## Running the benchmarks

In this section we describe the steps to reproduce the
[experimental results](#experimental-results),
assuming that Tensor2Tensor with the benchmarking patch is installed.
Results were obtained on the subset of the original `translate_ende_wmt32k` problem,
provided above.


### Running manually

To run the benchmark, specify the number of "global steps" to be benchmarked
using the `benchmark_steps` parameter:

```bash
PROBLEM=translate_ende_wmt32k
MODEL=transformer
HPARAMS=transformer_base_single_gpu

DATA_DIR=$HOME/t2t_data
TRAIN_DIR=$HOME/t2t_train/$PROBLEM/$MODEL-$HPARAMS

CUDA_VISIBLE_DEVICES=0 t2t-trainer --data_dir=$DATA_DIR --problem=$PROBLEM \
    --model=$MODEL --hparams_set=$HPARAMS --output_dir=$TRAIN_DIR \
    --log_level=30 --benchmark_steps=50

```

**Testing batch size on one GPU**

To check the performance for various batch sizes, modify the `batch_size`
hyperparameter under `hparams` argument. For example, to use batch size of 512
run:

```bash
CUDA_VISIBLE_DEVICES=0 t2t-trainer --data_dir=$DATA_DIR --problem=$PROBLEM \
    --model=$MODEL --hparams_set=$HPARAMS --output_dir=$TRAIN_DIR \
    --log_level=30 --benchmark_steps=50 --hparams='batch_size=512'
```


### Running using TensorHive

## Experimental results

### Batch size

![batch_size_v100](https://raw.githubusercontent.com/roscisz/TensorHive/develop/examples/t2t_transformer/img/bs_v100_single.png)
TODO: repeat v100 tests when other GPUs, CPU and PCI are not used
![batch_size_gtx1060](https://raw.githubusercontent.com/roscisz/TensorHive/develop/examples/t2t_transformer/img/bs_gtx1060_single.png)

## Kubernetes

### Running example
To build docker image using provided Dockerfile run
`docker build -t <yourdockerhub>/tensor2tensor .`
while in directory with Dockerfile.
Afterwards to push image to dockerhub (no need if it's been built on the same machine it will be tested later on)
`docker push <yourdockerhub>/tensor2tensor`
To run example change image docker name in t2t.yaml for a correct one and run
`sudo kubectl create -f t2t.yaml`
```
sudo kubectl get pod //see current pods
sudo kubectl describe pod t2t //check pod specification
sudo kubectl logs t2t //check logs from pod
```


### Configuring GPUs
Unfortunately kubernetes doesn't take into account other process using GPUs which leads to out-of-memory errors if somebody else runs their trening manually. Because CUDA_VISIBLE_DEVICES env variable is used inside the container it can only chose from GPUs kubernetes assigns to the container. So if we would like to deploy our training to GPU number 3 we would have to set GPUs limit to 4 and set CVD to "3". That is if the GPUs are on a single node. If they would be on different ones we could use [node labels and selectors](https://kubernetes.io/docs/tasks/configure-pod-container/assign-pods-nodes/).

### Benchmarking results
After running benchmarks on same commit and envoirment as natively we got very simlliar results which means docker is not adding any overhead (the results may vary a bit due to small variables as temperature of the machine and/or in the room). A significant advantage of Kubernetes is a possibility to just schedule all of the test jobs at once and Kubernetes will deal with running them on free GPUs whenever possible. However while we where testing it we found out that running benchmark on one GPU is noticeably faster if other GPUs are free.