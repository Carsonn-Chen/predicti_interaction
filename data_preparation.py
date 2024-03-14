import os,sys
import argparse
from model import variables
from model.data_preparation_helper import get_and_save_data, load_pairs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--min_size', type=int, required=True, help='anchor最小尺寸')
    parser.add_argument('-e', '--ext_size', type=int, required=False, help='anchor拓展尺寸')
    parser.add_argument('-n', '--name', type=str, required=True, help='数据集')
    parser.add_argument('-g', '--genome', required=True, help='参考基因组')
    parser.add_argument('-o', '--out_dir', type=str, required=True, help='输出位置')
    parser.add_argument('--pos_files', nargs='*', default=[], help='正样本')
    parser.add_argument('--neg_files', nargs='*', default=[], help='负样本')
    parser.add_argument('-t', '--all_test', action='store_true', default=False, help='输出全部数据')
    parser.add_argument('--out_test_only', action='store_true', default=False, help='只输出测试集')
    parser.add_argument('--no_test', action='store_true', default=False, help='只输出训练集和验证集')
    args = parser.parse_args()
    min_size = args.min_size
    
    variables.init(args.genome)
    name = args.name

    if len(args.pos_files) <= 0 and len(args.neg_files) <= 0:
        print('Nothing to do')
        sys.exit(0)
    dataset_names = ['train', 'valid', 'test']
    train_pairs, train_labels, val_pairs, val_labels, test_pairs, test_labels = load_pairs(args.pos_files,
                                                                                           args.neg_files,
                                                                                           variables.hg38)
    data_pairs = [train_pairs, val_pairs, test_pairs]
    data_labels = [train_labels, val_labels, test_labels]
    out_idxes = []
    if args.all_test:
        pairs = train_pairs + val_pairs + test_pairs
        labels = train_labels + val_labels + test_labels
        fn = os.path.join(args.out_dir, '{}_test.hdf5'.format(name))
        print(fn)
        get_and_save_data(pairs, labels, fn, min_size, ext_size=args.ext_size)
    elif args.out_test_only:
        out_idxes.append(2)
    elif args.no_test:
        out_idxes += [0, 1]
    else:
        out_idxes = [0, 1, 2]

    for idx in out_idxes:
        pairs = data_pairs[idx]
        labels = data_labels[idx]
        dset = dataset_names[idx]
        fn = os.path.join(args.out_dir,
                          "{}_singleton_tf_with_random_neg_seq_data_length_filtered_{}.hdf5".format(name, dset))
        print(fn)
        get_and_save_data(pairs, labels, fn, min_size, ext_size=args.ext_size)
