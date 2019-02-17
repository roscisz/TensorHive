## Table of contents
- [x] [Why Kubernetes](#why-kubernetes)
- [x] [Usage options](#usage-options)
- [x] [Minikube Installation](#minikube-installation)
- [x] [Microk8s installation and configuration](#microk8s-installation-and-configuration)
- [x] [Running single process learning](#running-single-process-learning)
- [x] [Running distributed learning](#running-distributed-learning)
- [x] [Summary](#summary)
- [ ] [Experimental results](#experimental-results)




## Why Kubernetes
Kubernetes allows for an easy, production-ready, container orchestration. It helps in deployment of machine learning trainings on multiple nodes with many GPUs and automating its configuration.

In most companies that are not using any solution of that kind, one would need to **manually**:

* obtain access to all machines having particular GPUs
* make sure not to interrupt somebody else's training
* configure `CUDA_VISIBLE_DEVICES` on each machine
* make training command adjustments and launch it everywhere

Kubernetes will take care of all this for us. We just need to set the amount of GPUs needed for our traning and it will make sure to provide it

## Usage options
Kubernetes is designed primarily for cloud use cases, however it also provides [multiple options to run locally](https://kubernetes.io/docs/setup/pick-right-solution/#local-machine-solutions) (essential for development and testing purposes)

We decided to try `minikube` first instead of `kubeadm` ([proposed in Nvidia docs here](https://docs.nvidia.com/datacenter/kubernetes-install-guide/index.html)) because it would require an additional machine acting as a master node.

Then we run into a few problems with `minikube`: blocked port, broken certificates, new configuration not being picked up, some of the containers not running correctly, files and folders being created in different locations and no simple way to remove it.
After trying a few other solutions we switched to `microk8s`, which turned out to be much easier to install, configure and remove.

## Minikube Installation

### Prerequisites
* Docker (version <= 18.06)
* Nvidia plugin installation (version > 2.0)

```
sudo apt-get install docker-ce=18.03.1~ce-0~ubuntu
sudo apt-get install nvidia-docker2=2.0.3+docker18.03.1-1 nvidia-container-runtime=2.0.0+docker18.03.1-1
sudo systemctl daemon-reload
sudo systemctl restart docker
```

Test nvidia-docker

`sudo docker run --runtime=nvidia --rm nvidia/cuda:9.0-base nvidia-smi`

### Minikube
Normally `minikube` uses a virtual machine with Docker inside. We chose to use Docker provided directly by the host instead, so we don't build additional layer of abstraction.

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

Allow kubernetes to use GPU by setting `nvidia-docker` as default runtime (**Nvidia driver must be ~> 361.93**)

Overwrite `daemon.json` under `/etc/docker/add`:

```
"default-runtime": "nvidia",
```
with:

```
{  
    "default-runtime": "nvidia",
    "runtimes": {  
        "nvidia": {  
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
```

Starting kubernetes through minikube

`sudo minikube start --vm-driver=none`

When minikube tells us that everything looks all right , we need to deploy `nvidia-device-plugin` which will allow to use GPUs on our node(s).

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

## Microk8s installation and configuration


```
sudo snap install microk8s --classic
sudo microk8s.start
microk8s.kubectl get nodes
microk8s.enable gpu
sudo microk8s.stop
sudo microk8s.start
```
As shown above, `microk8s` is easier and requires much less configuration. There is also quite a lot of built-in add-ons that can be turned on the same way as the GPU one.

Because `microk8s` is distributed as `snap` package, removal process is trivial and there is no need to worry about leftovers.
Micro8s also comes with its own `kubectl` so it won't interfere with existing configuration (though it can be aliased to be used via `kubectl` command).

To see available nodes:
`sudo kubectl get nodes`

To see more info about a node, pod or job:
`sudo kubectl describe node/pod/job <name>`
Example:
`sudo kubectl describe node minikube`
Somewhere in `capactity` it should output `nvidia.com/gpu: X` with X being number of available GPUs on this machine.

If everything worked correctly, now we should be able to create a pod using yaml template file from one of our examples:

1. Download `Dockerfile` and build image from it
2. Download template `sh` script, optionally adjust image name (`image:`) and run it.

### Running training examples
To see more detailed instructions on how to run specific training example check out [DeepSpeech README](https://github.com/roscisz/TensorHive/tree/kubernetes/examples/kubernetes/deepspeech) and [T2T README](https://github.com/roscisz/TensorHive/tree/kubernetes/examples/kubernetes/t2t_transformer)

<This should probably go directly into that single, specific README>
Template will create a training job for Mozilla's Deepspeech using a single GPU.

Commands to try out:

```
# Replace <name> with: 
# - ds (DeepSpeech)
# - t2t (T2T)
sudo kubectl get pod<name>
sudo kubectl logs pod <name>
sudo kubectl describe pod <name>
sudo kubectl delete pod <name>
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
Kubernetes can be very useful in this age of containerization and cloud. However, it requires a significant amount of time and effort to configure on each machine. This whole ecosystem is quite new, under constant development which results in frequent changes and backward compatibility issues.

It's meant to be used by cloud providers, so local solutions are mainly restricted to development and testing.
Additionally, considering how Docker handles layer caching, development can be really slow. For example DeepSpeech's original Dockerfile rebuilds everything from scratch when the code changes and that whole process can takes hours.
An alternative way is to build and test images on different computers, but it leads to uploading and downloading at least a few GB in case of rebuilding **bigger / heavier** layers.

