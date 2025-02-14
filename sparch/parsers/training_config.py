#
# SPDX-FileCopyrightText: Copyright © 2022 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Alexandre Bittar <abittar@idiap.ch>
#
# SPDX-License-Identifier: BSD-3-Clause
#
# This file is part of the sparch package
#
"""
This is where the parser for the training configuration is defined.
"""
import logging
from distutils.util import strtobool

logger = logging.getLogger(__name__)


def add_training_options(parser):
    parser.add_argument(
        "--sweep_name",
        type=str,
        default=None,
        help="Name for the sweep to run.",
    )
    parser.add_argument(
        "--sweep_id",
        type=str,
        default=None,
        help="Id of the current sweep to execute.",
    )
    parser.add_argument(
        "--debug",
        action='store_true',
        help="Trigger debug mode with no sweep on wandb use.",
    )
    parser.add_argument(
        "--gpu_device",
        type=int,
        #default=0,
        help="Which gpu device to use.",
    )
    parser.add_argument(
        "--seed",
        nargs="+",
        default = [13, 42, 73, 190, 268],
        type=int,
        help="Fix one or multiple seeds for the runs.",
    )
    parser.add_argument(
        "--use_pretrained_model",
        type=lambda x: bool(strtobool(str(x))),
        default=False,
        help="Whether to load a pretrained model or to create a new one.",
    )
    parser.add_argument(
        "--only_do_testing",
        type=lambda x: bool(strtobool(str(x))),
        default=False,
        help="If True, will skip training and only perform testing of the "
        "loaded model.",
    )
    parser.add_argument(
        "--load_exp_folder",
        type=str,
        default=None,
        help="Path to experiment folder with a pretrained model to load. Note "
        "that the same path will be used to store the current experiment.",
    )
    parser.add_argument(
        "--new_exp_folder",
        type=str,
        default=None,
        help="Path to output folder to store experiment.",
    )
    parser.add_argument(
        "--dataset_name",
        type=str,
        choices=["shd", "ssc", "hd", "sc"],
        default="shd",
        help="Dataset name (shd, ssc, hd or sc).",
    )
    parser.add_argument(
        "--data_folder",
        type=str,
        default="~/local/SHD",
        help="Path to dataset folder.",
    )
    parser.add_argument(
        "--log_tofile",
        type=lambda x: bool(strtobool(str(x))),
        default=False,
        help="Whether to print experiment log in an dedicated file or "
        "directly inside the terminal.",
    )
    parser.add_argument(
        "--save_best",
        type=lambda x: bool(strtobool(str(x))),
        default=True,
        help="If True, the model from the epoch with the highest validation "
        "accuracy is saved, if False, no model is saved.",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=128,
        help="Number of input examples inside a single batch.",
    )
    parser.add_argument(
        "--nb_steps",
        nargs="+",
        type=int,
        default=[100],
        help="Number of timesteps.",
    )
    parser.add_argument(
        "--max_time",
        nargs="+",
        type=float,
        default=[1.4],
        help="Max time for SHD samples.",
    )
    parser.add_argument(
        "--spatial_bin",
        nargs="+",
        type=int,
        default=[1],
        help="Spatial binning for SHD.",
    )
    parser.add_argument(
        "--time_offset",
        nargs="+",
        type=int,
        default=[0],
        help="Offset in # of timesteps to start counting loss.",
    )
    parser.add_argument(
        "--nb_epochs",
        type=int,
        default=100,
        help="Number of training epochs (i.e. passes through the dataset).",
    )
    parser.add_argument(
        "--start_epoch",
        type=int,
        default=0,
        help="Epoch number to start training at. Will be 0 if no pretrained "
        "model is given. First epoch will be start_epoch+1.",
    )
    parser.add_argument(
    "--method",
    choices=["grid", "bayes"],  # Restrict choices to grid or bayes
    default="grid",            # Optional: set a default if desired
    help="Choose between grid search or bayesian optimization for the sweep.",
    )

    parser.add_argument(
        "--lr",
        nargs="+",
        type=float,
        default=[1e-2],
        help="Initial learning rate for training. The default value of 0.01 "
        "is good for SHD and SC, but 0.001 seemed to work better for HD and SC.",
    )
    parser.add_argument(
        "--scheduler_patience",
        nargs='+',
        type=int,
        default=[10],
        help="Number of epochs without progress before the learning rate "
        "gets decreased.",
    )
    parser.add_argument(
        "--scheduler_factor",
        type=float,
        nargs='+',
        default=[0.7],
        help="Factor between 0 and 1 by which the learning rate gets "
        "decreased when the scheduler patience is reached.",
    )
    parser.add_argument(
        "--use_regularizers",
        type=lambda x: bool(strtobool(str(x))),
        default=False,
        help="Whether to use regularizers in order to constrain the "
        "firing rates of spiking neurons within a given range.",
    )
    parser.add_argument(
        "--reg_factor",
        type=float,
        default=0.5,
        help="Factor that scales the loss value from the regularizers.",
    )
    parser.add_argument(
        "--reg_fmin",
        type=float,
        default=0.01,
        help="Lowest firing frequency value of spiking neurons for which "
        "there is no regularization loss.",
    )
    parser.add_argument(
        "--reg_fmax",
        type=float,
        default=0.5,
        help="Highest firing frequency value of spiking neurons for which "
        "there is no regularization loss.",
    )
    parser.add_argument(
        "--use_augm",
        type=lambda x: bool(strtobool(str(x))),
        default=False,
        help="Whether to use data augmentation or not. Only implemented for "
        "nonspiking HD and SC datasets.",
    )
    return parser


def print_training_options(config):
    logging.info(
        """
        Training Config
        ---------------
        Debug run: {debug}
        Use pretrained model: {use_pretrained_model}
        Only do testing: {only_do_testing}
        Load experiment folder: {load_exp_folder}
        New experiment folder: {new_exp_folder}
        Dataset name: {dataset_name}
        Data folder: {data_folder}
        Log to file: {log_tofile}
        Save best model: {save_best}
        Batch size: {batch_size}
        Number of epochs: {nb_epochs}
        Start epoch: {start_epoch}
        Initial learning rate: {lr}
        Scheduler patience: {scheduler_patience}
        Scheduler factor: {scheduler_factor}
        Use regularizers: {use_regularizers}
        Regularization factor: {reg_factor}
        Regularization min firing rate: {reg_fmin}
        Reguarization max firing rate: {reg_fmax}
        Use data augmentation: {use_augm}
        Seed {seed}
    """.format(
            **config
        )
    )
