import os,sys
import argparse
from model.models import PartialDeepSeaModel, NNClassifier
from model import train
import torch


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('data_name')
    parser.add_argument('model_name')
    parser.add_argument('model_dir')
    parser.add_argument('-d', '--distance', action='store_true', default=False)

    return parser.parse_args()


if __name__=='__main__':
    args = get_args()
    legacy = True

    deepsea_model = PartialDeepSeaModel(4, use_weightsum=True, leaky=True, use_sigmoid=args.sigmoid)
    n_filters = deepsea_model.num_filters[-1]*4
    if args.distance:
        n_filters += 1
    classifier = NNClassifier(n_filters, legacy=legacy)

    train.test(deepsea_model, classifier, args.model_name, args.data_name, False, data_set='test',
               save_probs=True, use_distance=False, model_dir=args.model_dir, legacy=legacy)
