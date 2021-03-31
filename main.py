# -*- coding: utf-8 -*-
import os
import random

import numpy as np
import torch
from torch.backends import cudnn

from option import get_option
from trainers import trainer_factory
from utils.trainer_utils import save_option, initialize_logger
import logging
from datasets import dataloader_factory
import json
from experiments.celebA_experiments import *
from experiments.biased_mnist_experiments import *
from experiments.gqa_experiments import *


def backend_setting(option):
    # Initialize the expt_dir where all the results (predictions, checkpoints, logs, metrics) will be saved
    if option.expt_dir is None:
        option.expt_dir = os.path.join(option.save_dir, option.expt_name)

    if not os.path.exists(option.expt_dir):
        os.makedirs(option.expt_dir)

    # Configure the logger
    initialize_logger(option.expt_dir)

    # Set the random seeds
    if option.random_seed is None:
        option.random_seed = random.randint(1, 10000)
    random.seed(option.random_seed)
    torch.manual_seed(option.random_seed)
    torch.cuda.manual_seed_all(option.random_seed)
    np.random.seed(option.random_seed)

    if torch.cuda.is_available() and not option.cuda:
        logging.warn('GPU is available, but we are not using it!!!')

    if not torch.cuda.is_available() and option.cuda:
        option.cuda = False

    # Dataset specific settings
    set_if_null(option, 'bias_loss_gamma', 0.7)
    set_if_null(option, 'bias_ema_gamma', 0.7)


def set_if_null(option, attr_name, val):
    if not hasattr(option, attr_name) or getattr(option, attr_name) is None:
        setattr(option, attr_name, val)


def configure_biased_mnist(option):
    set_if_null(option, 'optimizer_name', 'Adam')
    set_if_null(option, 'batch_size', 128)
    # option.num_bias_classes = 2
    option.num_classes = 10
    # option.bias_variable_dims = 2
    set_if_null(option, 'lr', 1e-4)
    set_if_null(option, 'epochs', 30)
    set_if_null(option, 'bias_model_hid_dims', 64)
    set_if_null(option, 'model_name', 'BiasedMNISTCNN')
    option.dataset_name = 'biased_mnist'
    option.data_dir = option.root_dir + f"/{option.dataset_name}"
    set_if_null(option, 'bias_model_name', 'MLP2')
    set_if_null(option, 'bias_variable_type', 'categorical')
    set_if_null(option, 'num_envs_per_batch', 16)

    feature_dims = {
        'conv1': 32,
        'conv2': 32,
        'pooled2': 32,
        'conv3': 64,
        'conv4': 64,
        'conv5': 64,
        'pooled5': 128,
        'logits': option.num_classes
    }
    set_if_null(option, 'bias_predictor_name', 'MLP2')
    set_if_null(option, 'bias_predictor_in_layer', 'pooled2')

    option.bias_predictor_in_dims = feature_dims[option.bias_predictor_in_layer]
    option.bias_predictor_hid_dims = feature_dims[option.bias_predictor_in_layer]


def main():
    option = get_option()
    if option.project_name is None:
        option.project_name = option.dataset_name
    if option.expt_type is not None:
        eval(option.expt_type)(option, run)
    else:
        run(option)


def run(option):
    backend_setting(option)
    # neptune.create_experiment(name=option.trainer_name + "_" + option.expt_name,
    #                           params=option.__dict__)
    # neptune.append_tag(option.trainer_name + "_" + option.expt_name)
    data_loaders = dataloader_factory.build_dataloaders(option)
    if 'gqa' in option.dataset_name.lower():
        option.bias_variable_dims = option.num_groups
        option.num_bias_classes = option.num_groups

    save_option(option)
    logging.getLogger().info(json.dumps(option.__dict__, indent=4, sort_keys=True,
                                        default=lambda o: f"<<non-serializable: {type(o).__qualname__}>>"))

    trainer = trainer_factory.build_trainer(option)
    trainer.train(data_loaders['Train'], data_loaders['Test'], data_loaders['Unbalanced Train'])


if __name__ == '__main__':
    main()