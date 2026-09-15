#!/usr/bin/env python
# Comprueba los datos externos y muestra algunos partidos guardados en MySQL.
import app

# Consulta y muestra la información de partidos obtenida desde la fuente externa.
print('\n=== TESTING FALLBACK DATA ===')
data = app.fetch_external_data_example()
print("Fetched %d matches from external data" % len(data.get('matches', [])))
if data.get('matches'):
    print("\nFirst 3 matches:")
    for m in data['matches'][:3]:
        print("  %s vs %s (%s)" % (m.get('home_team'), m.get('away_team'), m.get('league_name')))
        print("    Stadium: %s" % m.get('stadium'))
        print("    Kickoff: %s" % m.get('kickoff'))
        print()

# Consulta y muestra los primeros partidos actualmente almacenados en la base de datos.
print('\n=== CURRENT DB MATCHES ===')
conn = app.get_db_connection()
cursor = conn.cursor(dictionary=True)
cursor.execute('SELECT id, league_name, home_team, away_team, stadium, kickoff FROM matches LIMIT 3')
matches = cursor.fetchall()
cursor.close()
conn.close()

for m in matches:
    print("  %s vs %s (%s)" % (m['home_team'], m['away_team'], m['league_name']))
    print("    Stadium: %s" % m['stadium'])
    print()
