import numpy as np


class Node:
    def __init__(self, id, node_type, pos, ratio_keys):
        # node id
        self.id = id
        # ratio keys
        self.ratio_keys = ratio_keys
        # node type: EU, exporting, EU with LNG, russia, UK..
        self.node_type = node_type
        # node plot location
        self.x, self.y = pos
        # whether included in this round of simulation
        self.isSim = False
        # supply amount of node from different source
        self.supply = dict.fromkeys(ratio_keys, 0)
        # flow in amount
        self.flow_in = dict.fromkeys(ratio_keys, 0)
        # consumption amount and ratios of node
        self.consumption = {
            "DIS": 0,
            "FNC": 0,
            "ratio": dict.fromkeys(self.ratio_keys, 1/len(self.ratio_keys))
        }
        # storage amount and ratios of node from "UGS"
        self.storage = {
            "exit": 0,  # to storage, as consumption
            "entry": 0,  # from storage, as supply
            "storage": 0,  # current storage amount
            "ratio": dict.fromkeys(self.ratio_keys, 1/len(self.ratio_keys))
        }
        # nodes link to this node
        self.neighbors = set({})

    def get_values(self):
        # print(self.supply)
        # print(self.consumption)
        # print(self.storage)

        return self.supply, self.consumption, self.storage

    def init_day(self, day_df):
        self.isSim = True
        # reset supply and storage
        self.storage["exit"] = 0
        self.storage["entry"] = 0
        self.supply = dict.fromkeys(self.ratio_keys, 0)

        # handle supply of the day
        for i in self.supply:
            self.supply[i] = day_df.loc[(day_df["fromCountryKey"] == i) & (
                day_df["toCountryKey"] == self.id)].sum()["value"]
        # handle consumption of the day
        self.consumption["DIS"] = day_df.loc[(day_df["fromCountryKey"] == self.id) & (
            day_df["toCountryKey"] == "DIS")].sum()["value"]
        self.consumption["FNC"] = day_df.loc[(day_df["fromCountryKey"] == self.id) & (
            day_df["toCountryKey"] == "FNC")].sum()["value"]
        # handle supply of the day
        self.storage["entry"] = day_df.loc[(day_df["fromCountryKey"] == "UGS") & (
            day_df["toCountryKey"] == self.id)].sum()["value"]
        self.storage["exit"] = day_df.loc[(day_df["fromCountryKey"] == self.id) & (
            day_df["toCountryKey"] == "UGS")].sum()["value"]
        # if self.id=="ES":
        # self.get_values()

    def balance_simple(self, out_links, in_links, threshold, detail=True):
        if detail:
            print("old ratio:", self.consumption["ratio"])
            print("direct source of this node:", self.supply)
        # print("in_links",in_links)

        # supply from current iteration
        supply_iter = dict.fromkeys(self.ratio_keys, 0)
        new_ratio = dict.fromkeys(self.ratio_keys, 1/len(self.ratio_keys))
        # out flow ratio from current iteration
        out_flow = dict.fromkeys(self.ratio_keys, 1/len(self.ratio_keys))
        total_supply = 0
        total_out_flow = 0
        total_diff = 0

        # supply from direct source
        for i in self.supply:
            supply_iter[i] = self.supply[i]
        # supply from flow
        for l in in_links:
            for i in supply_iter:
                supply_iter[i] += in_links[l].flow*in_links[l].ratio[i]
        # supply from storage
        for i in supply_iter:
            supply_iter[i] += self.storage["entry"]*self.storage["ratio"][i]

        total_supply = sum(supply_iter.values())
        if total_supply == 0:
            total_supply = 0.000001

        # calculate new ratio from supply of current iteration
        for i in supply_iter:
            new_ratio[i] = supply_iter[i]/total_supply
            # calculate iteration difference
            total_diff += abs(self.consumption["ratio"]
                              [i] - supply_iter[i]/total_supply)
            self.consumption["ratio"][i] = new_ratio[i]

        if detail:
            print("supply of this iteration:", supply_iter)
            print("new ratio", self.consumption["ratio"])

        # whether this node is at equilibrium
        if total_diff <= threshold:
            stop = True
        else:
            stop = False

        # calculate out flow ratio
        for i in supply_iter:
            out_flow[i] = (self.consumption["DIS"] +
                           self.consumption["FNC"])*supply_iter[i]/total_supply
            total_out_flow += out_flow[i]
        if total_out_flow == 0:
            total_out_flow = 0.000001

        # update the ratio of flow out from the node
        for l in out_links:
            for i in supply_iter:
                out_links[l].ratio[i] = out_flow[i]/total_out_flow
        # update storage amount and ratio
        # note: entry is relative to the net, so entry to storage means loss
        old_storage = self.storage["storage"]-self.storage["entry"]
        new_storage = self.storage["exit"]
        final_storage =  old_storage + self.storage["exit"]
        
        for i in supply_iter:
            out_flow_ratio = out_flow[i]/total_out_flow
            if final_storage > 0:
                # if the storage amount is not 0, cal storage ratio
                self.storage["ratio"][i] = (old_storage * self.storage["ratio"][i] + new_storage * out_flow_ratio)/final_storage
            else:
                # if the storage amount is 0, set the current ratio in storage based on out flow ratio
                self.storage["ratio"][i] = out_flow_ratio

        self.storage["storage"] = final_storage

        return stop, total_diff
