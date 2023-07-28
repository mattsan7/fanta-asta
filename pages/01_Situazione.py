import pandas as pd
import streamlit as st
import plotly.express as px

from utils import helpers

helpers.page_init('Situazione')

st.subheader('Work in progress...')

st.write('Samba:')
fig_P = px.pie(pd.DataFrame({'P': [1/3, 2/3], 'Names': ['Presi', 'Da Prendere']}), title='P',
               values='P', names='Names', hole=0.4, color='Names', color_discrete_map={'Presi': 'royalblue',
                                                                                       'Da Prendere': 'lightgrey'}
               )
fig_D = px.pie(pd.DataFrame({'D': [1/8, 7/8], 'Names': ['Presi', 'Da Prendere']}), title='D',
               values='D', names='Names', hole=0.4, color='Names', color_discrete_map={'Presi': 'green',
                                                                                       'Da Prendere': 'lightgrey'}
               )
fig_C = px.pie(pd.DataFrame({'C': [3/8, 5/8], 'Names': ['Presi', 'Da Prendere']}), title='C',
               values='C', names='Names', hole=0.4, color='Names', color_discrete_map={'Presi': 'yellow',
                                                                                       'Da Prendere': 'lightgrey'}
               )
fig_A = px.pie(pd.DataFrame({'A': [5/6, 1/6], 'Names': ['Presi', 'Da Prendere']}), title='A',
               values='A', names='Names', hole=0.4, color='Names', color_discrete_map={'Presi': 'red',
                                                                                       'Da Prendere': 'lightgrey'}
               )


col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    st.plotly_chart(fig_P, use_container_width=True)
with col2:
    st.plotly_chart(fig_D, use_container_width=True)
with col3:
    st.plotly_chart(fig_C, use_container_width=True)
with col4:
    st.plotly_chart(fig_A, use_container_width=True)
