import pandas as pd
from datetime import timedelta
import pickle

from .plotter import plot_net, plot_share, plot_converge, plot_ts, plot_net_flow
from .network import NetWorks
from .pd_utils import *
from .gene_report import gen_direct_supply, gene_supply_df, gen_combined_share
from .constant import *

class GasNetSim:
    Sim_num = 1000
    ratio_keys = RATIO_KEYS
    
    def __init__(self, nodes=None, flow_data=None, saved_file=None):
        if saved_file is not None:
            print("load saved simulation...")
            self.load_saved_sim(saved_file)
        elif nodes is not None:
            print("load data...")
            self.nodes_df = pd.read_csv(nodes)
            self.flow_data = pd.read_pickle(flow_data).drop_duplicates()
            self.flow_data["date_value"] =  (pd.to_datetime(self.flow_data["date"]) - pd.Timestamp('2000-01-01')).dt.days
            print("init network...")
            self.net = NetWorks(self.nodes_df, self.flow_data, self.ratio_keys)
            
        # init plotting function
        self.plot_net = plot_net
        self.plot_share = plot_share
        self.plot_converge = plot_converge    
        self.plot_ts = plot_ts   
        self.plot_net_flow = plot_net_flow   
        
        self.gene_supply_df = gene_supply_df 
        self.gen_combined_share = gen_combined_share
        self.gen_direct_supply = gen_direct_supply
        
    
    def load_saved_sim(self, file):
        with open(file, 'rb') as f:
            temp = pickle.load(f)
            self.nodes_df = temp.nodes_df
            self.flow_data = temp.flow_data
            self.net = temp.net
            
            # remove outliers only exists in UK
            self.res_node = temp.res_node[temp.res_node["DIS"]<10e10]
            self.res_link = temp.res_link[temp.res_link["flow"]<10e10]
            self.res_storage = temp.res_storage
            self.diff_list = temp.diff_list
            
            if "data_value" not in self.res_node.columns:
                self.res_node["date_value"] = (pd.to_datetime(self.res_node["date"]) - pd.Timestamp('2000-01-01')).dt.days
                self.res_link["date_value"] = (pd.to_datetime(self.res_link["date"]) - pd.Timestamp('2000-01-01')).dt.days
                self.res_storage["date_value"] = (pd.to_datetime(self.res_storage["date"]) - pd.Timestamp('2000-01-01')).dt.days
    
    def run_simulation(self,st="2017-01-01", ed="2021-12-31", save_file=None):
        Res_node = pd.DataFrame()
        Res_link = pd.DataFrame()
        Res_storage = pd.DataFrame()
        diff_list = []
        
        st = pd.to_datetime(st)
        ed = pd.to_datetime(ed)
        delta = timedelta(days=1)
        while st <= ed:
            (res_node, res_link, res_storage), diff = self.simulate_day(st)
            Res_node = pd.concat([Res_node, res_node])
            Res_link = pd.concat([Res_link, res_link])
            Res_storage = pd.concat([Res_storage, res_storage])
            
            diff_list.append({"date":st, "val":diff})
            st += delta
            
        self.res_node = Res_node
        self.res_link = Res_link
        self.res_storage = Res_storage
        self.diff_list = diff_list
        
        if save_file is not None:
            with open(save_file, 'wb') as f:
              pickle.dump(self, f)
            
        
    def simulate_day(self, date):
        print(f"simulate {date.strftime('%Y-%m-%d')}...")
        data_value = (pd.to_datetime(date) - pd.Timestamp('2000-01-01')).days
        df_day = self.flow_data.loc[self.flow_data["date_value"] == data_value]
        df_day = df_day.drop(columns=["date","date_value"])
        
        self.net.init_day(df_day)        
        s = 0
        diff = []
        while True:
            print(f"iter {s}")
            stop, iter_diff = self.net.iter(detail=False)            
            diff.append(iter_diff)
            s += 1
            if s > self.Sim_num or stop:
                break
        
        return self.net.summary(pd.to_datetime(date)), diff
        

