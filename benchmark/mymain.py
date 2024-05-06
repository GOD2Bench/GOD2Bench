import tqdm
import torch
import argparse
import warnings
import sys, os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from GAOOD.metric import *
from utils import init_model
from dataloader.data_loader import *
'''
python benchmark/mymain.py -exp_type oodd -DS_pair BZR+COX2 -num_epoch 400 -num_cluster 2 -alpha 0
oodd（两个数据集OOD），ood:是GOOD/Drugood，ad :异常检测（tox/TU）
model：模型名字
DS_pair BZR+COX2  对应两个数据集的OOD
Ds, 剩下两个，ood和ad
超参

'''
def main(args):
    auc, ap, rec = [], [], []
    print(args)
    for _ in tqdm.tqdm(range(args.num_trial)):
        if args.exp_type == 'ad' and args.DS.startswith('Tox21'): 
               data_train,data_val, data_test, dataloader,dataloader_val, dataloader_test, meta = get_ad_dataset_Tox21(args)
            # else:
            #     splits = get_ad_split_TU(args, fold=args.num_trial)
        elif args.exp_type == 'oodd':
            print("-------")
            print(args.exp_type)
            data_train,data_val, data_test, dataloader,dataloader_val, dataloader_test, meta = get_ood_dataset(args)
            
        elif args.exp_type == 'ad' and not args.DS.startswith('Tox21'):
            splits = get_ad_split_TU(args, fold=args.num_trial)
            data_train,data_val, data_test, dataloader,dataloader_val, dataloader_test, meta = get_ad_dataset_TU(args, splits[_])
            
        elif args.exp_type == 'ood':
            print("-------")
            print(args.exp_type)
            data_train,data_val, data_test, dataloader,dataloader_val, dataloader_test, meta = get_ood_dataset_spilt(args)

        args.max_nodes_num = meta['max_nodes_num']
        args.dataset_num_features = meta['num_feat']
        args.n_train =  meta['num_train']
        args.n_edge_feat = meta['num_edge_feat']
        
        # args.dataset_num_features = meta['num_feat']
        # args.n_train =  meta['num_train']
        # args.max_nodes_num = meta['max_nodes_num']

        model = init_model(args)
        ###如果要自定义dataloader,就把dataset传进去，dataloader=None,否则按下面的来即可
        
        if args.model == 'GOOD-D':
            print(args.model)
            model.fit(dataset=dataset_train, args=args, label=None, dataloader=dataloader, dataloader_val=dataloader_val)
        elif args.model == 'GraphDE':
            print(args.model)
            model.fit(dataset=dataset_train, args=args, label=None, dataloader=dataloader, dataloader_val=dataloader_val)
        elif args.model == 'GLocalKD':
            print(args.model)
            model.fit(dataset=dataset_train, args=args, label=None, dataloader=dataloader, dataloader_val=dataloader_val)
        elif args.model == 'GLADC':
            print(args.model)
            model.fit(dataset=dataset_train, args=args, label=None, dataloader=dataloader, dataloader_val=dataloader_val)
        elif args.model == 'SIGNET':
            print(args.model)
            model.fit(dataset=dataset_train, args=args, label=None, dataloader=dataloader, dataloader_val=dataloader_val)

        else:
            model.fit(dataset_train)

        score, y_all = model.predict(dataset=dataset_test, dataloader=dataloader_test, args=args, return_score=False)


        # print(score)
        # print(y_all)

        
        auc.append(ood_auc(y_all,score))
        print(auc)
        #auc.append(eval_roc_auc(y, score))
        #ap.append(eval_average_precision(y, score))
        #rec.append(eval_recall_at_k(y, score, k))

    auc = torch.tensor(auc)
    #ap = torch.tensor(ap)
    #rec = torch.tensor(rec)
    print(auc)
    '''
    print(args.dataset + " " + model.__class__.__name__ + " " +
          "AUC: {:.4f}±{:.4f} ({:.4f})\t"
          "AP: {:.4f}±{:.4f} ({:.4f})\t"
          "Recall: {:.4f}±{:.4f} ({:.4f})".format(torch.mean(auc),
                                                  torch.std(auc),
                                                  torch.max(auc),
                                                  torch.mean(ap),
                                                  torch.std(ap),
                                                  torch.max(ap),
                                                  torch.mean(rec),
                                                  torch.std(rec),
                                                  torch.max(rec)))
    '''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="GLADC",
                        help="supported model: [GLocalKD, GLADC, SIGNET, GOOD-D, GraphDE]."
                             "Default: GLADC")
    parser.add_argument("--gpu", type=int, default=0,
                        help="GPU Index. Default: -1, using CPU.")
    parser.add_argument("--dataset", type=str, default='inj_cora',
                        help="supported dataset: [inj_cora, inj_amazon, "
                             "inj_flickr, weibo, reddit, disney, books, "
                             "enron]. Default: inj_cora")
    
    parser.add_argument('-exp_type', type=str, default='ad', choices=['oodd', 'ad','ood'])
    parser.add_argument('-DS', help='Dataset', default='BZR') 
    #BZR, DHFR
    #(BZR, COX2), (ogbg-moltox21,ogbg-molsider)
    #Tox21_PPAR-gamma
    parser.add_argument('-DS_ood', help='Dataset', default='ogbg-molsider')
    parser.add_argument('-DS_pair', default=None)
    parser.add_argument('-rw_dim', type=int, default=16)
    parser.add_argument('-dg_dim', type=int, default=16)
    parser.add_argument('-batch_size', type=int, default=128)
    parser.add_argument('-batch_size_test', type=int, default=9999)
    parser.add_argument('-lr', type=float, default=0.0001)
    parser.add_argument('-num_layer', type=int, default=5)
    parser.add_argument('-hidden_dim', type=int, default=16)
    parser.add_argument('-num_trial', type=int, default=5)
    parser.add_argument('-num_epoch', type=int, default=400)
    parser.add_argument('-eval_freq', type=int, default=10)
    parser.add_argument('-is_adaptive', type=int, default=1)
    parser.add_argument('-num_cluster', type=int, default=2)
    parser.add_argument('-alpha', type=float, default=0)
    parser.add_argument('-n_train', type=int, default=10)


    '''
    GLocalKD
    '''
    parser.add_argument('--max-nodes', dest='max_nodes', type=int, default=0,
                        help='Maximum number of nodes (ignore graghs with nodes exceeding the number.')
    parser.add_argument('--clip', dest='clip', default=0.1, type=float, help='Gradient clipping.')
    # parser.add_argument('--num_epochs', dest='num_epochs', default=150, type=int, help='total epoch number')
    parser.add_argument('--batch-size', dest='batch_size', default=300, type=int, help='Batch size.')
    parser.add_argument('--hidden-dim', dest='hidden_dim', default=512, type=int, help='Hidden dimension')
    parser.add_argument('--output-dim', dest='output_dim', default=256, type=int, help='Output dimension')
    parser.add_argument('--num-gc-layers', dest='num_gc_layers', default=3, type=int,
                        help='Number of graph convolution layers before each pooling')
    parser.add_argument('--nobn', dest='bn', action='store_const', const=False, default=True,
                        help='Whether batch normalization is used')
    parser.add_argument('--dropout', dest='dropout', default=0.3, type=float, help='Dropout rate.')
    parser.add_argument('--nobias', dest='bias', action='store_const', const=False, default=True,
                        help='Whether to add bias. Default to True.')

    '''
    GLADC parameter
    '''
    parser.add_argument('--max-nodes', dest='max_nodes', type=int, default=0,
                        help='Maximum number of nodes (ignore graghs with nodes exceeding the number.')
    parser.add_argument('--dropout', dest='dropout', default=0.1, type=float, help='Dropout rate.')
    parser.add_argument('--output-dim', dest='output_dim', default=128, type=int, help='Output dimension')
    '''
    SIGNET parameter
    '''
    # parser.add_argument('--log_interval', type=int, default=1)
    parser.add_argument('--encoder_layers', type=int, default=5)
    parser.add_argument('--pooling', type=str, default='add', choices=['add', 'max'])
    parser.add_argument('--readout', type=str, default='concat', choices=['concat', 'add', 'last'])
    parser.add_argument('--explainer_model', type=str, default='gin', choices=['mlp', 'gin'])
    parser.add_argument('--explainer_layers', type=int, default=5)
    parser.add_argument('--explainer_hidden_dim', type=int, default=8)
    parser.add_argument('--explainer_readout', type=str, default='add', choices=['concat', 'add', 'last'])
 
    args = parser.parse_args()

    # global setting
    num_trial = 5

    main(args)
