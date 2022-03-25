from .constant import *
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import matplotlib
import matplotlib.cm as cm

# import seaborn as sns
# sns.set_theme("paper")
# sns.set_style("ticks")
# plt.rcParams["figure.figsize"] = (5.4,3.2)

from.pd_utils import group_by_time, color_map, color_map2


def plot_ts(df, fig_type="share", detailed=False):

    if detailed:
        color = COUNTRY_COLOR
    else:
        color = COUNTRY_COLOR_2

    if df.shape[1] == len(color):
        color = list(map(lambda x: x+"E6", color))
    else:
        color = list(map(lambda x: x+"80", color)) + \
            list(map(lambda x: x+"E6", color))

    fig, ax = plt.subplots()

    df.plot(
        kind='area',
        stacked=True,
        color=color,
        linewidth=0,
        ax=ax
    )

    if fig_type == "share":
        plt.ylim([0, 100])
        plt.ylabel("Supply Share (%)")
    else:
        plt.ylabel("Supply amount (kwh/d)")
    plt.xlabel("")
    plt.margins(0, 0)
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")

    return fig


def plot_converge(diff_list):
    diff = []
    max_length = max(list(map(lambda x: len(x["val"]), diff_list)))
    for d in diff_list:
        temp = [0]*(max_length-len(d["val"]))
        diff.append(d["val"]+temp)

    x = range(0, max_length)
    y = np.array(diff).mean(axis=0)
    error = np.array(diff).std(axis=0)
    plt.plot(x, y, 'k-')
    plt.fill_between(x, y-error, y+error)
    plt.title("iterations vs. total difference")
    plt.show()


def plot_share(res_df, title=None, plot_country=None, re_indexing=None, sorting=None, preprocessed=False, plot=True):
    if plot_country is None:
        plot_country = ["AT", "BE-LU", "BG",  "CH", "CZ", "DE", "DK-SE",
                        "ES", "FI", "FR", "GR", "HR", "HU",   "IE", "IT",
                        "LT", "LV-EE", "NL",  "PL",   "PT",  "RO",  "SI",
                        "SK", "UK", ]
    if re_indexing is None:
        re_indexing = ['PRO', 'LNG', 'AZ', 'DZ', 'LY', 'RS', 'TR', 'NO', 'RU']
    if sorting is None:
        sorting = ['RU', 'LNG', "NO"]

    if not preprocessed:
        temp = res_df.groupby(["country", ]).mean().reset_index()
        if "DIS" in temp.columns:
            temp = temp.drop(columns=["DIS", "FNC"])
        if "supply" in temp.columns:
            temp = temp.drop(columns=["supply", "stored"])
        if "date_value" in temp.columns:
            temp = temp.drop(columns=["date_value"])

        temp = temp.loc[temp["country"].isin(plot_country)]
        temp = temp.T
        temp.columns = temp.iloc[0].values
        temp = temp.drop(index=('country'))

        # sacale to sum = 1
        for c in temp.columns:
            if temp[c].sum() != 0:
                temp[c] = temp[c]/temp[c].sum()
        temp = temp.T

        # change column order
        temp = temp.reindex(columns=re_indexing)
        temp = temp*100
    else:
        temp = res_df
    # sort based on columns
    if sorting:
        temp = temp.sort_values(by=sorting, ascending=False)

    fig, ax = plt.subplots()
    if plot:
        temp.plot(kind='bar',
                  stacked=True,
                  title=title,
                  width=0.7,
                  color=COUNTRY_COLOR,
                  edgecolor="none",
                  ax=ax)
        plt.ylabel("Supply share (%)")
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.2))
        plt.xticks(rotation=45)
        plt.margins(0)
    # plt.show()
    return temp, fig


def plot_net(net):
    G = nx.DiGraph()
    for index, (key, n) in enumerate(net.nodes.items()):
        # print(n.id, n.x, n.y, n.node_type)
        G.add_node(n.id,  pos=(n.x, n.y), node_type=(n.node_type))

    utils = ["FNC", "UGS", "DIS", "LNG", "ITP", "PRO"]

    for index, (key, l) in enumerate(net.links.items()):
        if l.st not in utils and l.ed not in utils:
            # print(l.st, l.ed)
            G.add_edges_from([(l.st, l.ed)])

    node_color = []
    labels = []
    # for each node in the graph
    for node in G.nodes(data=True):
        node_color.append(NODE_COLOR[node[1]['node_type']])
        labels.append(node[1]["node_type"])

    # Make the graph
    nx.draw(G, nx.get_node_attributes(G, 'pos'),
            with_labels=True,
            node_color=node_color,
            arrowsize=12,
            node_size=1400)
    res = plt.gca()
    res.set_title("EU gas network (for simulation)")
    # plt.show()


def plot_net_flow(node, link, net, column="RU", cmap=None, base_size=300, diff=False):
    if cmap is None:
        cmap = cm.copper

    temp = node.groupby(["country"]).sum().reset_index()[["DIS", "FNC"]]
    temp["c"] = temp["DIS"]+temp["FNC"]
    node_res = node.groupby(["country"]).mean().reset_index()
    node_res["c"] = temp["c"]

    temp = link.groupby(["st", "ed"]).sum().reset_index()[["flow"]]
    link_res = link.groupby(["st", "ed"]).mean().reset_index()
    link_res["flow"] = temp["flow"]

    for e in EXPORTING:
        node_res.loc[node_res["country"] == e, e] = 1
        node_res.loc[node_res["country"] == e, "c"] = link_res.loc[link_res["st"] == e].sum()[
            "flow"]
        link_res.loc[link_res["st"] == e, e] = 1

    # print(node_res)
    # print(link_res)

    # node size
    minima = min(np.abs(node_res["c"]))
    maxima = max(np.abs(node_res["c"]))
    node_res["size"] = np.abs(node_res["c"])/maxima*1000+base_size

    # edge width and arrow size
    minima = min(np.abs(link_res["flow"]))
    maxima = max(np.abs(link_res["flow"]))
    link_res["width"] = np.abs(link_res["flow"])/maxima*5+2
    link_res["arrow_size"] = np.abs(link_res["flow"])/maxima*3+5

    # node color

    node_res = color_map2(node_res, column, CM)
    link_res = color_map2(link_res, column, CM)

    # minima = min(node_res[column])
    # maxima = max(node_res[column])

    # norm = matplotlib.colors.Normalize(vmin=minima, vmax=maxima, clip=True)
    # mapper = cm.ScalarMappable(norm=norm, cmap=cmap)
    # c = mapper.to_rgba(node_res[column],alpha=0.9)
    # colors = []
    # for cc in c:
    #     colors.append(matplotlib.colors.to_hex(cc, keep_alpha=True))
    # node_res["color"] = colors

    # # if diff:
    # #     node_res.loc[node_res[column]>=0,"color"] ="r"
    # #     node_res.loc[node_res[column]<0,"color"] ="b"

    # # edge color
    # minima = min(link_res[column])
    # maxima = max(link_res[column])

    # norm = matplotlib.colors.Normalize(vmin=minima, vmax=maxima, clip=True)
    # mapper = cm.ScalarMappable(norm=norm, cmap=cmap)
    # c = mapper.to_rgba(link_res[column],alpha=0.5)
    # colors = []
    # for cc in c:
    #     colors.append(matplotlib.colors.to_hex(cc, keep_alpha=True))
    # colors

    # link_res["color"] = colors

    # if diff:
    #     link_res.loc[link_res[column]>=0,"color"] ="r"
    #     link_res.loc[link_res[column]<0,"color"] ="b"
    # print(node_res)
    # print(link_res)

    G = nx.MultiDiGraph()
    for row in node_res.iterrows():
        r = row[1]
        n = net.nodes[r["country"]]
        G.add_node(n.id,  pos=(n.x, n.y), size=r["size"], color=r["color"])

    for row in link_res.iterrows():
        r = row[1]
        if r["st"] not in NO_CONSUMPTION and r["ed"] not in EXPORTING and r["flow"] > 0:
            G.add_edges_from([(r["st"], r["ed"])], width=r["width"],
                             arrow_size=r["arrow_size"], color=r["color"])

    color_list = list(nx.get_node_attributes(G, 'color').values())
    size_list = list(nx.get_node_attributes(G, 'size').values())

    color_list_link = list(nx.get_edge_attributes(G, 'color').values())
    width_list_link = list(nx.get_edge_attributes(G, 'width').values())
    arrow_size_list_link = list(
        nx.get_edge_attributes(G, 'arrow_size').values())
    
    fig, ax = plt.subplots(figsize=(10,7))
    
    nx.draw(G, nx.get_node_attributes(G, 'pos'),
            with_labels=True,
            node_color=color_list,
            edge_color=color_list_link,
            arrowsize=arrow_size_list_link,
            node_size=size_list,
            # font_color="#de4e6d",
            font_weight="bold",
            width=width_list_link,
            connectionstyle='arc3, rad = 0.15',
            ax=ax
            )
    
    return fig