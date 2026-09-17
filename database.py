

import sqlite3

def init_db():
    conn = sqlite3.connect('imakometreba.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            user_type TEXT DEFAULT 'personal',
            active_listings_count INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            is_promoted INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
if __name__ == '__main__':
    init_db()
    print("Baza podataka imakometreba.db je uspešno kreirana!")

import sqlite3

def init_db():
    conn = sqlite3.connect('imakometreba.db')
    cursor = conn.cursor()
    
    # Tabela korisnika
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            user_type TEXT DEFAULT 'personal',
            active_listings_count INTEGER DEFAULT 0
        )
    ''')
    
    # Tabela oglasa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            is_promoted INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabela za interne poruke (Chat)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (listing_id) REFERENCES listings (id),
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Baza je uspešno ažurirana sa tabelom za poruke!")

import sqlite3

def init_db():
    conn = sqlite3.connect('imakometreba.db')
    cursor = conn.cursor()
    
    # Tabela korisnika
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            user_type TEXT DEFAULT 'personal',
            active_listings_count INTEGER DEFAULT 0
        )
    ''')
    
    # Tabela oglasa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            is_promoted INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabela za poruke (Chat)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (listing_id) REFERENCES listings (id),
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')

    # Tabela za ocene i utiske
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reviewer_id INTEGER NOT NULL,
            rated_user_id INTEGER NOT NULL,
            score INTEGER NOT NULL CHECK (score IN (1, -1)), -- 1 za pozitivnu, -1 za negativnu
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reviewer_id) REFERENCES users (id),
            FOREIGN KEY (rated_user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Baza je uspešno ažurirana sa tabelom za ocene!")

