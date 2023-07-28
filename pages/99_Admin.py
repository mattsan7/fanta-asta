import pandas as pd
import streamlit as st

from utils import helpers


USER = "admin"
PASSWORD = "admin"


helpers.page_init("Admin")

# Page layout
col1, col2 = st.columns(2)

usr = col1.text_input("Username", placeholder='Username')  # type='password')
pwd = col2.text_input("Password", placeholder='Password', type="password")

# Show page only to authenticated user
if not (usr == USER and pwd == PASSWORD):
    st.warning("Effettuare il login", icon="⚠️")
    st.stop()

st.success('Accesso eseguito correttamente')

# Admin Sections
# --------------

# 1
st.header('Inserimento Utenti')

budget = st.slider(label='Budget',
                   min_value=0, max_value=1000,
                   value=500, step=25)

alias = st.text_input('Nome utente:', placeholder='User')

if st.button(label="Inserisci utente", key='user'):
    helpers.insert_user(alias, budget)


# 2
st.header('Caricamento Listone')
# https://www.gazzetta.it/static_images/infografiche/FREEMIUM/fantamercato-listone-2023-24.pdf
upload_file = st.file_uploader("Carica file")

if upload_file is not None:
    df = pd.read_csv(upload_file, sep=';', index_col=False)
    st.write(df.head())

    if st.button(label="Inserisci listone nel DB", key='listone'):
        # Simulate bid placement
        helpers.upload_players(df[['Ruolo', 'Nome', 'Squadra']])


# 3
st.header('Gestione Asta')
# Get current player name
st.subheader("Seleziona giocatore")
with helpers.get_db_engine() as conn:
    player_df = pd.DataFrame(conn.execute("SELECT player_name, player_role, team, owner FROM players").fetchall(),
                             columns=['player_name', 'player_role', 'team', 'owner'])

player_name = st.selectbox(
    'Seleziona giocatore:',
    player_df['player_name'].sort_values())
player_info = player_df.loc[player_df['player_name'] == player_name].copy()

auction_is_closed = False

if player_info.shape[0] > 0:
    player_role = player_info['player_role'].values[0]
    team = player_info['team'].values[0]
    player_owner = player_info['owner'].values[0]

    if player_owner is not None:
        auction_is_closed = True
        st.error('Il giocatore è già stato acquistato!')
    else:
        with helpers.get_db_engine() as conn:
            results = pd.DataFrame(conn.execute("""SELECT player_name
                                                    FROM current_player
                                                    ORDER BY id DESC
                                                    LIMIT 1""").fetchall(),
                                   columns=['player_name'])
            current_player_name = results['player_name'].values[0]

            if current_player_name != player_name:
                conn.execute(
                    "INSERT INTO current_player (player_name, player_role, team) "
                    "VALUES (?, ?, ?)",
                    (
                        player_name,
                        player_role,
                        team
                    ),
                )
                conn.commit()
                st.success(f'{player_name} selezionato correttamente!')

else:
    player_role = ''

st.subheader("Annulla offerta")
undo_button = st.button("Annulla ultima offerta")

if undo_button:
    # Simulate bid placement
    helpers.undo_last_bid(player_name)

st.subheader("Conferma offerta")
close_button = st.button("Aggiudicato!")

if close_button:
    # Simulate bid placement
    helpers.close_bid(player_name)


st.header('Visualizza')
view1, view2, view3, view4 = st.columns([1, 1, 1, 1])

# Button declaration is separated from click to use full page width for table display
with view1:
    view_users_button = st.button("Visualizza Users")
with view2:
    view_players_button = st.button("Visualizza Players")
with view3:
    view_bids_button = st.button("Visualizza Bids")
with view4:
    view_current_player_button = st.button("Current Player")

if view_users_button:
    with helpers.get_db_engine() as conn:
        results = conn.execute('SELECT * FROM users').fetchall()
    col_order = ['id', 'alias', 'number_gk', 'number_def', 'number_mid', 'number_att',
                 'budget', 'last_player_acquired', 'timestamp']
    st.write(pd.DataFrame(results, columns=col_order))
if view_players_button:
    with helpers.get_db_engine() as conn:
        results = conn.execute('SELECT * FROM players ORDER BY player_name').fetchall()
    col_order = ['id', 'player_name', 'player_role', 'team', 'owner', 'price']
    # st.write(pd.DataFrame(results).head(10))
    st.dataframe(pd.DataFrame(results, columns=col_order))
if view_bids_button:
    with helpers.get_db_engine() as conn:
        results = conn.execute('SELECT * FROM bids ORDER BY id DESC').fetchall()
    col_order = ['id', 'alias', 'player_name', 'player_role', 'team', 'bid_amount', 'success', 'timestamp']
    st.write(pd.DataFrame(results, columns=col_order).head(10))
if view_current_player_button:
    with helpers.get_db_engine() as conn:
        results = conn.execute('SELECT * FROM current_player ORDER BY id DESC LIMIT 1').fetchall()
    col_order = ['id', 'player_name', 'player_role', 'team', 'timestamp']
    st.write(pd.DataFrame(results, columns=col_order))

st.header('Download')
download1, download2, download3, _ = st.columns([1, 1, 1, 1])

with download1:
    download_users_button = st.button("Download Users")
with download2:
    download_players_button = st.button("Download Players")
with download3:
    download_bids_button = st.button("Download Bids")


st.header('Upload')
upload1, upload2, upload3, _ = st.columns([1, 1, 1, 1])

with upload1:
    upload_users_button = st.button("Upload Users")
with upload2:
    upload_players_button = st.button("Upload Players")
with upload3:
    upload_bids_button = st.button("Upload Bids")


st.header('Reset')
reset1, reset2, reset3, reset4 = st.columns([1, 1, 1, 1])

with reset1:
    reset_users_button = st.button("Reset Users")
with reset2:
    reset_players_button = st.button("Reset Players")
with reset3:
    reset_bids_button = st.button("Reset Bids")
with reset4:
    reset_current_player_button = st.button("Reset Current Player")

if reset_users_button:
    helpers.reset_table('users')
if reset_players_button:
    helpers.reset_table('players')
if reset_bids_button:
    helpers.reset_table('bids')
if reset_current_player_button:
    helpers.reset_table('current_player')
