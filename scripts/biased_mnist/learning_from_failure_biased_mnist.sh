#!/bin/bash
source common.sh
set -e
source activate bias_mitigator

TRAINER_NAME='LffTrainer'

for bias_loss_gamma in 0.3; do
  python main.py \
  --expt_type biased_mnist_experiments \
  --lr 1e-4 \
  --weight_decay 1e-3 \
  --trainer_name ${TRAINER_NAME} \
  --optimizer_name Adam \
  --bias_loss_gamma ${bias_loss_gamma} \
  --root_dir ${ROOT}
done