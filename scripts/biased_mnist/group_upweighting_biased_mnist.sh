#!/bin/bash
source common.sh
set -e
source activate bias_mitigator

TRAINER_NAME='GroupUpweightingTrainer'

CUDA_VISIBLE_DEVICES=0 python main.py \
--expt_type biased_mnist_experiments \
--trainer_name ${TRAINER_NAME} \
--lr 1e-3 \
--weight_decay 0.1 \
--root_dir ${ROOT}