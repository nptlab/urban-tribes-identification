import pandas as pd
import numpy as np

class UserTrace:
    def __init__(self, user_id ,raw_trace_DF, delta_seconds):
        self.user_id = user_id
        self.per_cell_intervals = UserTrace._per_location_intervals(UserTrace._per_location_timestamps(raw_trace_DF, 'cell_id'), 
                                                                    delta_seconds)
        self.per_area_intervals = UserTrace._per_location_intervals(UserTrace._per_location_timestamps(raw_trace_DF, 'area_id'), 
                                                                    delta_seconds)
    
    def get_cells(self):
        return list(self.per_cell_intervals.keys())
    
    def get_areas(self):
        return list(self.per_area_intervals.keys())
    
        
    @staticmethod
    def _per_location_timestamps(raw_trace_DF, location_col):
        return dict( [ (location, data['timestamp'].values ) for location, data in raw_trace_DF.groupby(location_col) ] )
        
    @staticmethod
    def _per_location_intervals(per_loc_timestamps_dict, delta_seconds):
        return dict([(loc, UserTrace._expand_and_aggragate( t_list ,delta_seconds ) ) for loc, t_list in per_loc_timestamps_dict.items()])
        
        
    @staticmethod  
    def _expand_and_aggragate(timestamp_list, delta_seconds):
        timestamp_list = sorted(timestamp_list)
        cur_first_timestamp = timestamp_list[0]
        cur_last_timestamp = timestamp_list[0]
        
        interval_list = []

        for timestamp in timestamp_list[1:]:
            if timestamp - cur_last_timestamp <= delta_seconds:
                cur_last_timestamp = timestamp
            else:
                interval_list.append( ( cur_first_timestamp - delta_seconds , cur_last_timestamp + delta_seconds) )
                cur_first_timestamp = timestamp
                cur_last_timestamp = timestamp
        #append last
        interval_list.append( ( cur_first_timestamp - delta_seconds , cur_last_timestamp + delta_seconds) )
        return interval_list
        
        
def load_and_process(trace_file_path, unique_users, delta_seconds):
    #the file should have the following fields: user_id, timestamp, cell_id, area_id
    raw_traces_DF = pd.read_csv(trace_file_path, 
                names=['user_id', 'timestamp', 'cell_id' , 'area_id'] , 
                dtype=np.int32 )
    print('remove unnecessary users') 
    raw_traces_DF = raw_traces_DF.loc[raw_traces_DF['user_id'].isin(unique_users)]
    
    print('traces processing') 
    user_traces_dict= {}
    done=0
    for user_id, raw_trace in raw_traces_DF.groupby('user_id'):
        if done % 100 == 0:
            print (done, '/' , len(unique_users))
        user_traces_dict[user_id ] = UserTrace(user_id, raw_trace, delta_seconds)
        done = done +1
        
    
    return user_traces_dict