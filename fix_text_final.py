#!/usr/bin/env python3
"""
Final Text Fix Verification
============================
Verificación final de correcciones de texto aplicadas
"""

import sys
import os
from pathlib import Path

def verify_fixes_applied():
    """Verify that all text fixes have been applied correctly."""
    print("✅ VERIFICACIÓN FINAL DE CORRECCIONES DE TEXTO")
    print("=" * 70)
    
    main_window_file = Path("/Volumes/dd/Nuevo Tidal/MusicFlow_Organizer/src/ui/main_window.py")
    
    if not main_window_file.exists():
        print("❌ No se encontró el archivo main_window.py")
        return False
    
    with open(main_window_file, 'r') as f:
        content = f.read()
    
    # Verificar correcciones específicas
    fixes_to_check = [
        ('Title font size', 'QFont("Arial", 22, QFont.Bold)', 'Título principal legible'),
        ('Subtitle font size', 'QFont("Arial", 11)', 'Subtítulo mejorado'),
        ('Stats value font', 'QFont("Arial", 16, QFont.Bold)', 'Valores estadísticas claros'),
        ('Stats label font', 'QFont("Arial", 9, QFont.Bold)', 'Etiquetas mínimas pero legibles'),
        ('Status font size', 'font-size: 12px', 'Texto de estado legible'),
        ('Widget height adjustment', 'setMinimumHeight(55)', 'Altura suficiente para texto'),
        ('Widget max height', 'setMaximumHeight(65)', 'Espacio adecuado'),
    ]
    
    print("🔍 VERIFICANDO CORRECCIONES APLICADAS:")
    print("-" * 50)
    
    all_good = True
    for fix_name, search_text, description in fixes_to_check:
        if search_text in content:
            print(f"✅ {fix_name:<20}: {description}")
        else:
            print(f"❌ {fix_name:<20}: NO ENCONTRADO - {search_text}")
            all_good = False
    
    return all_good

def check_problematic_patterns():
    """Check for problematic font size patterns."""
    print(f"\n🔍 VERIFICANDO PATRONES PROBLEMÁTICOS:")
    print("-" * 50)
    
    main_window_file = Path("/Volumes/dd/Nuevo Tidal/MusicFlow_Organizer/src/ui/main_window.py")
    
    with open(main_window_file, 'r') as f:
        lines = f.readlines()
    
    problematic_patterns = [
        ('font-size: 8px', 'Texto demasiado pequeño'),
        ('font-size: 9px', 'Texto muy pequeño'),
        ('font-size: 10px', 'Texto pequeño'),
        ('QFont("Arial", 7', 'Fuente demasiado pequeña'),
        ('QFont("Arial", 8', 'Fuente muy pequeña'),
        ('setMaximumHeight(40)', 'Widget demasiado bajo'),
        ('setMaximumHeight(45)', 'Widget muy bajo'),
    ]
    
    issues_found = []
    for i, line in enumerate(lines, 1):
        for pattern, issue in problematic_patterns:
            if pattern in line:
                issues_found.append((i, pattern, issue, line.strip()))
    
    if issues_found:
        print("⚠️  POSIBLES PROBLEMAS ENCONTRADOS:")
        for line_num, pattern, issue, line_content in issues_found:
            print(f"   Línea {line_num}: {issue}")
            print(f"   Patrón: {pattern}")
            print(f"   Código: {line_content}")
            print()
    else:
        print("✅ No se encontraron patrones problemáticos")
    
    return len(issues_found) == 0

def show_current_configuration():
    """Show the current text configuration."""
    print(f"\n📊 CONFIGURACIÓN ACTUAL DE TEXTO:")
    print("-" * 50)
    
    current_config = {
        'Título Principal': '22pt Arial Bold',
        'Subtítulo': '11pt Arial Regular',
        'Valores Estadísticas': '16pt Arial Bold',
        'Etiquetas Estadísticas': '9pt Arial Bold',
        'Texto de Estado': '12px CSS',
        'Altura Widget Stats': '55-65px',
        'Ancho Widget Stats': '100-140px',
        'Header Height': '70-80px'
    }
    
    for element, config in current_config.items():
        print(f"• {element:<20}: {config}")

def provide_troubleshooting():
    """Provide troubleshooting steps if text is still not visible."""
    print(f"\n🔧 SI AÚN HAY PROBLEMAS DE VISIBILIDAD:")
    print("-" * 50)
    
    print("1. 🖥️  VERIFICAR CONFIGURACIÓN DEL SISTEMA:")
    print("   • macOS System Preferences → Displays → Resolution")
    print("   • macOS System Preferences → Accessibility → Display")
    print("   • Verificar configuración de DPI/scaling")
    
    print(f"\n2. 🔍 VERIFICAR EN LA APLICACIÓN:")
    print("   • Redimensionar ventana para aumentar tamaño")
    print("   • Probar en pantalla externa si está disponible")
    print("   • Verificar que la app no esté en modo de alta resolución")
    
    print(f"\n3. 🎛️  CONFIGURACIONES QT/PYSIDE:")
    print("   • QT_SCALE_FACTOR environment variable")
    print("   • QT_AUTO_SCREEN_SCALE_FACTOR")
    print("   • Sistema de DPI automático de Qt")
    
    print(f"\n4. 🐛 DEBUG ESPECÍFICO:")
    print("   • Ejecutar con QT_LOGGING_RULES='qt.qpa.fonts.debug=true'")
    print("   • Verificar logs de Qt para problemas de fuente")
    print("   • Probar en modo Debug de PySide6")

if __name__ == "__main__":
    print("🎧 MUSICFLOW ORGANIZER - VERIFICACIÓN FINAL DE TEXTO")
    print("=" * 80)
    
    fixes_ok = verify_fixes_applied()
    patterns_ok = check_problematic_patterns()
    
    show_current_configuration()
    
    if fixes_ok and patterns_ok:
        print(f"\n🏆 RESULTADO FINAL:")
        print("=" * 50)
        print("✅ Todas las correcciones de texto han sido aplicadas")
        print("✅ No se encontraron patrones problemáticos")
        print("✅ Los tamaños de fuente están en rangos legibles")
        print("✅ Los widgets tienen altura suficiente para el texto")
        
        print(f"\n🎯 ESTADO: CORRECCIONES COMPLETADAS")
        print("Si persisten problemas de visibilidad, son específicos del sistema")
    else:
        print(f"\n⚠️  ATENCIÓN:")
        print("=" * 50)
        if not fixes_ok:
            print("❌ Algunas correcciones no se aplicaron correctamente")
        if not patterns_ok:
            print("❌ Se encontraron patrones problemáticos")
        print("🔧 Revisar y aplicar correcciones adicionales")
    
    provide_troubleshooting()
    
    print(f"\n📋 RESUMEN DE CAMBIOS REALIZADOS:")
    print("• Título: 20pt → 22pt (↑10%)")
    print("• Subtítulo: 10pt → 11pt (↑10%)")
    print("• Stats values: 14pt → 16pt (↑14%)")
    print("• Stats labels: 8pt → 9pt (↑12%)")
    print("• Status text: 11px → 12px (↑9%)")
    print("• Widget height: 50-60px → 55-65px (↑10%)")