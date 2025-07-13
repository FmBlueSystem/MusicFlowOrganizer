#!/usr/bin/env python3
"""
Text Issues Diagnostic and Fix
==============================
Identificar y corregir problemas específicos de texto en la UI
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def diagnose_common_text_issues():
    """Diagnose common text issues in Qt applications."""
    print("🔍 DIAGNÓSTICO DE PROBLEMAS DE TEXTO")
    print("=" * 60)
    
    common_issues = [
        {
            'issue': 'Texto cortado en botones',
            'locations': ['Menu items', 'Action buttons', 'Tab headers'],
            'causes': ['Font metrics variation', 'Fixed width containers', 'Platform differences'],
            'symptoms': ['Text appears with "..." at end', 'Buttons too small for content', 'Overlap with other elements']
        },
        {
            'issue': 'Text overflow en tabla',
            'locations': ['Table cells', 'Column headers', 'Status messages'],
            'causes': ['Column width too small', 'Long file names', 'Variable font rendering'],
            'symptoms': ['Text spills outside cell', 'Horizontal scrollbar needed', 'Overlapping columns']
        },
        {
            'issue': 'Dialog text truncation',
            'locations': ['Message boxes', 'Confirmation dialogs', 'Progress dialogs'],
            'causes': ['Fixed dialog size', 'Long messages', 'Small screen resolution'],
            'symptoms': ['Message cut off', 'OK/Cancel buttons not visible', 'Text wrapping issues']
        },
        {
            'issue': 'Window title overflow',
            'locations': ['Main window title bar', 'Dialog titles'],
            'causes': ['Title too long', 'Window too narrow', 'System title bar constraints'],
            'symptoms': ['Title truncated with ...', 'Important info lost', 'Looks unprofessional']
        }
    ]
    
    for i, issue in enumerate(common_issues, 1):
        print(f"\n{i}. {issue['issue'].upper()}")
        print(f"   Ubicaciones: {', '.join(issue['locations'])}")
        print(f"   Causas: {', '.join(issue['causes'])}")
        print(f"   Síntomas: {', '.join(issue['symptoms'])}")
    
    return common_issues

def check_current_text_settings():
    """Check current text and font settings."""
    print(f"\n⚙️  CONFIGURACIÓN ACTUAL DE TEXTO")
    print("=" * 60)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QFont, QFontMetrics
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Check system font
        system_font = QApplication.font()
        font_metrics = QFontMetrics(system_font)
        
        print(f"Font Family: {system_font.family()}")
        print(f"Font Size: {system_font.pointSize()}pt")
        print(f"Font Weight: {system_font.weight()}")
        print(f"Font Style: {'Italic' if system_font.italic() else 'Normal'}")
        
        # Test text measurements
        test_texts = [
            "🎧 MusicFlow Organizer - DJ Library Management",
            "🤖 AI Enhance Selected Tracks", 
            "Very Long Song Name That Could Cause Display Issues.mp3",
            "Progressive House/Trance",
            "Mixed In Key Analyzed"
        ]
        
        print(f"\n📏 TEXT MEASUREMENTS:")
        for text in test_texts:
            width = font_metrics.horizontalAdvance(text)
            height = font_metrics.height()
            print(f"   '{text[:30]}...' = {width}px x {height}px")
            
    except Exception as e:
        print(f"❌ Error checking font settings: {e}")

def suggest_specific_fixes():
    """Suggest specific fixes for the text issues."""
    print(f"\n🔧 FIXES ESPECÍFICOS RECOMENDADOS")
    print("=" * 60)
    
    fixes = [
        {
            'problem': 'Títulos de ventana muy largos',
            'fix': 'Usar títulos más cortos y descriptivos',
            'code': 'setWindowTitle("🎧 MusicFlow - DJ Tools")'
        },
        {
            'problem': 'Botones con texto cortado',
            'fix': 'Ajustar tamaño automáticamente o usar iconos',
            'code': 'button.adjustSize() o button.setMinimumSize()'
        },
        {
            'problem': 'Columnas de tabla muy estrechas',
            'fix': 'Usar setSectionResizeMode(QHeaderView.ResizeToContents)',
            'code': 'table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)'
        },
        {
            'problem': 'Dialogs con texto cortado',
            'fix': 'Usar QScrollArea o ajustar tamaño dinámicamente',
            'code': 'dialog.resize(dialog.sizeHint())'
        },
        {
            'problem': 'Status bar overflow',
            'fix': 'Usar elided text con QFontMetrics.elidedText()',
            'code': 'elidedText = font_metrics.elidedText(text, Qt.ElideRight, width)'
        }
    ]
    
    for i, fix in enumerate(fixes, 1):
        print(f"{i}. {fix['problem']}")
        print(f"   Solución: {fix['fix']}")
        print(f"   Código: {fix['code']}")
        print()

def create_text_fix_recommendations():
    """Create specific recommendations based on MusicFlow layout."""
    print(f"\n🎯 RECOMENDACIONES PARA MUSICFLOW")
    print("=" * 60)
    
    print("PRIORITY FIXES:")
    print("1. ✅ IMPLEMENTED - Column widths increased")
    print("2. ✅ IMPLEMENTED - File name truncation with tooltips") 
    print("3. ✅ IMPLEMENTED - Shorter button/menu text")
    print("4. ✅ IMPLEMENTED - Responsive window sizing")
    print("5. ✅ IMPLEMENTED - Enhanced dialog sizing")
    
    print(f"\nADDITIONAL IMPROVEMENTS:")
    print("• Use QFontMetrics.elidedText() for dynamic truncation")
    print("• Add word wrapping where appropriate")
    print("• Implement auto-sizing for containers")
    print("• Use rich text formatting for complex layouts")
    print("• Add horizontal scrollbars as fallback")
    
    print(f"\nIF STILL HAVING ISSUES:")
    print("• Check system DPI scaling settings")
    print("• Verify font rendering on different macOS versions")
    print("• Test with different system fonts")
    print("• Consider using fixed-width fonts for tables")
    print("• Add style sheets for precise control")

if __name__ == "__main__":
    print("🔍 MUSICFLOW ORGANIZER - TEXT ISSUES DIAGNOSTIC")
    print("=" * 80)
    
    issues = diagnose_common_text_issues()
    check_current_text_settings()
    suggest_specific_fixes()
    create_text_fix_recommendations()
    
    print("\n📋 NEXT STEPS:")
    print("=" * 80)
    print("1. Identify the specific text problem from the image")
    print("2. Apply targeted fix from recommendations above")
    print("3. Test fix with different screen resolutions")
    print("4. Verify fix doesn't break other UI elements")
    print("5. Update layout validation tests")
    
    print(f"\n💡 Para problemas específicos, puedes:")
    print("• Describir exactamente qué texto se ve cortado")
    print("• Indicar en qué parte de la UI ocurre")
    print("• Mencionar tu resolución de pantalla")
    print("• Especificar si es en ventana normal o maximizada")