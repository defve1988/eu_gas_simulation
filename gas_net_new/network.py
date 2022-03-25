import pandas as pd
from pyvis.network import Network as nxNetwork
import networkx as nx

from .node import Node
from .link import Link


class NetWorks:
    # label for utilities infantsure in the network
    utils = ["FNC", "UGS", "DIS", "LNG", "PRO"]
    # exporting country label
    export_country = ["RU", "DZ", "NO", "RS", "TR", "LY", "AZ"]

    def __init__(self, node_df, flow_data, ratio_keys, threshold=0.0001, simple=True):

        # nodes: Node
        self.nodes = {}
        # links: Link
        self.links = {}
        # threshold for equilibrium
        self.threshold = threshold

        self.ratio_keys = ratio_keys

        # residual amount and ratio of the network
        # calculated with (ITP_exit, ITP_entry) subtracted with supply from direct import
        # will not be applied for the most simulation
        self.simple = simple
        self.residual = {
            "val": 0,
            "ratio": dict.fromkeys(self.ratio_keys, 0)
        }

        self.init_nodes(node_df)
        self.init_links(flow_data)
        self.make_nx_net()

    def init_nodes(self, node_df):
        # init node of the network
        self.nodes = {}
        for r in node_df.iterrows():
            countryKey = r[1]["countryKey"]
            if countryKey not in self.utils:
                self.nodes[countryKey] = Node(
                    countryKey, r[1]["type"], (r[1]["X1"], -r[1]["Y1"]), self.ratio_keys)

    def init_links(self, flow_data):
        # init links of the network
        self.links = {}
        self.link_df = flow_data.groupby(
            ["fromCountryKey", "toCountryKey"]).size().reset_index()
        for row in self.link_df.iterrows():
            r = row[1]
            if r["toCountryKey"] not in self.utils and r["fromCountryKey"] not in self.utils:
                link_key = f"{r['fromCountryKey']}_{r['toCountryKey']}"
                self.links[link_key] = Link(
                    r["fromCountryKey"], r["toCountryKey"], self.ratio_keys)
                # add node to neighbors
                self.nodes[r["toCountryKey"]].neighbors.add(
                    r["fromCountryKey"])
                self.nodes[r["fromCountryKey"]].neighbors.add(
                    r["toCountryKey"])

    def make_nx_net(self, show=True):
        group = {
            "EU": {"val": 1, "color": "#349ceb"},
            "exporting": {"val": 2, "color": "#77e820"},
            "Russia": {"val": 3, "color": "#eb4034"},
            "non-EU": {"val": 4, "color": "#949494"},
            "EU with LNG": {"val": 5, "color": "#f0e35b"},
        }
        utils = ["FNC", "UGS", "DIS", "LNG", "ITP", "PRO"]
        
        G = nx.DiGraph()
        for index, (key, n) in enumerate(self.nodes.items()):
            # print(n.id, n.x, n.y, n.node_type)
            G.add_node(n.id,  pos=(n.x*80, -n.y*80), group=(n.node_type), color= group[n.node_type]["color"])

        for index, (key, l) in enumerate(self.links.items()):
            if l.st not in utils and l.ed not in utils:
                # print(l.st, l.ed)
                G.add_edges_from([(l.st, l.ed)])
        
        nt = nxNetwork('800px', '800px', directed=True)
        nt.from_nx(G)
        # todo: not finished
        # for index, (key, n) in enumerate(self.nodes.items()):
        #     nt.add_node(n.id, label=n.id,
        #                 x=n.x*80, y=-n.y*80, fixed=True,
        #                 group=group[n.node_type]["val"],
        #                 color=group[n.node_type]["color"],
        #                 )
        
        # for index, (key, l) in enumerate(self.links.items()):
        #     if l.st not in utils and l.ed not in utils:
        #         nt.add_edge(l.st, l.ed)

        if show:
            nt.show_buttons(filter_=['physics'])
            nt.show('nx.html')
        
        self.nt = nt
        self.nx = G
        

    def init_day(self, day_df):
        """_summary_

        Args:
            day_df (pd.DataFrame): flow dataframe for specified date
        """

        # init the net for a new round of simulation
        # the ratio from previous simulation will not be changed
        for index, (key, n) in enumerate(self.nodes.items()):
            n.isSim = False

        for index, (key, l) in enumerate(self.links.items()):
            l.isSim = False

        # get and init included nodes and links
        sim_pairs = day_df.groupby(
            ["fromCountryKey", "toCountryKey"]).size().reset_index()
        # print(sim_pairs)
        initialized = []
        for row in sim_pairs.iterrows():
            r = row[1]
            if r["fromCountryKey"] not in self.utils+initialized:
                # print(r["fromCountryKey"])
                self.nodes[r["fromCountryKey"]].init_day(day_df)
                initialized.append(r["fromCountryKey"])
                # print()
                # self.nodes[r["fromCountryKey"]].get_values()
            if r["toCountryKey"] not in self.utils+initialized:
                # print(r["toCountryKey"])
                self.nodes[r["toCountryKey"]].init_day(day_df)
                initialized.append(r["toCountryKey"])
                # print()
                # self.nodes[r["toCountryKey"]].get_values()

            if r["fromCountryKey"] not in self.utils and r["toCountryKey"] not in self.utils:
                self.links[f"{r['fromCountryKey']}_{r['toCountryKey']}"].init_day(
                    day_df)

    def get_links(self, node):
        out_links = {}
        in_links = {}
        for index, (key, l) in enumerate(self.links.items()):
            if l.st == node.id:
                out_links[key] = l
            if l.ed == node.id:
                in_links[key] = l

        return out_links, in_links

    def iter(self, detail=True):
        stop = None
        network_diff = 0
        for index, (key, n) in enumerate(self.nodes.items()):
            # if n.node_type not in ["exporting","russia"]:
            # print(n.id)
            if n.isSim:
                out_links, in_links = self.get_links(n)
                if self.simple:
                    p, diff = n.balance_simple(
                        out_links, in_links, self.threshold, detail)
                else:
                    pass

                n.get_values()
                print(f"{n.id}, diff:{diff}, equilibrium: {p}")
                stop = p if stop is None else stop and p
                network_diff += diff

        return stop, network_diff

    def summary(self, date):
        res_node = pd.DataFrame(
            columns=['date', 'country', "DIS", "FNC"] + self.ratio_keys)
        res_storage = pd.DataFrame(
            columns=['date', 'country'] + self.ratio_keys)
        res_link = pd.DataFrame(
            columns=['date', 'st', 'ed', "flow"] + self.ratio_keys)

        res_node = []
        res_storage = []
        res_link = []

        for index, (key, n) in enumerate(self.nodes.items()):
            if n.isSim:
                _, consumption, storage = n.get_values()
                temp = {
                    "date": date,
                    "country": n.id,
                    "DIS": consumption["DIS"],
                    "FNC": consumption["FNC"],
                }
                temp.update(consumption["ratio"])
                res_node.append(temp)

                temp = {
                    "date": date,
                    "country": n.id,
                    "supply":storage["entry"],
                    "stored":storage["exit"],
                }
                temp.update(storage["ratio"])
                res_storage.append(temp)

        for index, (key, l) in enumerate(self.links.items()):
            if l.isSim:
                flow, ratio = l.get_values()
                temp = {
                    "date": date,
                    "st": l.st,
                    "ed": l.ed,
                    "flow": flow,
                }
                temp.update(ratio)
                res_link.append(temp)

        res_node = pd.DataFrame(res_node)
        res_link = pd.DataFrame(res_link)
        res_storage = pd.DataFrame(res_storage)

        return res_node, res_link, res_storage
