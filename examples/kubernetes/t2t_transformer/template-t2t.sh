
#!/bin/bash
if [ -z $1 ]; then
    TBS=1024
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

echo `rm ds.yaml`
echo `touch ds.yaml`

cat <<EOT >> ds.yaml
apiVersion: v1
kind: Pod
metadata:
  name: t2t
spec:
  containers:
    - args:
      - t2t-trainer
      - --data_dir=/root/t2t_data
      - --problem=translate_ende_wmt32k
      - --model=transformer
      - --hparams_set=transformer_base_single_gpu
      - --output_dir=/root/t2t_train/translate_ende_wmt32k/transformer-transformer_base_single_gpu
      - --log_level=30
      - --benchmark_steps=30
      - --hparams='batch_size=$TBS'
      name: t2t-container
      image: piotrowskidariusz/tensor2tensor:old
      env:
        - name: CUDA_VISIBLE_DEVICES
          value: "$CVD"
      resources:
        limits:
          nvidia.com/gpu: $GPUS
  restartPolicy: Never   
EOT
echo `kubectl create -f ds.yaml`
