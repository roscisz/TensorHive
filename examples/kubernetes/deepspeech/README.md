## Running example
To build docker image using provided Dockerfile run
`docker build -t <yourdockerhub>/deepspeech .`
while in directory with Dockerfile.
Afterwards to push image to dockerhub (no need if it's been built on the same machine it will be tested later on)
`docker push <yourdockerhub>/deepspeech`
To run example change image docker name in ds.yaml for a correct one and run
`sudo kubectl create -f ds.yaml`
```
sudo kubectl get pod //see current pods
sudo kubectl describe pod ds //check pod specification
sudo kubectl logs ds //check logs from pod
```


## Configuring GPUs
Unfortunately kubernetes doesn't take into account other process using GPUs which leads to out-of-memory errors if somebody else runs their trening manually. Because CUDA_VISIBLE_DEVICES env variable is used inside the container it can only chose from GPUs kubernetes assigns to the container. So if we would like to deploy our training to GPU number 3 we would have to set GPUs limit to 4 and set CVD to "3". That is if the GPUs are on a single node. If they would be on different ones we could use [node labels and selectors](https://kubernetes.io/docs/tasks/configure-pod-container/assign-pods-nodes/).

## Benchmarking results
After running benchmarks on same commit and envoirment as natively we got very simlliar results which means docker is not adding any overhead (the results may vary a bit due to small variables as temperature of the machine and/or in the room). A significant advantage of Kubernetes is a possibility to just schedule all of the test jobs at once and Kubernetes will deal with running them on free GPUs whenever possible. However while we where testing it we found out that running benchmark on one GPU is noticeably faster if other GPUs are free.