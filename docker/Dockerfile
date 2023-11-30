FROM nvcr.io/nvidia/pytorch:22.10-py3

ENV PROJECT_ROOT=/root
ENV PROJECT_DIR=/root/ndltsr
ENV WORK_DIR=/root/ndltsr/src
ENV FORCE_CUDA="1"
ENV TORCH_CUDA_ARCH_LIST="7.5+PTX"
ENV TORCH_NVCC_FLAGS="-Xfatbin -compress-all"

RUN set -x \
    && apt update \
    && apt upgrade -y

RUN set -x \
    && apt update \
    && apt -y install locales \
    && locale-gen ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8
RUN localedef -f UTF-8 -i ja_JP ja_JP.utf8


ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN set -x && apt -y install libglib2.0-0
RUN set -x && apt -y install libgl1-mesa-dev
RUN set -x && apt -y install vim git

RUN set -x && pip install tqdm opencv-python==4.5.1.48 pycocotools==2.0.6 progress==1.6 shapely==2.0.1 imgaug==0.4.0 msgpack==1.0.7 fastapi==0.104.1 uvicorn==0.23.2

COPY . ${PROJECT_ROOT}

RUN set -x && wget -nc https://lab.ndl.go.jp/dataset/ndltsrmodel/model_last.pth  ${PROJECT_DIR}/exp/ctdet_mid/train_wireless_ndl/
RUN set -x && wget -nc https://lab.ndl.go.jp/dataset/ndltsrmodel/processor_last.pth  ${PROJECT_DIR}/exp/ctdet_mid/train_wireless_ndl/

WORKDIR ${WORK_DIR}

EXPOSE 8080

ENTRYPOINT ["python3","api.py"]
