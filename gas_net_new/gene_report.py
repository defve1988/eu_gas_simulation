import pandas as pd
from .pd_utils import group_by_time
from .constant import RATIO_KEYS


def gene_supply_df(df_node, df_storage,
            country="all", period="D",
            type="share",
            fun="sum",
            contains=None,
            reindex=None,
            detailed=False):

    groupby = [] if country == "all" else ["country"]
    if contains is None:
        contains = ["node", "storage"]

    if not detailed:
        reindex_node = [
            "Production",
            "Import-LNG",
            "Import-others",
            "Import-Russia", ]
        reindex_storage = [
            "Storage-Production",
            "Storage-LNG",
            "Storage-others",
            "Storage-Russia",
        ]

    node_grouped, df_node = group_by_time(df_node,
                                          date_col="date",
                                          period=period,
                                          groupby=groupby,
                                          fun="sum")
    storage_grouped, df_storage = group_by_time(df_storage,
                                                date_col="date",
                                                period=period,
                                                groupby=groupby,
                                                fun="sum")
    if country != "all":
        node_grouped = node_grouped.loc[node_grouped["country"] == country]
        storage_grouped = storage_grouped.loc[storage_grouped["country"] == country]

    if not detailed:
        node_grouped["others"] = node_grouped["AZ"] + node_grouped["DZ"] + \
            node_grouped["NO"] + node_grouped["RS"] + \
            node_grouped["TR"] + node_grouped["LY"]
        node_grouped = node_grouped[["period", "DIS",
                                     "FNC", "LNG", "PRO", "RU", "others"]]

        storage_grouped["others"] = storage_grouped["AZ"] + storage_grouped["DZ"] + \
            storage_grouped["NO"] + storage_grouped["RS"] + \
            storage_grouped["TR"] + storage_grouped["LY"]
        storage_grouped = storage_grouped[[
            "period", "supply", "stored", "LNG", "PRO", "RU", "others"]]

        node_grouped = node_grouped.rename(columns={"RU": "Russia",
                                                    "PRO": "Production",
                                                    "LNG": "LNG", })
        storage_grouped = storage_grouped.rename(columns={"RU": "Russia",
                                                          "PRO": "Production",
                                                          "LNG": "LNG", })
    else:
        node_grouped = node_grouped.drop(columns=["date_value", "date"])
        storage_grouped = storage_grouped.drop(columns=["date_value", "date"])

    not_used = ["period", "DIS", "FNC", "date",
                "date_value", "supply", "stored"]

    for c in node_grouped.columns:
        if c not in not_used:
            node_grouped[c] = (node_grouped["DIS"] +
                               node_grouped["FNC"])*node_grouped[c]
            if c != "Production":
                node_grouped = node_grouped.rename(columns={c: f"Import-{c}"})

    for c in storage_grouped.columns:
        if c not in not_used:
            storage_grouped[c] = storage_grouped["supply"] * \
                storage_grouped[c]
            storage_grouped = storage_grouped.rename(
                columns={c: f"Storage-{c}"})

    node_grouped = node_grouped.set_index("period")
    storage_grouped = storage_grouped.set_index("period")
    node_grouped = node_grouped.drop(columns=["DIS", "FNC"])
    storage_grouped = storage_grouped.drop(columns=["supply", "stored"])

    c = []
    re_index = [] if reindex is None else reindex
    if "storage" in contains:
        c.append(storage_grouped)
        if not detailed and reindex is None:
            re_index.extend(reindex_storage)
    if "node" in contains:
        c.append(node_grouped)
        if not detailed and reindex is None:
            re_index.extend(reindex_node)


    res = pd.concat(c, axis=1, verify_integrity=True)

    if type == "share":
        res = res.div(res.sum(axis=1), axis=0)*100
        
    if len(re_index)>0:
        res = res.reindex(columns=re_index)

    # daily storage could have very small negative values
    res[res < 0] = 0

    return res

def gen_combined_share(g):
    df1 = g.res_node[(g.res_node["DIS"]>0)|(g.res_node["FNC"]>0)]
    df2 = g.res_storage[(g.res_storage["supply"]>0)&(g.res_storage["stored"]>0)]
    
    temp = pd.merge(df1,df2, on=['date','country'], how="outer")
    temp = temp.fillna(0)
    
    df=pd.DataFrame()
    df["date"] = temp["date"]
    df["country"] = temp["country"]
    df["directSupply"] = temp["DIS"]+ temp["FNC"]-temp["supply"]
    df["storageSupply"] = temp["supply"]
    df["DIS"] = temp["DIS"]
    df["FNC"] = temp["FNC"]
    
    for k in RATIO_KEYS:
        df[k+"_fromDirectSupply"] = ((temp["DIS"]+ temp["FNC"])*temp[k+"_x"] - temp["supply"]*temp[k+"_y"]) / (temp["DIS"]+ temp["FNC"]-temp["supply"])
        df[k+"_fromStorage"] = temp[k+"_y"]
    
    return df

def gen_direct_supply(g):
    df1 = g.res_node[(g.res_node["DIS"]>0)|(g.res_node["FNC"]>0)]
    df2 = g.res_storage[(g.res_storage["supply"]>0)&(g.res_storage["stored"]>0)]
    
    temp = pd.merge(df1,df2, on=['date','country'], how="outer")
    temp = temp.fillna(0)
    
    df=pd.DataFrame()
    df["date"] = temp["date"]
    df["country"] = temp["country"]
    df["supply"] = temp["DIS"]+ temp["FNC"]-temp["supply"]
    for k in RATIO_KEYS:
        df[k] = ((temp["DIS"]+ temp["FNC"])*temp[k+"_x"] - temp["supply"]*temp[k+"_y"]) / (temp["DIS"]+ temp["FNC"]-temp["supply"])
        
    df.loc[df["supply"]>0]
    
    return df