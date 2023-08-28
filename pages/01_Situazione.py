import pandas as pd
import sqlite3
import streamlit as st
# import plotly.express as px

from utils import helpers

helpers.page_init('Situazione', layout='wide')

# Connect to the SQLite database
conn = sqlite3.connect("database.db")
c = conn.cursor()

# Get user input for auction item and initial price
player_name, player_role, team, current_bidder, current_bid = helpers.get_current_bid()

# TODO: better visualization (es. background azzurro, immagini, icone...)
st.title(f'> > > > {player_name} [{team[:3].upper()}] < < < <')

# Display auction details
st.header(f"Prezzo attuale: {current_bid} [{current_bidder}]")

# refresh button (useless, just for refresh)
st.button('Aggiorna')

st.write(' ')


st.write('')

results = c.execute("""SELECT alias, number_gk, number_def, number_mid, number_att, budget
                            FROM users""").fetchall()
alias_info = pd.DataFrame(results,
                          columns=['alias', 'number_gk', 'number_def', 'number_mid', 'number_att', 'budget'])

col1, col2, col3 = st.columns([0.1, 0.1, 1])

for _n, _row in alias_info.iterrows():
    with col1:
        st.write(_row['alias'])
    with col2:
        st.markdown(f"**{_row['budget']}**")
    with col3:
        gk_str = '🟦 ' * _row['number_gk'] + '⬜️ ' * (3 - _row['number_gk'])
        def_str = '🟩 ' * _row['number_def'] + '⬜️ ' * (8 - _row['number_def'])
        mid_str = '🟨 ' * _row['number_mid'] + '⬜️ ' * (8 - _row['number_mid'])
        att_str = '🟥 ' * _row['number_att'] + '⬜️ ' * (6 - _row['number_att'])
        st.write(gk_str + def_str + mid_str + att_str)

        # st.write('🟦 ' * 3 + '🟩 ' * 8 + '🟨 ' * 8 + '🟥 ' * 6 + '🔲 ' + '⬜️ ')


# fig_P = px.pie(pd.DataFrame({'P': [1/3, 2/3], 'Names': ['Presi', 'Da Prendere']}), title='P',
#                values='P', names='Names', hole=0.4, color='Names', color_discrete_map={'Presi': 'royalblue',
#                                                                                        'Da Prendere': 'lightgrey'}
#                )
# fig_D = px.pie(pd.DataFrame({'D': [1/8, 7/8], 'Names': ['Presi', 'Da Prendere']}), title='D',
#                values='D', names='Names', hole=0.4, color='Names', color_discrete_map={'Presi': 'green',
#                                                                                        'Da Prendere': 'lightgrey'}
#                )
# fig_C = px.pie(pd.DataFrame({'C': [3/8, 5/8], 'Names': ['Presi', 'Da Prendere']}), title='C',
#                values='C', names='Names', hole=0.4, color='Names', color_discrete_map={'Presi': 'yellow',
#                                                                                        'Da Prendere': 'lightgrey'}
#                )
# fig_A = px.pie(pd.DataFrame({'A': [5/6, 1/6], 'Names': ['Presi', 'Da Prendere']}), title='A',
#                values='A', names='Names', hole=0.4, color='Names', color_discrete_map={'Presi': 'red',
#                                                                                        'Da Prendere': 'lightgrey'}
#                )
#
#
# col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
#
# with col1:
#     st.plotly_chart(fig_P, use_container_width=True)
# with col2:
#     st.plotly_chart(fig_D, use_container_width=True)
# with col3:
#     st.plotly_chart(fig_C, use_container_width=True)
# with col4:
#     st.plotly_chart(fig_A, use_container_width=True)
