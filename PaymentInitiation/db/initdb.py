create_transactions_table_sql = """CREATE TABLE IF NOT EXISTS Transactions (
                                id integer PRIMARY KEY AUTOINCREMENT,
                                token text NOT NULL,
                                merchant text NOT NULL,
                                status text NOT NULL,
                                merchantData text NOT NULL,
                                iban text NOT NULL
                            );"""

create_nonces_table_sql = """CREATE TABLE IF NOT EXISTS Nonce_table (
                            token text PRIMARY KEY ,
                            nonce text NOT NULL
                        );"""   

create_accounts_table_sql = """CREATE TABLE IF NOT EXISTS Accounts (
                            email text PRIMARY KEY,
                            password text NOT NULL,
                            iban text NOT NULL
                        );"""

drop_transactions_table_sql = """DROP TABLE IF EXISTS Transactions;"""  

drop_nonces_table_sql = """DROP TABLE IF EXISTS Nonce_table;"""        

drop_accounts_table_sql = """DROP TABLE IF EXISTS Accounts;"""

add_user = "INSERT INTO Accounts (email, password, iban) VALUES (?,?,?)"