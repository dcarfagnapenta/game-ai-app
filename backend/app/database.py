import sqlite3

DB_PATH = "videogames_bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferenze_utente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            titolo_gioco TEXT NOT NULL,
            completato INTEGER DEFAULT 0,
            voto TEXT,
            recensione_utente TEXT,
            UNIQUE(user_id, titolo_gioco)
        )
    ''')
    conn.commit()
    conn.close()

def salva_o_aggiorna_gioco(user_id, titolo, completato=None, voto=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT completato, voto FROM preferenze_utente WHERE user_id = ? AND titolo_gioco = ?", 
        (user_id, titolo)
    )
    row = cursor.fetchone()
    
    if row:
        nuovo_completato = completato if completato is not None else row[0]
        nuovo_voto = voto if voto is not None else row[1]
        cursor.execute('''
            UPDATE preferenze_utente 
            SET completato = ?, voto = ? 
            WHERE user_id = ? AND titolo_gioco = ?
        ''', (nuovo_completato, nuovo_voto, user_id, titolo))
    else:
        cursor.execute('''
            INSERT INTO preferenze_utente (user_id, titolo_gioco, completato, voto)
            VALUES (?, ?, ?, ?)
        ''', (user_id, titolo, completato or 0, voto or "neutro"))
        
    conn.commit()
    conn.close()

def ottieni_profilo_utente(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT titolo_gioco, completato, voto FROM preferenze_utente WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "L'utente non ha ancora espresso preferenze su nessun gioco."
        
    profilo = "Giochi dell'utente:\n"
    for row in rows:
        stato = "Completato" if row[1] == 1 else "In corso/Da iniziare"
        profilo += f"- {row[0]}: Stato: {stato}, Feedback: {row[2]}\n"
    return profilo
