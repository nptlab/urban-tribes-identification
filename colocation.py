import itertools
import functools
import collections
import math

_TICK_SIZE = 60 #in seconds

#expand intevarl using one minute tick
def _interval_expand(start_sec, end_sec, user_id ): 
    start_sec = start_sec - (start_sec % _TICK_SIZE)
    end_sec = end_sec - (end_sec % _TICK_SIZE)
    return itertools.zip_longest(range(start_sec,end_sec+1,_TICK_SIZE), [user_id] , fillvalue= user_id )


def _trace_expansion(intervals_trace, user_id):
    return itertools.chain.from_iterable([ _interval_expand( i[0],i[1], user_id ) for i in intervals_trace ]) 


def _find_colocation_tick(expanded_traces, min_members ): 
    coloc_dict = collections.defaultdict(set)
    for minute, user in expanded_traces:
        coloc_dict[minute].add(user)
    #print(coloc_dict)
    return list(sorted(filter(lambda item: len(item[1]) >= min_members , coloc_dict.items() )))

def _are_ticks_contiguous(tick_1, tick_2):
    return math.fabs(tick_1[0] - tick_2[0]) <= _TICK_SIZE and tick_1[1] == tick_2[1]
    
    
def _from_tick_to_interval(tick_trace):
    #tick_trace MUST BE ORDERED
    #time, {members}
    if len(tick_trace) == 0:
        return []
    
    cur_start_interval = tick_trace[0]
    cur_end_interval = tick_trace[0]
    interval_list = []
    for t in tick_trace[1:] :
        if _are_ticks_contiguous(cur_end_interval, t ):
             cur_end_interval = t 
        else:
            #save current
            interval_list.append( (cur_start_interval[0], cur_end_interval[0], cur_end_interval[1]) )  
            cur_start_interval = t
            cur_end_interval = t
    
    interval_list.append( (cur_start_interval[0], cur_end_interval[0], cur_end_interval[1]) )
    return interval_list


def _location_colocation(traces, p_clique, loc, min_members, method_str ):
    expanded_traces = itertools.chain.from_iterable(
        [ _trace_expansion( getattr(traces[u],method_str).get(loc, [] ), u ) for u in p_clique ]
    )
    return (loc, _from_tick_to_interval(_find_colocation_tick(expanded_traces, min_members)))

def _compute_internal(traces, p_clique, min_members, common_location,  method_str ):
    return dict(
        filter(lambda item : len(item[1])>0,
               [_location_colocation(traces, p_clique, l, min_members, method_str) for l in common_location]
              ))

def compute ( p_clique, traces, member_presence_threshold = 0.6) :
    min_members = math.ceil(len(p_clique) * member_presence_threshold)
    
    common_cells = list(functools.reduce(lambda x,y : x.union(y) , [set(traces[u].get_cells()) for u in p_clique]))
    common_areas = list(functools.reduce(lambda x,y : x.union(y) , [set(traces[u].get_areas()) for u in p_clique]))
    
            
    per_cell_colocation= _compute_internal(traces, p_clique, min_members, common_cells, 'per_cell_intervals')
    per_area_colocation= _compute_internal(traces, p_clique, min_members, common_areas, 'per_area_intervals')
    
    return (per_cell_colocation, per_area_colocation)