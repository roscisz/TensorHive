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
  - [ ] Scalability on multiple GPUs
  - [ ] Scalability on multiple nodes

## Installation

In this section we describe installation steps for DeepSpeech that we used in our setup.
For detailed instructions for running the DeepSpeech training go to the
[DeepSpeech project site](https://github.com/mozilla/DeepSpeech).

### Prerequisites

* Ubuntu 16.04
* Python 3, Pip3
* CUDA 9.0 with CuDNN 7
* TensorFlow 1.6.0

**Running on nvidia-docker**
```bash
nvidia-docker pull nvidia/cuda:9.0-cudnn7-devel
nvidia-docker run -it nvidia/cuda:9.0-cudnn7-devel
apt-get update
apt-get install -y python3 python3-pip git wget
pip3 install 'tensorflow-gpu==1.6.0' pandas python_speech_features pyxdg progressbar2
```

### Installing DeepSpeech

**Install python bindings**
```bash
pip3 install deepspeech
```

**Clone the proper version of DeepSpeech**
```bash
git clone https://github.com/mozilla/DeepSpeech.git
cd DeepSpeech/
git reset --hard e00bfd0f413912855eb2312bc1efe3bd2b023b25
```

**Download native libraries**
```bash
python3 util/taskcluster.py --arch gpu --target native_client/
```

**Download small dataset**
```bash
python3 bin/import_ldc93s1.py ldc93s1
```

### Applying the benchmarking patch

```bash
wget https://raw.githubusercontent.com/roscisz/TensorHive/feature/deepspeech_example/examples/deepspeech/deepspeech_benchmarking.patch
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
LD_LIBRARY_PATH=native_client/ python3 ./DeepSpeech.py --train_files=ldc93s1/ldc93s1.csv --dev_files=ldc93s1/ldc93s1.csv --test_files=ldc93s1/ldc93s1.csv --log_level=3 --benchmark_steps=10 --train_batch_size=128
```
### Running using TensorHive

## Experimental results

### Batch size

![batch_size_v100](https://raw.githubusercontent.com/roscisz/TensorHive/feature/deepspeech_example/examples/deepspeech/img/batch_size_v100.png)
TODO: repeat v100 tests when other GPUs, CPU and PCI are not used
![batch_size_gtx1060](https://raw.githubusercontent.com/roscisz/TensorHive/feature/deepspeech_example/examples/deepspeech/img/batch_size_gtx1060.png)

