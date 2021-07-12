# syntax = docker/dockerfile:experimental
#
# NOTE: To build this you will need a docker version > 18.06 with
#       experimental enabled and DOCKER_BUILDKIT=1
#
#       If you do not use buildkit you are not going to have a good time
#
#       For reference:
#           https://docs.docker.com/develop/develop-images/build_enhancements/
ARG TORCH_BUILD_IMAGE=nvidia/cuda:11.2.2-cudnn8-devel-ubuntu20.04
ARG BASE_IMAGE=nvidia/cuda:11.2.2-cudnn8-runtime-ubuntu20.04

FROM ${TORCH_BUILD_IMAGE} as dev-base
ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,id=apt-dev,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        ccache \
        cmake \
        curl \
        git \
        libjpeg-dev \
        libpng-dev \
    && rm -rf /var/lib/apt/lists/* \
    && /usr/sbin/update-ccache-symlinks \
    && mkdir /opt/ccache \
    && ccache --set-config=cache_dir=/opt/ccache

FROM dev-base as conda
ARG MAGMA_CUDA_VERSION=112
ENV PATH /opt/conda/bin:$PATH
RUN curl -o ~/miniconda.sh -O https://repo.anaconda.com/miniconda/Miniconda3-py38_4.9.2-Linux-x86_64.sh \
    && bash ~/miniconda.sh -p /opt/conda -b \
    && rm ~/miniconda.sh \
    && conda install -y \
        astunparse \
        cffi \
        cmake \
        conda-build \
        dataclasses \
        ipython \
        future \
        mkl \
        mkl-include \
        ninja \
        numpy \
        python=3.8 \
        pyyaml \
        setuptools \
        six \
        requests \
        typing_extensions \
    && conda install -y -c  pytorch "magma-cuda${MAGMA_CUDA_VERSION}" \
    && conda clean -ya


ARG TORCH_GIT_REV=be038d89898d0d2111b8acedefd08ceed62664cb
FROM conda as torch_build
WORKDIR /opt/pytorch/pytorch
RUN git clone https://github.com/pytorch/pytorch . \
    && git checkout ${TORCH_GIT_REV} \
    && git submodule sync \
    && git submodule update --init --recursive \
    && export CMAKE_PREFIX_PATH="/opt/conda/bin" \
    && USE_CUDA=1 USE_CUDNN=1 USE_MKLDNN=1 \
    TORCH_CUDA_ARCH_LIST="3.5 5.2 6.0 6.1 7.0+PTX" \
    TORCH_NVCC_FLAGS="-Xfatbin -compress-all" \
    MAX_JOBS=40 \
    python setup.py install

ARG TORCHVISION_GIT_REV=9a6c8bbebdde22b37255f6a78816839823f28d8b
WORKDIR /opt/pytorch/vision
RUN git clone https://github.com/pytorch/vision . \
    && git checkout ${TORCHVISION_GIT_REV} \
    && python setup.py install

FROM ${BASE_IMAGE} as build
ENV PATH /opt/conda/bin:$PATH
COPY --from=torch_build /opt/conda /opt/conda

ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,id=apt-dev,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        ffmpeg \
        gcc \
        git \
        libjpeg-dev \
        libpng-dev \
        libsm6 \
        libxext6 \
        wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# SlowFast python dependencies:
# Acquired from https://raw.githubusercontent.com/facebookresearch/SlowFast/9dd4923/INSTALL.md
RUN export CMAKE_PREFIX_PATH="/opt/conda/bin" \
    && pip install \
        albumentations==1.0.0 \
        cython==0.29.23 \
        efficientnet_pytorch \
        iopath==0.1.8 \
        moviepy==1.0.3 \
        omegaconf==2.1.0.rc1 \
        opencv-python==4.5.1.48 \
        psutil==5.8.0 \
        pytorchvideo==0.1.1 \
        scikit-learn==0.24.2 \
        simplejson==3.17.2 \
	hydra-core==1.1.0 \
	hydra_colorlog==1.1.0


COPY classifier /workspace/classifier
COPY rmq_manager /workspace/rmq_manager

RUN pip install -e rmq_manager
