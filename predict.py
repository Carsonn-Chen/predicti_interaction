import torch
import argparse
import h5py
import numpy as np
import xgboost as xgb
from sklearn.externals import joblib
from model.models import PartialDeepSeaModel
from model import train


def get_args():
    parser = argparse.ArgumentParser('')
    parser.add_argument('-m', '--model_file', type=str, required=True, help='数据集')
    parser.add_argument('-c', '--classifier_file', type=str, required=True, help='分类器')
    parser.add_argument('--data_file', required=True, help='文件')
    parser.add_argument('--output_pre', required=True, help='输出位置')
    parser.add_argument('-d', '--use_distance', action='store_true', default=False, help='使用距离')
    args = parser.parse_args()
    return args

if __name__=='__main__':
    args = get_args()
    model = PartialDeepSeaModel(4, use_weightsum=True, leaky=True, use_sigmoid=args.sigmoid)
    model.load_state_dict(torch.load(args.model_file))
    model.cuda()
    model.eval()
    classifier = joblib.load(args.classifier_file)
    (train_data, train_left_data, train_right_data,
     train_left_edges, train_right_edges,
     train_labels, train_dists) = train.load_hdf5_data(args.data_file)
    pairs = train_data['pairs'][:]
    probs = np.zeros(len(pairs))

    if args.store_factor_outputs:
        data_store = h5py.File(args.output_pre + '_factor_outputs.hdf5', 'w')
        left_data_store = data_store.create_dataset('left_out', (len(train_labels), model.num_filters[-1] * 2),
                                                    dtype='float32',
                                                    chunks=True, compression='gzip')
        right_data_store = data_store.create_dataset('right_out', (len(train_labels), model.num_filters[-1] * 2),
                                                     dtype='float32',
                                                     chunks=True, compression='gzip')
        dist_data_store = data_store.create_dataset('dists', data=train_dists, dtype='float32',
                                                    chunks=True, compression='gzip')

        pair_dtype = ','.join('uint8,u8,u8,uint8,u8,u8,u8'.split(',') + ['uint8'] * (len(pairs[0]) - 7))
        pair_data_store = data_store.create_dataset('pairs', data=np.array(pairs, dtype=pair_dtype), chunks=True,
                                                    compression='gzip')
        labels_data_store = data_store.create_dataset('labels', data=train_labels, dtype='uint8')

    i = 0
    last_print = 0
    while i < len(train_left_edges) - 1:
        end, left_out, right_out, _, _ = train.compute_factor_output(train_left_data, train_left_edges,
                                                                     train_right_data,
                                                                     train_right_edges,
                                                                     train_dists, train_labels, i,
                                                                     evaluation=True, factor_model=model,
                                                                     max_size=1000, same=args.same, legacy=args.legacy)
        left_out = left_out.data.cpu().numpy()
        right_out = right_out.data.cpu().numpy()
        if args.use_distance:
            curr_dists = np.array(train_dists[i:end])
            curr_dists = curr_dists[:, [0]]
            input_for_classifier = np.concatenate([left_out, right_out, curr_dists], axis=1)
        else:
            input_for_classifier = np.concatenate([left_out, right_out], axis=1)
        probs[i:end] = classifier.predict(xgb.DMatrix(input_for_classifier), ntree_limit=classifier.best_ntree_limit)
        if args.store_factor_outputs:
            left_data_store[i:end] = left_out
            right_data_store[i:end] = right_out
        if end - last_print > 5000:
            last_print = end
            print('generating input : %d / %d. With %d >= 0.5 so far' % (end, len(train_labels), sum(probs[:end]>=0.5)))
        i = end
    if args.store_factor_outputs:
        data_store.close()

    with open(args.output_pre + '_probs.txt', 'w') as out:
        for pair, prob in zip(pairs, probs):
            pair_str = [str(p) for p in pair] + [str(prob)]
            for i in [0,3]:
                if pair_str[i] == '23':
                    pair_str[i] = 'chrX'
                else:
                    pair_str[i] = 'chr' + pair_str[i]
            out.write('\t'.join(pair_str) + '\n')



