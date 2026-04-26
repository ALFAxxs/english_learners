import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

cur.execute("INSERT OR IGNORE INTO django_migrations (app, name, applied) VALUES ('game', '0001_initial', datetime('now'))")

cur.execute('''
CREATE TABLE IF NOT EXISTS game_playersnapshot (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    verb_index INTEGER NOT NULL,
    verb_base VARCHAR(100) NOT NULL,
    image VARCHAR(100) NOT NULL,
    taken_at DATETIME NOT NULL,
    session_id INTEGER NOT NULL REFERENCES game_gamesession(id)
)
''')

conn.commit()
conn.close()
print('Done!')