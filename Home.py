import pandas as pd
import sqlite3

import streamlit as st

from utils import helpers


# Connect to the SQLite database
with helpers.get_db_engine() as conn:
    # Create tables if they don't exist
    conn.execute(
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

    conn.execute(
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

    conn.execute(
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

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS current_player (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            player_role TEXT,
            team TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )


# Function to simulate bidding logic (replace this with your backend implementation)
def place_bid(player_name, bidder, bid_amount):
    # You can implement logic to handle bids, store them in a database, etc.
    with helpers.get_db_engine() as conn:
        results = conn.execute(
            "SELECT player_role, team FROM players WHERE player_name IN (?)",
            (player_name, ),
        ).fetchall()

        player_role = results[0][0]
        team = results[0][1]

        # st.write(f"{player_name} - Ruolo {player_role} - {team}")

        conn.execute(
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

    st.experimental_rerun()

    st.success("Bid placed successfully!")


helpers.page_init('Home')


def main():

    # st.session_state is used to keep user logged in
    if 'alias' not in st.session_state:
        input_alias = st.text_input('Inserisci il tuo nome:', placeholder='Username')
        if input_alias == '':
            st.warning('Effettuare il login', icon="⚠️")
            st.stop()
    else:
        input_alias = st.session_state['alias']

    is_initialized = helpers.check_user(input_alias)

    if (not is_initialized) & ('alias' not in st.session_state):
        if input_alias != '':
            st.warning('Il nome inserito non è corretto', icon="⚠️")
        st.stop()
    else:
        alias = st.session_state['alias'] = input_alias
        st.success(f'Benvenuto {alias}!')

    # Get user input for auction item and initial price
    player_name, player_role, team, current_bidder, current_bid = helpers.get_current_bid()

    # st.title(f':red[> > > >] {player_name} [{team[:3].upper()}] :red[< < < <]')
    st.info(f"## :red[> > > >] {player_name} [{team[:3].upper()}] :red[< < < <]")

    # Display auction details
    st.write(f"### Prezzo attuale: :blue[{current_bid} [{current_bidder}]]")

    # refresh button (useless, just for refresh)
    st.button('Aggiorna')

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

    with helpers.get_db_engine() as conn:
        results = conn.execute("""SELECT alias, number_gk, number_def, number_mid, number_att, budget
                                FROM users WHERE alias IN (?)""", (alias, )).fetchall()
    alias_info = pd.DataFrame(results,
                              columns=['alias', 'number_gk', 'number_def', 'number_mid', 'number_att', 'budget'])

    auction_is_closed = helpers.check_ownership(player_name)

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

    if plus_one_button | plus_5_button | plus_10_button | custom_button:
        # Simulate bid placement
        if player_name == ' ':
            st.error("Nessun giocatore disponibile")
        elif role_is_full:
            st.error("Hai già acquistato il numero massimo di giocatori consentito per il ruolo!")
        elif auction_is_closed:
            st.error("L'asta è già stata chiusa!")
        elif alias == current_bidder:
            st.error("Hai già fatto la migliore offerta!")
        elif budget_is_over:
            st.error(f"Non hai abbastanza budget! Puoi offrire al massimo {available_budget}")
        elif bid_amount <= current_bid:
            st.error("Devi rilanciare di più!")
        else:
            place_bid(player_name, alias, bid_amount)


if __name__ == "__main__":
    main()
