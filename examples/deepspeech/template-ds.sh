
#!/bin/bash
if [ -z $1 ]; then
    TBS=2
else
    TBS=$1
fi

if [ -z $2 ]; then
    CVD='0'
else
    CVD=$2
fi

if [ -z $3 ]; then
    GPUS=1
else
    GPUS=$3
fi

echo `rm t2t.yaml`
echo `touch ds.yaml`

cat <<EOT >> ds.yaml
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
      - --train_batch_size=$TBS
      - --benchmark_steps=30
      - --notest
      name: ds-container
      image: <yourdockerhub>/deepspeech
      env:
        - name: CUDA_VISIBLE_DEVICES
          value: "$CVD"
      resources:
        limits:
          nvidia.com/gpu: $GPUS
  restartPolicy: Never
EOT
echo `kubectl create -f ds.yaml`
