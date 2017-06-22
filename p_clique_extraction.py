import subprocess
import networkx as nx
import functools

PCE_PATH = './pce/pce'
PCE_INPUT_PATH = 'tmp/pce_input.csv'
REVERSE_ID_PATH = 'tmp/reverse_id.csv'
FOUND_P_CLIQUE_PATH = 'tmp/found_q_clique.out'

def _prepare_pce_input_files(graph, realId_to_pceId_map, pceId_to_realId_map):
    with open(PCE_INPUT_PATH,'w') as out_file , open(REVERSE_ID_PATH, 'w') as reverse_id_out_file :
        for node in sorted(graph.nodes()):
            reverse_id_out_file.write(str(node))
            line_to_write = ','.join([str(realId_to_pceId_map[neighbor]) for neighbor in nx.all_neighbors(graph, node) ])
            out_file.write(line_to_write+'\n')
            reverse_id_out_file.write('\n')
            
def _exec_pce(graph, p_clique_min_size, p_clique_max_size, t_density):
    run_args = [ PCE_PATH, '%M', '-l', str(p_clique_min_size), '-u', str(p_clique_max_size), \
            '-Q', REVERSE_ID_PATH , PCE_INPUT_PATH , str(t_density), FOUND_P_CLIQUE_PATH]
    
    print('PCE algorithm execution', run_args)
    
    return_code = subprocess.run(run_args).returncode
    print('return code', return_code)
    
    return _remove_disconnected(graph)
     
    
    
def _remove_disconnected(graph):
    p_clique_list = []
    with open(FOUND_P_CLIQUE_PATH,'r') as p_clique_file: 
        analyzed = 0
        accepted = 0
        for line in p_clique_file:
            if analyzed %50000 == 0:
                print('Analyzed', analyzed, accepted)
            cur_qclique = [ int(n) for n in line.split()]
            if nx.is_connected(graph.subgraph(cur_qclique)):
                p_clique_list.append(cur_qclique)
                accepted = accepted +1
            analyzed =  analyzed +1
    
    return p_clique_list

def _prune_and_convert_to_str_id(p_clique_subgraph, member_min_degree):
    return "-".join([ str(n) for n in sorted([ n[0] for n in  p_clique_subgraph.degree().items() if n[1] >= member_min_degree ]) ])


def _prune_and_collapse_p_clique(p_cliques, graph , member_min_degree):
    pruned_p_cliques = [ _prune_and_convert_to_str_id(graph.subgraph(p_c), member_min_degree) for p_c in p_cliques ]
    pruned_p_cliques = set(pruned_p_cliques) #collapse
    return [ [ int(m) for m in p_c_str_id.split('-') ]  for p_c_str_id in pruned_p_cliques  ]
        

    
def _remove_self_loop(graph):
    for e in [ e for e in graph.edges_iter() if e[0]==e[1] ]:
        graph.remove_edge(*e[:2])

    return graph
    
def find_p_cliques(graph_filepath, 
            p_clique_min_size = 5, 
            p_clique_max_size = 20, 
            t_density = 0.8, 
            member_min_degree = 1):
    
    
    graph = _remove_self_loop(nx.read_gpickle(graph_filepath))
    
    realId_to_pceId_map = dict(zip(sorted(graph.nodes()), range(0,graph.number_of_nodes())))
    pceId_to_realId_map = dict(map( lambda a:[a[1],a[0]], realId_to_pceId_map.items() ))
    
    _prepare_pce_input_files(graph, realId_to_pceId_map, pceId_to_realId_map)
    p_cliques = _exec_pce(graph, p_clique_min_size, p_clique_max_size, t_density)
    if member_min_degree > 1:
        p_cliques = _prune_and_collapse_p_clique(p_cliques, graph, member_min_degree)
    
    unique_users = unique_users = functools.reduce(lambda x,y: x.union(y) ,[ set(c) for c in p_cliques])
    
    return (graph , p_cliques, unique_users)
    
    
