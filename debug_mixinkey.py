#!/usr/bin/env python3
"""
debug_mixinkey.py
================
Script de análisis aislado para entender la estructura de la base de datos Mixed In Key
y determinar cómo leer correctamente los datos.

© 2025 - Freddy Molina - BlueSystemIO
"""

import sqlite3
import os
from pathlib import Path
import json

def find_mixinkey_databases():
    """Buscar todas las bases de datos de Mixed In Key"""
    search_paths = [
        Path.home() / "Library" / "Application Support" / "Mixed In Key 11",
        Path.home() / "Library" / "Application Support" / "Mixed In Key 10",
        Path.home() / "Library" / "Application Support" / "Mixed In Key Live",
        Path.home() / "Library" / "Application Support" / "Mixedinkey",
    ]
    
    found_dbs = []
    
    for search_path in search_paths:
        if search_path.exists():
            print(f"🔍 Buscando en: {search_path}")
            for db_file in search_path.rglob("*.mikdb"):
                found_dbs.append(db_file)
                print(f"  ✅ Encontrado: {db_file.name}")
    
    return found_dbs

def analyze_database_structure(db_path):
    """Analizar la estructura completa de una base de datos SQLite"""
    print(f"\n📊 ANALIZANDO: {db_path}")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 1. Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tablas encontradas: {tables}")
        
        # 2. Analizar cada tabla
        for table_name in tables:
            print(f"\n🔍 TABLA: {table_name}")
            print("-" * 40)
            
            # Schema de la tabla
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            print("📝 Columnas:")
            for col in columns_info:
                col_id, col_name, col_type, not_null, default_val, is_pk = col
                pk_marker = " (PK)" if is_pk else ""
                print(f"  - {col_name}: {col_type}{pk_marker}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"📊 Número de registros: {row_count}")
            
            # Mostrar algunos ejemplos si hay datos
            if row_count > 0:
                print("📄 Ejemplos de datos (primeros 3 registros):")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_rows = cursor.fetchall()
                column_names = [col[1] for col in columns_info]
                
                for i, row in enumerate(sample_rows, 1):
                    print(f"  Registro {i}:")
                    for col_name, value in zip(column_names, row):
                        # Truncar valores largos para mejor legibilidad
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        print(f"    {col_name}: {value}")
                    print()
        
        # 3. Buscar campos clave para Mixed In Key
        print("\n🎵 BÚSQUEDA DE CAMPOS MUSICALES:")
        print("-" * 40)
        
        music_fields = ['bpm', 'key', 'energy', 'artist', 'title', 'album', 'filepath', 'directory', 'filename']
        
        for table_name in tables:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1].lower() for col in cursor.fetchall()]
            
            found_fields = []
            for field in music_fields:
                matches = [col for col in columns if field in col.lower()]
                if matches:
                    found_fields.extend(matches)
            
            if found_fields:
                print(f"  Tabla '{table_name}': {found_fields}")
        
        # 4. Intentar queries específicas para encontrar datos musicales
        print("\n🎯 INTENTANDO QUERIES ESPECÍFICAS:")
        print("-" * 40)
        
        test_queries = [
            "SELECT * FROM Music LIMIT 1",
            "SELECT * FROM Tracks LIMIT 1", 
            "SELECT * FROM Files LIMIT 1",
            "SELECT * FROM Library LIMIT 1"
        ]
        
        for query in test_queries:
            try:
                cursor.execute(query)
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    print(f"  ✅ {query}")
                    print(f"     Columnas: {columns}")
                    print(f"     Datos: {result[:5]}...")  # Primeros 5 campos
                else:
                    print(f"  ⚠️  {query} - Sin datos")
            except sqlite3.Error as e:
                print(f"  ❌ {query} - Error: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analizando {db_path}: {e}")

def main():
    print("🎧 ANÁLISIS DE BASE DE DATOS MIXED IN KEY")
    print("=" * 80)
    
    # Buscar bases de datos
    databases = find_mixinkey_databases()
    
    if not databases:
        print("❌ No se encontraron bases de datos Mixed In Key")
        return
    
    print(f"\n📊 Se encontraron {len(databases)} base(s) de datos")
    
    # Analizar cada base de datos
    for db_path in databases:
        analyze_database_structure(db_path)
    
    print("\n🎯 ANÁLISIS COMPLETADO")
    print("=" * 80)
    print("Con esta información podemos crear el mapeo correcto para la aplicación principal.")

if __name__ == "__main__":
    main()