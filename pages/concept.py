
import streamlit as st


class Concept:
  
    @staticmethod
    def write(state):
        st.header("Project Descriptions")
        st.markdown("### Motivation")
        st.markdown("""
1. EU plans to _**cut the gas supply from Russia**_, it is important to understand the impact to each EU country from this ploicy.
2. The consumption/storage share of Russian gas in EU counties remain unknown (from public dataset) altough the total importing data from Russian can be collected from ENSTOG.''')
3. This project aims to provide estimations for the _**consumption-supply-storage of EU gas network**_ by solving network balance using ENSTOG and other public datasets.''')
4. Further discussions can be performed based on the results of simulations, such as:
    * _the potential risks of EU countries without Russian gas,_
    * _the possibilities of filling the gaps caused by the Russian gas,_             
    * _...._             
                    """)
         
        st.markdown("### Simulation Concept")
        
        try:
            c1, c2 = st.columns(2)
            c1.image("concept1.png")
            c2.image("concept.png")
            
        except Exception as e:
            st.error("hum... something is going wrong here...")
            st.error(e)

