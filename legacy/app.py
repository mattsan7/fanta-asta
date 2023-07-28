import pandas as pd
import sqlite3

import streamlit as st


# TODO: come gestire credenziali su streamlit? file .toml
# TODO: servono credenziali
USER = "admin"
PASSWORD = "admin"

# Connect to the SQLite database
conn = sqlite3.connect("../database.db")
c = conn.cursor()

# Create tables if they don't exist
c.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alias TEXT UNIQUE,
        number_gk INTEGER,
        number_def INTEGER,
        number_mid INTEGER,
        number_att INTEGER,
        budget INTEGER,
        last_player_acquired TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)

c.execute(
    """
    CREATE TABLE IF NOT EXISTS bids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alias TEXT,
        player_name TEXT,
        player_role TEXT,
        team TEXT,
        bid_amount INTEGER,
        success INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)

c.execute(
    """
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT,
        player_role TEXT,
        team TEXT,
        owner TEXT,
        price INTEGER
    )
"""
)


# Function to simulate bidding logic (replace this with your backend implementation)
def place_bid(player_name, bidder, bid_amount):
    # You can implement logic to handle bids, store them in a database, etc.

    results = c.execute(
        "SELECT player_role, team FROM players WHERE player_name IN (?)",
        (player_name, ),
    ).fetchall()

    player_role = results[0][0]
    team = results[0][1]

    # st.write(f"{player_name} - Ruolo {player_role} - {team}")

    c.execute(
        "INSERT INTO bids (alias, player_name, player_role, team, bid_amount) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            bidder,
            player_name,
            player_role,
            team,
            bid_amount
        ),
    )
    conn.commit()

    st.success("Bid placed successfully!")


# Function to simulate bidding logic (replace this with your backend implementation)
def get_current_bid(player_name):
    # You can implement logic to handle bids, store them in a database, etc.

    results = c.execute(
        """SELECT alias, bid_amount
            FROM bids
            WHERE player_name IN (?)
            ORDER BY bid_amount DESC
            LIMIT 1
        """,
        (player_name, ),
    ).fetchall()

    if len(results) == 0:
        alias = ' '
        bid_amount = 0
    else:
        alias = results[0][0]
        bid_amount = results[0][1]

    return alias, bid_amount


# Function to simulate bidding logic (replace this with your backend implementation)
def close_bid(player_name):
    # You can implement logic to handle bids, store them in a database, etc.

    alias, bid_amount = get_current_bid(player_name)

    # Update the match information in the database based on the game_id
    c.execute(
        """
        UPDATE bids 
        SET success = 1
        WHERE player_name = ?
            AND alias = ?
            AND bid_amount = ?
    """,
        (
            player_name,
            alias,
            bid_amount
        ),
    )
    conn.commit()

    # Update the match information in the database based on the game_id
    c.execute(
        """
        UPDATE players 
        SET owner = ?
            , price = ?
        WHERE player_name = ?
    """,
        (
            alias,
            bid_amount,
            player_name
        ),
    )
    conn.commit()

    player_dict = dict(c.execute(
        "SELECT player_name, player_role FROM players WHERE player_name IN (?)",
        (player_name, ),
    ).fetchall())

    player_role = player_dict[player_name]

    current_alias_situation = pd.DataFrame(c.execute("""
             SELECT alias, number_gk, number_def, number_mid, number_att, budget
             FROM users
             WHERE alias = ?
             ORDER BY timestamp DESC
             LIMIT 1
             """, (alias, )).fetchall(),
             columns=['alias', 'number_gk', 'number_def', 'number_mid', 'number_att', 'budget'])

    st.write(current_alias_situation)

    n_gk = current_alias_situation['number_gk'].values[0]
    n_def = current_alias_situation['number_def'].values[0]
    n_mid = current_alias_situation['number_mid'].values[0]
    n_att = current_alias_situation['number_att'].values[0]

    if player_role == 'P':
        n_gk += 1
    elif player_role == 'D':
        n_def += 1
    elif player_role == 'C':
        n_mid += 1
    elif player_role == 'A':
        n_att += 1
    else:
        st.error('Ruolo sconosciuto! Verificare i dati')

    remaining_budget = current_alias_situation['budget'].values[0] - bid_amount

    # Add the match information in the database based on the game_id
    c.execute(
        """UPDATE users 
        SET number_gk = ?
            , number_def = ?
            , number_mid = ?
            , number_att = ?
            , budget = ?
            , last_player_acquired = ?
        WHERE alias = ?""",
        (
            int(n_gk),
            int(n_def),
            int(n_mid),
            int(n_att),
            int(remaining_budget),
            player_name,
            alias,
        ),
    )
    conn.commit()

    st.success("Match successfully Edited.")


def upload_players(file):

    c.execute("DELETE FROM players")
    conn.commit()

    file_as_list = file.to_records(index=False).tolist()

    c.executemany("INSERT INTO  players (player_role, player_name, team) VALUES (?, ?, ?)", file_as_list)
    conn.commit()

    sanity_check_results = c.execute(
        """SELECT *
            FROM players
        """
    ).fetchall()

    if file.shape[0] == pd.DataFrame(sanity_check_results).shape[0]:
        st.success("Listone caricato correttamente")
    else:
        st.error("Qualcosa non ha funzionato: ricontrollare!")


def undo_last_bid(player_name):

    c.execute("""DELETE
                FROM bids
                WHERE player_name = ?
                    AND bid_amount = (SELECT MAX(bid_amount) FROM bids WHERE player_name = ?)""",
              (player_name, player_name,)
              )
    conn.commit()

    st.success("Ultima offerta eliminata correttamente")


def insert_user(alias, budget):

    results = c.execute("""SELECT alias, number_gk, number_def, number_mid, number_att, budget
                            FROM users WHERE alias IN (?)""", (alias, )).fetchall()

    if alias == '':
        st.warning('Inserisci il tuo nome!', icon="⚠️")
    elif pd.DataFrame(results).shape[0] == 0:
        # Add the match information in the database based on the game_id
        c.execute(
            "INSERT INTO users (alias, number_gk, number_def, number_mid, number_att, budget)"
            "VALUES (?, ?, ?, ?, ?, ?)",
            (alias, 0, 0, 0, 0, budget),
        )
        conn.commit()

        st.success("Utente inserito correttamente!")
    else:
        st.write(pd.DataFrame(results,
                              columns=['alias', 'number_gk', 'number_def', 'number_mid', 'number_att', 'budget']))

    return


def main():
    # TODO: multi-page
    # TODO: refresh button? (pointless)
    st.header("Fanta Asta")

    # ADMIN
    # TODO: rendere il budget una variabile
    budget = 500

    alias = st.text_input('Inserisci il tuo nome:')

    # TODO: inizializzare users: lo fa l'admin per un subset di giocatori prefissato o ognuno entra e si registra?
    insert_user(alias, budget)

    # TODO: caricamento pagina solo dopo autenticazione

    # Get current player name
    player_df = pd.DataFrame(c.execute("SELECT player_name, player_role, team, owner FROM players").fetchall(),
                             columns=['player_name', 'player_role', 'team', 'owner'])

    # TODO: dovrà selezionare l'admin il giocatore su cui si svolge l'asta

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

        # TODO: better visualization (es. background azzurro, immagini, icone...)
        st.title(f'> > > > {player_name} [{team[:3].upper()}] < < < <')
    else:
        player_role = ''

    # Get user input for auction item and initial price
    current_bidder, current_bid = get_current_bid(player_name)

    # Display auction details
    st.header(f"Prezzo attuale: {current_bid} [{current_bidder}]")

    # Get current user (you can implement authentication for multiple users)
    # TODO: authenticated user ID
    # https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/
    # TODO: aggiungere una pagina admin per vedere chi si è registrato

    st.write(' ')

    # Real-time bidding section
    col1, col2, col3, _, _ = st.columns([1, 1, 1, 1, 1])

    with col1:
        plus_one_offer = current_bid + 1
        plus_one_button = st.button(f"💲 - Offri {plus_one_offer}")
    with col2:
        next_multiple_5_offer = (current_bid + 6) // 5 * 5
        plus_5_button = st.button(f"💰 - Offri {next_multiple_5_offer}")
    with col3:
        next_multiple_10_offer = (current_bid + 16) // 10 * 10
        plus_10_button = st.button(f"🤑 - Offri {next_multiple_10_offer}")

    custom_amount = st.number_input("Inserisci la tua offerta:", value=current_bid * 1.0, step=1.0)
    custom_button = st.button("Offri")

    if plus_one_button:
        bid_amount = plus_one_offer
    elif plus_5_button:
        bid_amount = next_multiple_5_offer
    elif plus_10_button:
        bid_amount = next_multiple_10_offer
    elif custom_button:
        bid_amount = custom_amount
    else:
        bid_amount = current_bid

    results = c.execute("""SELECT alias, number_gk, number_def, number_mid, number_att, budget
                            FROM users WHERE alias IN (?)""", (alias, )).fetchall()
    alias_info = pd.DataFrame(results,
                              columns=['alias', 'number_gk', 'number_def', 'number_mid', 'number_att', 'budget'])

    # TODO: file .py con le constants (e.g. budget, mapping, numero di giocatori per ruolo...)

    if alias_info.shape[0] > 0:
        if player_role == 'P':
            role_is_full = (alias_info['number_gk'].values[0] >= 3)
        elif player_role == 'D':
            role_is_full = (alias_info['number_def'].values[0] >= 8)
        elif player_role == 'C':
            role_is_full = (alias_info['number_mid'].values[0] >= 8)
        elif player_role == 'A':
            role_is_full = (alias_info['number_att'].values[0] >= 6)
        else:
            role_is_full = False

        remaining_budget = alias_info['budget'].values[0]
        available_budget = (remaining_budget
                            - (3 - alias_info['number_gk'].values[0])
                            - (8 - alias_info['number_def'].values[0])
                            - (8 - alias_info['number_mid'].values[0])
                            - (6 - alias_info['number_att'].values[0])
                            + 1
                            )
        budget_is_over = (bid_amount > available_budget)
    else:
        role_is_full = False

        available_budget = budget
        budget_is_over = False

    if plus_one_button | plus_5_button | plus_10_button | custom_button:
        # Simulate bid placement
        if bid_amount <= current_bid:
            st.error("Devi rilanciare di più!")
        elif auction_is_closed:
            st.error("L'asta è già stata chiusa!")
        elif role_is_full:
            st.error("Hai già acquistato il numero massimo di giocatori consentito per il ruolo!")
        elif budget_is_over:
            st.error(f"Non hai abbastanza budget! Puoi offrire al massimo {available_budget}")
        else:
            place_bid(player_name, alias, bid_amount)

    # TODO: pagina dedicata
    st.title("Admin")

    st.header("Visualizza tabelle")
    view1, view2, view3, _ = st.columns([1, 1, 1, 1])

    with view1:
        view_users_button = st.button("Visualizza Users")
    with view2:
        view_players_button = st.button("Visualizza Players")
    with view3:
        view_bids_button = st.button("Visualizza Bids")

    if view_users_button:
        results = c.execute('SELECT * FROM users').fetchall()
        col_order = ['id', 'alias', 'number_gk', 'number_def', 'number_mid', 'number_att',
                     'budget', 'last_player_acquired', 'timestamp']
        st.write(pd.DataFrame(results, columns=col_order).tail(10))
    if view_players_button:
        results = c.execute('SELECT * FROM players ORDER BY player_name').fetchall()
        col_order = ['id', 'player_name', 'player_role', 'team', 'owner', 'price']
        # st.write(pd.DataFrame(results).head(10))
        st.dataframe(pd.DataFrame(results, columns=col_order))
    if view_bids_button:
        results = c.execute('SELECT * FROM bids ORDER BY timestamp DESC').fetchall()
        col_order = ['id', 'alias', 'player_name', 'player_role', 'team', 'bid_amount', 'success', 'timestamp']
        st.write(pd.DataFrame(results, columns=col_order).head(10))

    st.header("Annulla offerta")
    undo_button = st.button("Annulla ultima offerta")

    if undo_button:
        # Simulate bid placement
        undo_last_bid(player_name)

    st.header("Conferma offerta")
    close_button = st.button("Aggiudicato!")

    if close_button:
        # Simulate bid placement
        close_bid(player_name)

    st.header("Caricamento listone")
    # https://www.gazzetta.it/static_images/infografiche/FREEMIUM/fantamercato-listone-2023-24.pdf
    upload_file = st.file_uploader("Carica file")

    if upload_file is not None:
        df = pd.read_csv(upload_file, sep=';', index_col=False)
        st.write(df.head())

        upload_button = st.button("Inserisci listone nel DB")

        if upload_button:
            # Simulate bid placement
            upload_players(df[['Ruolo', 'Nome', 'Squadra']])
    else:
        sanity_check_results = pd.DataFrame(c.execute(
            "SELECT player_name, player_role, team, owner FROM players"
        ).fetchall(), columns=['player_name', 'player_role', 'team', 'owner'])

        if sanity_check_results.shape[0] > 0:
            st.warning("Controlla il listone")
            st.write(sanity_check_results.head())
        else:
            st.error('Carica il listone', icon="⚠️")

    # TODO: aggiungere export bids per avere riassunto / backup
    # TODO: come backup, permettere il caricamento della tabella bids o players e il ricalcolo della tabella users
    # TODO: visualizzare con emoji colorate il riempimento degli slot per ogni giocatore per ruolo
    # TODO: tabellina con ultimi acquisti e prezzi
    # TODO: crediti residui
    # TODO: admin può fare reset per riazzerare bids e users + owner e prezzo della tabella players


if __name__ == "__main__":
    main()
