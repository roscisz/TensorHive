# DeepSpeech benchmarks

In this example we provide experimental results and steps to reproduce for benchmarking performance of training the
[Baidu's Deep Speech](https://arxiv.org/abs/1412.5567) Recurrent Neural Network for automatic speech recognition.

The example is based on [Project DeepSpeech by Mozilla](https://github.com/mozilla/DeepSpeech) which is an open source
implementation in TensorFlow that supports distributed training using Distributed TensorFlow.

## Table of contents
- [x] [Installation instructions](#installation)
- [ ] [Instructions for running the benchmarks](#running-the-benchmarks)
  - [x] [Manually](#running-manually)
  - [ ] [Using TensorHive](#running-using-tensorhive)
- [ ] [Experimental results](#experimental-results):
  - [x] [Batch size influence on training performance on various GPUs](#batch-size)
  - [x] [Scalability on multiple GPUs](#multigpu-scalability)
  - [ ] Scalability in a distributed setting

## Installation

In this section we describe installation steps for DeepSpeech that we used in our setup.
For detailed instructions for running the DeepSpeech training go to the
[DeepSpeech project site](https://github.com/mozilla/DeepSpeech).

### Prerequisites

* GNU/Linux
* Python 3, Pip3, git, wget
* CUDA 9.0 with CuDNN 7
* TensorFlow 1.6.0
* Python packages: pandas, python_speech_features, pyxdg, progressbar2

The environment can be for example set up using nvidia-docker as follows:

```bash
nvidia-docker pull nvidia/cuda:9.0-cudnn7-devel
nvidia-docker run -it nvidia/cuda:9.0-cudnn7-devel
apt-get update
apt-get install -y python3 python3-pip git wget
pip3 install 'tensorflow-gpu==1.6.0' pandas python_speech_features pyxdg progressbar2 scipy
```

### Installing DeepSpeech

**Clone the proper version of DeepSpeech**
```bash
git clone https://github.com/mozilla/DeepSpeech.git
cd DeepSpeech/
git reset --hard e00bfd0f413912855eb2312bc1efe3bd2b023b25
```
Note: if you have git-lfs installed, you can disable it for the benchmarks using environment variable GIT_LFS_SKIP_SMUDGE=1.

**Download native libraries**
```bash
python3 util/taskcluster.py --arch gpu --target native_client/ --branch=v0.2.0
```

**Download small dataset**
```bash
python3 bin/import_ldc93s1.py ldc93s1
```

### Applying the benchmarking patch

```bash
wget https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/deepspeech/deepspeech_benchmarking.patch
git apply deepspeech_benchmarking.patch
```

## Running the benchmarks

In this section we describe the steps to reproduce the [experimental results](#experimental-results),
assuming that the DeepSpeech training program is installed and the benchmarking patch is applied.

### Running manually

To run the benchmark, specify the number of "global steps" to be benchmarked using the `benchmark_steps` parameter:

```bash
LD_LIBRARY_PATH=native_client/ CUDA_VISIBLE_DEVICES=0 python3 ./DeepSpeech.py --train_files=ldc93s1/ldc93s1.csv --dev_files=ldc93s1/ldc93s1.csv --test_files=ldc93s1/ldc93s1.csv --log_level=3 --benchmark_steps=10
```

**Testing batch size on one GPU**

To check the performance for various batch sizes, modify the `train_batch_size` parameter. For example, to use batch size of 128 run:

```bash
LD_LIBRARY_PATH=native_client/ CUDA_VISIBLE_DEVICES=0 python3 ./DeepSpeech.py --train_files=ldc93s1/ldc93s1.csv --dev_files=ldc93s1/ldc93s1.csv --test_files=ldc93s1/ldc93s1.csv --log_level=3 --benchmark_steps=10 --train_batch_size=128
```
**Testing scalability on many GPUs**

***In-graph replication***

To check the performance of parallel training on multiple GPUs, modify the CUDA_VISIBLE_DEVICES environment variable.
For example, to use GPUs 1 and 2, set CUDA_VISIBLE_DEVICES=1,2 and to use all GPUs in a 4-GPU system, set
CUDA_VISIBLE_DEVICES=0,1,2,3. The in-graph replication method for data-parallel, synchronized training implemented in
Mozilla DeepSpeech will be used.

### Running using TensorHive

## Experimental results

### Batch size

![batch_size_v100](https://raw.githubusercontent.com/roscisz/TensorHive/develop/examples/deepspeech/img/batch_size_v100.png)
![batch_size_gtx1060](https://raw.githubusercontent.com/roscisz/TensorHive/develop/examples/deepspeech/img/batch_size_gtx1060.png)

### MultiGPU scalability

The following results show performance results on NVIDIA® DGX Station™, depending on the choice utilized GPUs. The
results are marked with ID's of the used GPUs, for example '013' means that CUDA_VISIBLE_DEVICES was set to 0,1,3.

![multigpu_128](https://raw.githubusercontent.com/roscisz/TensorHive/develop/examples/deepspeech/img/multigpu_128.png)
![multigpu_64](https://raw.githubusercontent.com/roscisz/TensorHive/develop/examples/deepspeech/img/multigpu_64.png)

Two interesting facts can be seen in the charts. First, in the cases of utilizing two GPUs, it is significant which
GPUs are used exactly. For example, combining GPUs 0 and 1 or 2 and 3 results in worse performance. This is probably
connected with interconnects between the GPUs. The differences are more visible in the case of higher batch size per
GPU, which results in more intensive communication during synchronization. Secondly, scalability beyond two GPUs is
poor for high batch size (128), while for lower batch_size (64) scalability is better, giving the best performance on
4 GPUs. 

