FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04

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
RUN apt-get install -qq -y cuda-command-line-tools-9-0

# Install pip
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py

RUN mkdir /usr/local/cuda/lib &&  \
    ln -s /usr/lib/x86_64-linux-gnu/libnccl.so.2 /usr/local/cuda/lib/libnccl.so.2 && \
    ln -s /usr/include/nccl.h /usr/local/cuda/include/nccl.h && \
    ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 && \
    ln -s /usr/include/cudnn.h /usr/local/cuda/include/cudnn.h

ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/usr/local/cuda/extras/CUPTI/lib64:/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu/:/usr/local/cuda/lib64/stubs/

RUN git clone https://github.com/tensorflow/tensor2tensor.git
WORKDIR /tensor2tensor
RUN git checkout 178738d
RUN wget https://raw.githubusercontent.com/roscisz/TensorHive/master/examples/t2t_transformer/tensor2tensor_benchmarking.patch
RUN git apply tensor2tensor_benchmarking.patch
RUN pip install tensorflow-gpu==1.12.0
RUN pip install .
ENV PROBLEM=translate_ende_wmt32k
RUN pip install tensor2tensor
ENV MODEL=transformer
ENV HPARAMS=transformer_base_single_gpu
ENV DATA_DIR=$HOME/t2t_data
ENV TRAIN_DIR=$HOME/t2t_train/$PROBLEM/$MODEL-$HPARAMS
ENV CUDA_VISIBLE_DEVICES=0



ENV DATA_DIR=/root/t2t_data
ENV TMP_DIR=/tmp/t2t_datagen
ENV TRAIN_DIR=/root/t2t_train/$PROBLEM/$MODEL-$HPARAMS

RUN mkdir -p $DATA_DIR $TMP_DIR $TRAIN_DIR

RUN wget https://github.com/roscisz/TensorHive/raw/master/examples/t2t_transformer/t2t_data.tar.gz
RUN tar xzf t2t_data.tar.gz
RUN rm t2t_data.tar.gz
