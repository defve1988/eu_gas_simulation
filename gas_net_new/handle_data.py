import pandas as pd
import numpy as np


def handle_operational(operational_path, links):
    print("load operational data...")
    # read data
    operational = pd.read_pickle(operational_path, compression='xz')
    
    print("handle operational data...")
    # keep non NAN values
    operational =operational.loc[operational['isNA']!=1]
    # keep useful columns
    operational = operational[['periodTo', 'pointKey', 'directionKey', 'unit',  'value']]
    
    # keep relvent points
    keep_points = set(links["pointKey"].unique())
    keep_points.remove(np.nan)
    operational = operational.loc[operational["pointKey"].isin(keep_points)]
    
    # convert date
    operational["date"] = pd.to_datetime(operational['periodTo']).dt.date
    operational = operational.drop(columns=['periodTo'])
    
    for row in links.loc[~links["pointKey"].isna()].iterrows():
        r = row[1]
        operational.loc[operational["pointKey"]==r["pointKey"], "countryKey"]=r["fromCountryKey"]
        operational.loc[operational["pointKey"]==r["pointKey"], "adjacentCountryKey"]=r["toCountryKey"]
    
    return operational
    

def handle_aggregated(aggregated_path, balanceZone, DE, AT):
    print("load aggregated data...")
    # read data
    aggregated = pd.read_pickle(aggregated_path, compression='xz')
    balanceZone= pd.read_csv(balanceZone)
    
    print("handle aggregated data...")
    # keep useful columns
    aggregated = aggregated[['periodTo', 'countryKey', 'directionKey', 'unit',  'value', 'adjacentSystemsLabel']]
    # combine and rename regions
    aggregated.loc[aggregated["countryKey"]=="BE", "countryKey"]="BE-LU"
    aggregated.loc[aggregated["countryKey"]=="LU", "countryKey"]="BE-LU"
    aggregated.loc[aggregated["countryKey"]=="LV", "countryKey"]="LV-EE"
    aggregated.loc[aggregated["countryKey"]=="EE", "countryKey"]="LV-EE"
    aggregated.loc[aggregated["countryKey"]=="DK", "countryKey"]="DK-SE"
    aggregated.loc[aggregated["countryKey"]=="SE", "countryKey"]="DK-SE"
    for row in balanceZone.iterrows():
        r=row[1]
        aggregated.loc[aggregated["adjacentSystemsLabel"]==r["adjacentSystemsLabel"], "adjacentCountryKey"] = r["Assigned_country_key"]
    aggregated = aggregated.drop(columns=["adjacentSystemsLabel"])
    
    # remove DE-DE from original data
    aggregated = aggregated.loc[~((aggregated["countryKey"]=="DE") & (aggregated["adjacentCountryKey"]=="DE"))]
    
    # add de and at consumption data
    print("combine DE consumption data...")
    DE= pd.read_csv(DE)
    DE = DE.set_index("date").stack().reset_index()
    DE = DE.rename(columns={
        "level_1":"adjacentCountryKey",
        0:"value",
    })
    DE.loc[DE["adjacentCountryKey"]=="Distribution", "adjacentCountryKey"]="DIS"
    DE.loc[DE["adjacentCountryKey"]=="Final Consumer", "adjacentCountryKey"]="FNC"
    DE["countryKey"]="DE"
    DE["directionKey"]="exit"
    DE["unit"]="kWh/d"
    
    print("combine AT consumption data...")
    AT= pd.read_csv(AT)
    AT = AT.rename(columns={
        "Total consumption":"value",
    })
    AT["countryKey"]="AT"
    AT["directionKey"]="exit"
    AT["unit"]="kWh/d"
    AT["adjacentCountryKey"]="DIS"
    
    aggregated = pd.concat([aggregated, DE, AT])
    
    # convert date
    aggregated["date"] = pd.to_datetime(aggregated['periodTo']).dt.date
    aggregated = aggregated.drop(columns=['periodTo'])
    
    return aggregated