FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04
RUN apt-get update
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        wget \
        git \
        python \
        python-dev \
        python-pip \
        python-wheel \
        python-numpy \
        libcurl3-dev  \
        ca-certificates \
        gcc \
        sox \
        libsox-fmt-mp3 \
        htop \
        nano \
        swig \
        cmake \
        libboost-all-dev \
        zlib1g-dev \
        libbz2-dev \
        liblzma-dev \
        locales \
        pkg-config \
        libsox-dev


RUN apt-get install -y python3 python3-pip
RUN pip3 install 'tensorflow-gpu==1.6.0' pandas python_speech_features pyxdg progressbar2 scipy

RUN git clone https://github.com/mozilla/DeepSpeech.git
WORKDIR /DeepSpeech/
RUN git reset --hard e00bfd0f413912855eb2312bc1efe3bd2b023b25

# GPU Environment Setup
ENV TF_NEED_CUDA 1
ENV CUDA_TOOLKIT_PATH /usr/local/cuda
ENV CUDA_PKG_VERSION 9-0=9.0.176-1
ENV CUDA_VERSION 9.0.176
ENV TF_CUDA_VERSION 9.0
ENV TF_CUDNN_VERSION 7.4.1
ENV CUDNN_INSTALL_PATH /usr/lib/x86_64-linux-gnu/
ENV TF_CUDA_COMPUTE_CAPABILITIES 6.0

# Common Environment Setup
ENV TF_BUILD_CONTAINER_TYPE GPU
ENV TF_BUILD_OPTIONS OPT
ENV TF_BUILD_DISABLE_GCP 1
ENV TF_BUILD_ENABLE_XLA 0
ENV TF_BUILD_PYTHON_VERSION PYTHON2
ENV TF_BUILD_IS_OPT OPT
ENV TF_BUILD_IS_PIP PIP

# Other Parameters
ENV CC_OPT_FLAGS -mavx -mavx2 -msse4.1 -msse4.2 -mfma
ENV TF_NEED_GCP 0
ENV TF_NEED_HDFS 0
ENV TF_NEED_JEMALLOC 1
ENV TF_NEED_OPENCL 0
ENV TF_CUDA_CLANG 0
ENV TF_NEED_MKL 0
ENV TF_ENABLE_XLA 0

ENV GIT_LFS_SKIP_SMUDGE=1 

RUN ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1
RUN cp /usr/include/cudnn.h /usr/local/cuda/include/cudnn.h

# Set library paths
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/usr/local/cuda/extras/CUPTI/lib64:/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu/:/usr/local/cuda/lib64/stubs/
WORKDIR /DeepSpeech/

RUN python3 util/taskcluster.py --arch gpu --target native_client/ --branch=v0.2.0
RUN python3 bin/import_ldc93s1.py ldc93s1
RUN wget https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/deepspeech/deepspeech_benchmarking.patch
RUN git apply deepspeech_benchmarking.patch
ENV LD_LIBRARY_PATH=native_client/

