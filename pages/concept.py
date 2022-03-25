# from numpy import correlate
import streamlit as st
# from pandas_profiling import ProfileReport
# from streamlit_pandas_profiling import st_profile_report
    

# CORRS = ["pearson", "spearman", "kendall", "phi_k", "cramers"]

class Concept:
    
    @staticmethod
    def init_profile(config):
        config.samples.head=0
        config.samples.tail=0
        config.samples.random=0
        config.missing_diagrams["bar"] = False
        config.missing_diagrams["matrix"] = False
        config.missing_diagrams["heatmap"] = False
        config.missing_diagrams["dendrogram"] = False
        config.interactions.targets = []
        config.interactions.continuous = False
        

        for c in CORRS:
            config.correlations[c].calculate = False
        
        return config
    
    
    @staticmethod
    def show_missing(config): 
        config.missing_diagrams["bar"] = True
        config.missing_diagrams["matrix"] = True
        config.missing_diagrams["heatmap"] = True
        config.missing_diagrams["dendrogram"] = True
        
        return config
    
    
    @staticmethod
    def write(state):
        st.header("Data Summary")
        if state.g is not None:
            st.dataframe(state.g.res_node)
            # pr = state.df.profile_report()
                                            
            # pr.config = DataInfo.init_profile(pr.config)

            # show_corr = st.checkbox("Show correlation")
            # if show_corr:
            #     selected_corr = st.multiselect(
            #         "Correlations", CORRS, CORRS)
            #     for c in selected_corr:
            #         pr.config.correlations[c].calculate = True

            # # show_interaction = st.checkbox("Show interations")
            # # if show_interaction:
            # #     selected_vars = st.multiselect(
            # #         "Variables", state.df.columns, list(state.df.columns))
            # #     pr.config.interactions.targets = selected_vars
            # #     pr.config.interactions.continuous = True

            # show_missing = st.checkbox("Show missing values")
            # if show_missing:
            #     pr.config = DataInfo.show_missing(pr.config)

            # ok = st.button("Generate Summary")
            # if ok:
            #     st_profile_report(pr)
        else:
            st.error("Please upload/select dataset first!")
