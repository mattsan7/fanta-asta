import pandas as pd
import sqlite3

import streamlit as st


def page_init(title: str, **kwargs):
    st.set_page_config(
        page_title=f"{title} - Fanta Asta",
        page_icon="💰",
        initial_sidebar_state="auto",
        menu_items=None,
        **kwargs
    )

    st.title(title)


def get_db_engine():

    return sqlite3.connect("./database.db")


def get_db_cursor(engine):
    return engine.cursor()


def upload_listone(file):

    with get_db_engine() as conn:
        c = get_db_cursor(conn)

        c.execute("DELETE FROM players")
        conn.commit()

        file_as_list = file.to_records(index=False).tolist()

        c.executemany("INSERT INTO  players (player_role, player_name, team, owner, price) VALUES (?, ?, ?, ?, ?)", file_as_list)
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


def upload_table(file, table_name):

    with get_db_engine() as conn:
        c = get_db_cursor(conn)

        c.execute(f"DELETE FROM {table_name}")
        conn.commit()

        for _col in file.columns:
            file[_col] = file[_col].astype(str)

        file_as_list = file.to_records(index=False).tolist()

        # c.executemany(f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?)", file_as_list)
        c.execute(f"INSERT INTO {table_name} VALUES {', '.join(map(str, file_as_list))}")
        conn.commit()

        sanity_check_results = c.execute(
            f"""SELECT *
                FROM {table_name}
            """
        ).fetchall()

        if file.shape[0] == pd.DataFrame(sanity_check_results).shape[0]:
            st.success("Tabella caricata correttamente")
        else:
            st.error("Qualcosa non ha funzionato: ricontrollare!")


def insert_user(alias, budget):

    with get_db_engine() as conn:
        results = conn.execute("""SELECT alias, number_gk, number_def, number_mid, number_att, budget
                                FROM users WHERE alias IN (?)""", (alias, )).fetchall()

        if alias == '':
            st.warning('Inserire il nome utente!', icon="⚠️")
        elif pd.DataFrame(results).shape[0] == 0:
            # Add the match information in the database based on the game_id
            conn.execute(
                "INSERT INTO users (alias, number_gk, number_def, number_mid, number_att, budget)"
                "VALUES (?, ?, ?, ?, ?, ?)",
                (alias, 0, 0, 0, 0, budget),
            )
            conn.commit()

            st.success("Utente inserito correttamente!")
        else:
            st.error("Utente già presente!")


# Function to simulate bidding logic (replace this with your backend implementation)
def get_current_bid():
    # You can implement logic to handle bids, store them in a database, etc.

    with get_db_engine() as conn:
        results = conn.execute(
            """SELECT c.player_name, c.player_role, c.team,
                    COALESCE(b.alias, ' '),
                    COALESCE(b.bid_amount, 0)
                FROM current_player c
                    LEFT JOIN bids b
                    ON c.player_name = b.player_name
                WHERE c.id = (SELECT MAX(id) FROM current_player)
                ORDER BY b.bid_amount DESC
                LIMIT 1
            """
        ).fetchall()

    if len(results) == 0:
        player_name = ' '
        player_role = ' '
        team = ' '
        alias = ' '
        bid_amount = 0
    else:
        player_name = results[0][0]
        player_role = results[0][1]
        team = results[0][2]
        alias = results[0][3]
        bid_amount = results[0][4]

    return player_name, player_role, team, alias, bid_amount


def check_user(alias):

    with get_db_engine() as conn:
        # LIKE operator is case-insensitive
        results = conn.execute("SELECT * FROM users WHERE alias LIKE (?)",
                               (alias, )).fetchall()

    if len(results) == 1:
        return True
    else:
        return False


def undo_last_bid(player_name):

    with get_db_engine() as conn:
        conn.execute("""DELETE
                    FROM bids
                    WHERE player_name = ?
                        AND bid_amount = (SELECT MAX(bid_amount) FROM bids WHERE player_name = ?)""",
                     (player_name, player_name,)
                     )
        conn.commit()

        st.success(f"Ultima offerta per {player_name} eliminata correttamente!")


def close_bid(player_name):
    # You can implement logic to handle bids, store them in a database, etc.
    if player_name is None:
        st.error('Non è stato selezionato nessun giocatore!')
    else:
        _, _, _, alias, bid_amount = get_current_bid()

        with get_db_engine() as conn:
            # Update the match information in the database based on the game_id
            conn.execute(
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
            conn.execute(
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

            player_dict = dict(conn.execute(
                "SELECT player_name, player_role FROM players WHERE player_name IN (?)",
                (player_name, ),
            ).fetchall())

            player_role = player_dict[player_name]

            current_alias_situation = pd.DataFrame(conn.execute("""
                     SELECT alias, number_gk, number_def, number_mid, number_att, budget
                     FROM users
                     WHERE alias = ?
                     ORDER BY timestamp DESC
                     LIMIT 1
                     """, (alias, )).fetchall(),
                     columns=['alias', 'number_gk', 'number_def', 'number_mid', 'number_att', 'budget'])

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
            conn.execute(
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


def check_ownership(player_name):

    with get_db_engine() as conn:
        player_info = pd.DataFrame(conn.execute("SELECT owner FROM players WHERE player_name IN (?)",
                                                (player_name, )).fetchall(),
                                   columns=['owner'])

    auction_is_closed = False

    if player_info.shape[0] > 0:
        player_owner = player_info['owner'].values[0]
        if player_owner is not None:
            auction_is_closed = True

    return auction_is_closed


def reset_table(table_name):

    with get_db_engine() as conn:
        conn.execute(f"""DELETE
                    FROM {table_name}""")
        conn.commit()

        st.success(f"Tabella {table_name} resettata correttamente!")
