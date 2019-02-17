## Table of contents
- [x] [Why Kubernetes](#why-kubernetes)
- [x] [Usage options](#usage-options)
- [x] [Installation](#installation)
- [x] [Running single process learning](#running-single-process-learning)
- [x] [Running distributed learning](#running-distributed-learning)
- [x] [Summary](#summary)
- [ ] [Experimental results](#experimental-results)




## Why Kubernetes
Kubernetes allows for an easy, production ready, container orchestration. For us that means deploying machine learning trainings easily on multiple nodes with multiple GPUs with automated configuration. Without such a solution, in typical company, even after obtaining access to machine(s) with GPU(s), one would have to manually take care of setting accessiblle nodes and/or GPUs and make sure his traning will not interfere with somebodys else. Kubernetes will take care of that for us. We just need to set the amount of needed GPUs for our traning and kubernetes will make sure to provide it.

## Usage options
Kubernetes is designed primarily for cloud usage, however it provides locally hosted options mainly for testing and development. It provides multiple solutions, a list of which can be found here - https://kubernetes.io/docs/setup/pick-right-solution/#local-machine-solutions. 
Even though kubeadm is proposed in Nvidia docs here - https://docs.nvidia.com/datacenter/kubernetes-install-guide/index.html we decided to use minikube as it didn't require adding additional machine acting as a master node. We run into a few problems with minikube and after trying a few solutions we decided to switch to microk8s. I turned out to be much better option for our purpose due to easier installation, configuration and unistallation (it wasn't that easy to clean everything after minikube).

## Installation
Docker (version <= 18.06) and Nvidia plugin installation (version > 2.0)

```
sudo apt-get install docker-ce=18.03.1~ce-0~ubuntu
sudo apt-get install nvidia-docker2=2.0.3+docker18.03.1-1 nvidia-container-runtime=2.0.0+docker18.03.1-1
sudo systemctl daemon-reload
sudo systemctl restart docker
```

Test nvidia-docker

`sudo docker run --runtime=nvidia --rm nvidia/cuda:9.0-base nvidia-smi`

Minikube installation. Normally minikube uses a virtual machine with docker inside. We chose to use docker from host not to add additional layer of abstraction.

```
sudo apt-get update && sudo apt-get install -y apt-transport-https
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl

curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 \
  && chmod +x minikube

sudo cp minikube /usr/local/bin && rm minikube
```

Allow kubernetes to use GPU (Nvidia driver must be ~> 361.93)

Set nvidia-docker as default runtime

In daemon.json which should be located in /etc/docker/ add:

"default-runtime": "nvidia",

Afterwards it should look something like this:

{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}

Starting kubernetes through minikube

`sudo minikube start --vm-driver=none`

When minikube tells us everything look all right we need to deploy nvidia plugin allowing to use GPUs on our node(s)

```
sudo kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v1.11/nvidia-device-plugin.yml
```

Restart docker and kubernetes:
```
sudo minikube stop
sudo service docker stop
sudo service docker start
sudo minikube start --vm-driver=none
```

Microk8s installation and configuration.

```
sudo snap install microk8s --classic
sudo microk8s.start
microk8s.kubectl get nodes
microk8s.enable gpu
sudo microk8s.stop
sudo microk8s.start
```

As shown microk8s is easier and require less configuration. There is also quite a lot of built in addons that can be turned on the same way as gpu one. Due to the usage of snap, unistallation is easier and there is no need to worry about leftovers. Micro8s also comes with its own kubectl so it won't after existing configuration if there is any but can be also aliased to be used with kubectl command. 

`sudo kubectl get nodes`
Should output available nodes

To see more info about a node pod or job use kubectl describe node/pod/job <name>

`sudo kubectl describe node minikube`
Somewhere in capactity it should show nvidia.com/gpu: x 
with x being number of available GPUs on our machine


If everything worked correctlly we should be able to create a pod using a yaml template. Download a Dockerfile and build an image from it first. After that download the template, fill in a correct image name and run it. To see a detailed instrucion on how to run an example see README in deepspeech directory. 

Template will create a traning job for Mozilla's Deepspeech using a single GPU.

To output availavle nodes or pods use kubectl get pod/node.
To see logs from a given node or pod use kubectl logs pod/node <name>.
To remove pod use kubectl delete pod <name>.
```
sudo kubectl logs pod <ds>
sudo kubectl describe pod <ds>
sudo kubectl delete pod <ds>
```



## Running single process learning
Template used above:
```
apiVersion: v1
kind: Pod
metadata:
  name: ds
spec:
  containers:
    - args:
      - python3
      - ./DeepSpeech.py
      - --train_files=ldc93s1/ldc93s1.csv
      - --dev_files=ldc93s1/ldc93s1.csv
      - --test_files=ldc93s1/ldc93s1.csv
      - --log_level=0
      - --train_batch_size=32
      - --benchmark_steps=30
      - --notest
      name: ds-container
      image: <yourdockerhub>/deepspeech
      env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
      resources:
        limits:
          nvidia.com/gpu: 1
  restartPolicy: Never
```

It provides a name for our pod, docker image source command with arguments to be run inside of the container, env variables and an amount of requested GPUs. 
Even though we passed two GPUs to CUDA_VISIBLE_DEVICES it will not be able to "cheat" kubernetes and still will only have access to one GPU that was requested.


## Running distributed learning
There are two ways of running distributed training using kubernetes: deploying one container which has access to multiple GPUs and has multiple processes running inside of it or deploying multiple containers - one for each gpu with only one process running.

## Experimental results

### Summary
Kubernetes can be very usefull in this age of containerization and cloud. It allows for an easy orchestration and automatization. However, it requires a lot of configuration besides that the whole ecosystem is quite new and in constant development which means things are changing fast! Its main focus is on cloud providers so local solutions are mainly for development and testing. Becuase of the fact how Docker handle cacheing development can be really slow. For example DeepSpeech's original Dockerfile contains building everything from scratch so after changing anything in code that can't be applied after this process rebuilding image takes hours. On top of that a popular option is to build and test images on different computer and that means uploading and downloading at least a few GB in case of rebuilding bigger layers.  

