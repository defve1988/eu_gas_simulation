import matplotlib.cm as cm

CM = {
    "PRO":cm.gray_r, 
    "LNG":cm.autumn, 
    "AZ":cm.winter_r, 
    "DZ":cm.cool_r, 
    "LY":cm.Purples,
    "RS":cm.Blues, 
    "TR":cm.Greens, 
    "NO":cm.YlOrBr, 
    "RU":cm.copper, 
}

COUNTRY_COLOR = ["#787777",
                 "#ebc036",
                 "#7795e6",
                 "#3ec7c2",
                 "#993ec7",
                 "#121eff",
                 "#2ab015",
                 "#d16615",
                 "#f2433a",
                 ]

COUNTRY_COLOR_2 = ["#787777",
                   "#ebc036",
                   "#2ab015",
                   "#f2433a", ]

NODE_COLOR = {
    "EU": "#349ceb",
    "exporting": "#2ab015",
    "Russia": "#f2433a",
    "non-EU": "#949494",
    "EU with LNG": "#ebc036",
}

EXPORTING = ["RU", "AZ", "DZ", "NO", "RS", "TR", "LY"]
NO_CONSUMPTION = ["SK", "DK-SE", "FI", "IE", "LT", "CZ"]
RATIO_KEYS = ["LNG", "PRO", "RU", "AZ", "DZ", "NO", "RS", "TR", "LY"]

AGG_FUN = {
    "LNG":('LNG','mean'), 
    "PRO":('PRO','mean'), 
    "RU":('RU','mean'), 
    "AZ":('AZ','mean'), 
    "DZ":('DZ','mean'), 
    "NO":('NO','mean'), 
    "RS":('RS','mean'), 
    "TR":('TR','mean'), 
    "LY":('LY','mean')
}

COUNTRY = [
    "AT",
    "BE-LU",
    "BG",
    "CZ",
    "DE",
    "DK-SE",
    "ES",
    "FI",
    "FR",
    "GR",
    "HR",
    "HU",
    "IE",
    "IT",
    "LT",
    "LV-EE",
    "NL",
    "PL",
    "PT",
    "RO",
    "SI",
    "SK",
    "UK",
]
