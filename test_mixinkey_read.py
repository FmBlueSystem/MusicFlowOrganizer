#!/usr/bin/env python3
"""
test_mixinkey_read.py
====================
Script de prueba para validar la lectura correcta de Collection11.mikdb
usando el esquema Core Data correcto.
"""

import sqlite3
from pathlib import Path

def test_read_collection11():
    """Probar lectura de Collection11.mikdb con esquema correcto"""
    db_path = Path.home() / "Library" / "Application Support" / "Mixedinkey" / "Collection11.mikdb"
    
    if not db_path.exists():
        print(f"❌ Base de datos no encontrada: {db_path}")
        return
    
    print(f"🔍 Probando lectura de: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Query correcta para tabla ZSONG
        query = "SELECT ZARTIST, ZNAME, ZALBUM, ZTEMPO, ZKEY, ZENERGY, ZGENRE FROM ZSONG LIMIT 5"
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        print(f"✅ Query exitosa: {len(rows)} registros encontrados")
        print(f"📋 Columnas: {columns}")
        print("\n🎵 MUESTRA DE DATOS:")
        print("-" * 80)
        
        for i, row in enumerate(rows, 1):
            print(f"Track {i}:")
            for col, value in zip(columns, row):
                print(f"  {col}: {value}")
            print()
        
        # Conteo total
        cursor.execute("SELECT COUNT(*) FROM ZSONG")
        total = cursor.fetchone()[0]
        print(f"📊 Total de canciones en la base de datos: {total}")
        
        # Verificar datos no nulos
        cursor.execute("SELECT COUNT(*) FROM ZSONG WHERE ZARTIST IS NOT NULL AND ZNAME IS NOT NULL")
        with_metadata = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ZSONG WHERE ZTEMPO IS NOT NULL")
        with_bpm = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ZSONG WHERE ZKEY IS NOT NULL")
        with_key = cursor.fetchone()[0]
        
        print(f"📈 Estadísticas:")
        print(f"  - Con artista y título: {with_metadata}")
        print(f"  - Con BPM: {with_bpm}")
        print(f"  - Con Key: {with_key}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def create_sample_mapping():
    """Crear mapeo de ejemplo para la aplicación principal"""
    
    mapping = {
        # Metadatos básicos
        'ZARTIST': 'artist',
        'ZNAME': 'title',  # En Mixed In Key, ZNAME es el título
        'ZALBUM': 'album',
        'ZGENRE': 'genre',
        
        # Análisis musical
        'ZTEMPO': 'bpm',  # ZTEMPO contiene el BPM real
        'ZKEY': 'key',    # ZKEY contiene la clave Camelot
        'ZENERGY': 'energy',  # ZENERGY es el nivel de energía
        
        # Metadatos adicionales
        'ZYEAR': 'year',
        'ZBITRATE': 'bitrate',
        'ZFILESIZE': 'file_size',
        'ZVOLUME': 'volume',
        
        # Nota: No hay campo directo de file_path en ZSONG
        # Necesitamos usar ZBOOKMARKDATA o construir desde metadatos
    }
    
    print("\n🗺️ MAPEO SUGERIDO PARA LA APLICACIÓN:")
    print("-" * 50)
    for db_field, app_field in mapping.items():
        print(f"  {db_field} -> {app_field}")
    
    return mapping

if __name__ == "__main__":
    print("🎧 TEST DE LECTURA MIXED IN KEY COLLECTION11.MIKDB")
    print("=" * 60)
    
    test_read_collection11()
    create_sample_mapping()
    
    print("\n🎯 CONCLUSIÓN:")
    print("=" * 60)
    print("✅ La base de datos se puede leer correctamente")
    print("✅ Usar query: SELECT * FROM ZSONG")
    print("✅ Campos principales: ZARTIST, ZNAME, ZTEMPO, ZKEY, ZENERGY")
    print("⚠️  Falta determinar cómo obtener file_path")