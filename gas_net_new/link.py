class Link:
    def __init__(self, st, ed, ratio_keys):
        # flow st and ed node key, string
        self.st = st
        self.ed = ed
        # whether included in this round of simulation
        self.isSim = False
        # flow amount and ratio
        self.flow = 0
        self.ratio = dict.fromkeys(ratio_keys, 1/len(ratio_keys))

    def init_day(self, day_df):
        self.isSim = True
        self.flow = day_df.loc[(day_df["fromCountryKey"]==self.st) & (day_df["toCountryKey"]==self.ed)].sum()["value"]
        
    def get_values(self):
        # print(self.flow)
        # print(self.ratio)
        
        return self.flow, self.ratio