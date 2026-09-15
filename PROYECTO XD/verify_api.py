#!/usr/bin/env python
# Verifica el inicio de sesión de prueba y la respuesta de la API de partidos.
import app
import json

# Crea un cliente de pruebas para ejecutar solicitudes sin abrir un navegador.
c = app.app.test_client()
r = c.post('/login', data={'login_input':'admin','password':'admin123'}, follow_redirects=False)
r2 = c.get('/api/partidos')
data = r2.get_json()

# Muestra un resumen de las ligas y partidos devueltos por la API.
print('\n=== API VERIFICATION ===')
print('Total leagues:', len(data.get('leagues', [])))

for i, league in enumerate(data.get('leagues', [])[:6]):
    name = league.get('name')
    matches = league.get('matches', [])
    print(f'\n{i+1}. {name}: {len(matches)} partidos')
    
    for j, match in enumerate(matches[:2]):
        home = match.get('home')
        away = match.get('away')
        stadium = match.get('stadium')
        time = match.get('time')
        print(f'   Match {j+1}: {home} vs {away}')
        print(f'   Stadium: {stadium}, Time: {time}')
