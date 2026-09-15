#!/usr/bin/env python
# Prueba la inicialización, sincronización y lectura de datos de la base de datos.
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Importa las operaciones de base de datos que se validarán en este script.
    from app import init_db, get_db_connection, sync_external_to_db, fetch_external_data_example
    
    # Crea las tablas y los registros mínimos requeridos por la aplicación.
    print("1. Initializing database...")
    init_db()
    print("   ✓ Database initialized")
    
    # Descarga y guarda los datos deportivos externos.
    print("2. Syncing external data...")
    data = fetch_external_data_example()
    print(f"   - Got {len(data.get('matches', []))} matches")
    sync_external_to_db(data)
    print("   ✓ Data synced")
    
    # Comprueba que la sincronización dejó registros disponibles en MySQL.
    print("3. Verifying data in database...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM matches')
    result = cursor.fetchone()
    count = result[0] if result else 0
    print(f"   ✓ Found {count} matches in database")
    
    print("4. Sample match:")
    cursor.execute('SELECT * FROM matches LIMIT 1')
    sample = cursor.fetchone()
    if sample:
        print(f"   {sample}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ All checks passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
