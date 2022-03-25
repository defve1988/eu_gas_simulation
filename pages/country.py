# from numpy import correlate
import streamlit as st
# from pandas_profiling import ProfileReport
# from streamlit_pandas_profiling import st_profile_report
    

# CORRS = ["pearson", "spearman", "kendall", "phi_k", "cramers"]

class Country:
    
   
    
    @staticmethod
    def write(state):
        st.header("Country View")
        try:
            cc1, _, _ = st.columns(3)
            
            contains = cc1.selectbox(
                "Aspect",
                ("consumption",
                 "storage")
            )
            
            c1, c2 = st.columns(2)
            
            y1 = c1.selectbox(
                "First Year",
                (2021, 2020, 2019, 2018, 2017),
                index=0,                
            )
            y2 = c2.selectbox(
                "Second Year",
                (2021, 2020, 2019, 2018, 2017),
                index=4,
            )
            
        except Exception as e:
            st.error("hum... something is going wrong here...")
            st.error(e)
