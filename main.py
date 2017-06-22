import argparse
import pickle
import time

import colocation
import p_clique_extraction
import traces
from utils import grouper

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Urban-Tribes identification')
    parser.add_argument('-g', '--social_graph_path', help='Name of file containing social graph', dest='social_graph_path', required=True,action='store_true' )
    parsed_args = parser.parse_args()


    social_graph , p_clique_dataset, unique_users = p_clique_extraction.find_p_cliques(parsed_args.social_graph_path)
    users_trace_dict = traces.load_and_process('data/user-trace.csv', unique_users, 30 * 60)

    p_clique_per_file = 500
    for i, p_clique_group in enumerate(grouper(sorted(p_clique_dataset, key=lambda p_c: len(p_c)), p_clique_per_file)):
        data_list = []
        s_time = time.time()
        for p_clique in p_clique_group:
            cell_coloc, area_coloc = colocation.compute(p_clique, users_trace_dict)
            data_list.append({
                'members': set(p_clique),
                'cell_coloc': cell_coloc,
                'area_coloc': area_coloc
            })
        pickle.dump(obj=data_list, file=open('data/p_clique_coloc_' + "{:06d}".format(i) + '.pkl', 'wb'))
        print('Done', i, 'elapsed time', time.time() - s_time)