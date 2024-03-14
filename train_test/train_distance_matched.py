import os,sys
import torch
import argparse
from model.models import PartialDeepSeaModel, NNClassifier
from model import train


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('data_name')
    parser.add_argument('model_name')
    parser.add_argument('model_dir')
    parser.add_argument('-e', '--epochs', type=int, default=40,
                        help='Number of epochs for training. Default: 40')
    parser.add_argument('-d', '--distance', action='store_true', default=False)

    return parser.parse_args()


if __name__=='__main__':
    args = get_args()
    legacy = True
    data_name = args.data_name
    model_name = args.model_name

    deepsea_model = PartialDeepSeaModel(4, use_weightsum=True, leaky=True, use_sigmoid=args.sigmoid)
    n_filters = deepsea_model.num_filters[-1]*4
    if args.distance:
        n_filters += 1
    classifier = NNClassifier(n_filters, legacy=legacy)

    deepsea_model = PartialDeepSeaModel(4, use_weightsum=True, leaky=True, use_sigmoid=args.sigmoid)
    classifier = NNClassifier(n_filters, legacy=legacy)
    train.train(model=deepsea_model, classifier=classifier, init_lr=0.0001, epochs=args.epochs,
                data_pre=data_name, model_name=model_name, retraining=True,
                use_weight_for_training=None, use_distance=args.distance,
                model_dir=args.model_dir, legacy=legacy)
