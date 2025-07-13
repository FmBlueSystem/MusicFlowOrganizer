#!/usr/bin/env python3
"""
UI Layout Validation Test
=========================
Detectar problemas de tamaño, texto que se sale y layout issues
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QDialog, QMessageBox
from PySide6.QtCore import QSize
from PySide6.QtGui import QFontMetrics, QFont

def test_text_overflow_issues():
    """Test for text overflow and sizing issues."""
    print("🔍 UI LAYOUT VALIDATION")
    print("=" * 50)
    
    # Create minimal app for font metrics
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Test problematic texts
    problematic_texts = [
        {
            'type': 'Window Title',
            'text': '🎧 MusicFlow Organizer - DJ Library Management',  # Updated shorter title
            'max_width': 1400
        },
        {
            'type': 'Dialog Title',
            'text': 'AI Enhancement Confirmation',
            'max_width': 400
        },
        {
            'type': 'Button Text',
            'text': '🤖 AI Enhance',  # Updated shorter text
            'max_width': 250
        },
        {
            'type': 'Status Message',
            'text': 'Successfully enhanced 15 out of 20 tracks with AI-powered genre classification',
            'max_width': 600
        },
        {
            'type': 'Column Header',
            'text': 'MixIn Key',
            'max_width': 100
        },
        {
            'type': 'File Name',
            'text': 'Very Long Song Name That Could Cause Display Issues - Artist Name (Extended Remix Version).flac',
            'max_width': 280  # Now fits in table (will be truncated with ellipsis)
        }
    ]
    
    font = QFont()
    font_metrics = QFontMetrics(font)
    
    print("📊 TEXT OVERFLOW ANALYSIS:")
    print("-" * 60)
    print(f"{'Type':<15} {'Width':<6} {'Max':<6} {'Status':<10} {'Text Preview':<30}")
    print("-" * 60)
    
    issues_found = []
    
    for item in problematic_texts:
        text_width = font_metrics.horizontalAdvance(item['text'])
        max_width = item['max_width']
        status = "❌ OVERFLOW" if text_width > max_width else "✅ OK"
        
        if text_width > max_width:
            issues_found.append(item)
        
        preview = item['text'][:27] + "..." if len(item['text']) > 30 else item['text']
        
        print(f"{item['type']:<15} {text_width:<6} {max_width:<6} {status:<10} {preview:<30}")
    
    print()
    return issues_found

def test_table_column_sizing():
    """Test table column sizing issues."""
    print("📋 TABLE COLUMN ANALYSIS:")
    print("-" * 40)
    
    columns = [
        {'name': 'File', 'content_sample': 'Very Long Song Name - Artist (Remix).flac', 'min_width': 280},  # Updated
        {'name': 'Genre', 'content_sample': 'Progressive House', 'min_width': 135},  # Updated
        {'name': 'BPM', 'content_sample': '128.45', 'min_width': 65},   # Updated
        {'name': 'Key', 'content_sample': '7A', 'min_width': 45},       # Updated
        {'name': 'Energy', 'content_sample': '8', 'min_width': 65},     # Updated
        {'name': 'MixIn Key', 'content_sample': 'Analyzed', 'min_width': 80}
    ]
    
    app = QApplication.instance()
    font = QFont()
    font_metrics = QFontMetrics(font)
    
    table_issues = []
    
    for col in columns:
        header_width = font_metrics.horizontalAdvance(col['name'])
        content_width = font_metrics.horizontalAdvance(col['content_sample'])
        required_width = max(header_width, content_width) + 20  # padding
        
        if required_width > col['min_width']:
            table_issues.append({
                'column': col['name'],
                'required': required_width,
                'allocated': col['min_width'],
                'overflow': required_width - col['min_width']
            })
        
        status = "❌" if required_width > col['min_width'] else "✅"
        print(f"{status} {col['name']:<10}: needs {required_width}px, has {col['min_width']}px")
    
    return table_issues

def test_dialog_sizing():
    """Test dialog sizing issues."""
    print("\n💬 DIALOG SIZING ANALYSIS:")
    print("-" * 40)
    
    dialogs = [
        {
            'name': 'AI Enhancement Confirmation',
            'content': 'Enhance 15 track(s) with OpenAI GPT-4?\n\nThis will analyze:\n• Genre classification\n• Mood detection\n• Language/Region identification\n\nNote: This requires an internet connection and uses your OpenAI API key.',
            'min_size': (500, 250)  # Updated size
        },
        {
            'name': 'Duplicate Tracks Dialog',
            'content': 'Found 25 groups of duplicate tracks:\n\nGroup 1:\n- /very/long/path/to/music/file/Song Name.mp3\n- /another/very/long/path/Song Name (Copy).mp3',
            'min_size': (600, 400)
        }
    ]
    
    dialog_issues = []
    
    for dialog in dialogs:
        lines = dialog['content'].split('\n')
        max_line_length = max(len(line) for line in lines)
        estimated_width = max_line_length * 8  # rough estimate
        estimated_height = len(lines) * 20 + 100  # rough estimate
        
        min_width, min_height = dialog['min_size']
        
        width_ok = estimated_width <= min_width
        height_ok = estimated_height <= min_height
        
        status = "✅" if width_ok and height_ok else "❌"
        print(f"{status} {dialog['name']}")
        print(f"    Estimated: {estimated_width}x{estimated_height}")
        print(f"    Allocated: {min_width}x{min_height}")
        
        if not width_ok or not height_ok:
            dialog_issues.append(dialog)
    
    return dialog_issues

def suggest_fixes(text_issues, table_issues, dialog_issues):
    """Suggest fixes for identified issues."""
    print("\n🔧 SUGGESTED FIXES:")
    print("=" * 50)
    
    if text_issues:
        print("📝 Text Overflow Fixes:")
        for issue in text_issues:
            if issue['type'] == 'Window Title':
                print("   • Shorten window title: '🎧 MusicFlow Organizer - DJ Library'")
            elif issue['type'] == 'Button Text':
                print("   • Use shorter button text: '🤖 AI Enhance'")
            elif issue['type'] == 'File Name':
                print("   • Truncate long filenames with ellipsis")
            elif issue['type'] == 'Status Message':
                print("   • Break long status messages into multiple lines")
    
    if table_issues:
        print("\n📋 Table Column Fixes:")
        for issue in table_issues:
            print(f"   • {issue['column']}: increase width by {issue['overflow']}px")
    
    if dialog_issues:
        print("\n💬 Dialog Sizing Fixes:")
        for issue in dialog_issues:
            print(f"   • {issue['name']}: increase dialog size or add scrolling")
    
    # Responsive design suggestions
    print("\n📱 Responsive Design Suggestions:")
    print("   • Implement dynamic sizing based on screen resolution")
    print("   • Add horizontal scrollbars for tables when needed")
    print("   • Use word-wrap for long text elements")
    print("   • Implement collapsible sections for smaller screens")

if __name__ == "__main__":
    print("🔍 MusicFlow Organizer - UI Layout Validation")
    print("=" * 60)
    
    text_issues = test_text_overflow_issues()
    table_issues = test_table_column_sizing()
    dialog_issues = test_dialog_sizing()
    
    total_issues = len(text_issues) + len(table_issues) + len(dialog_issues)
    
    if total_issues > 0:
        print(f"\n⚠️  FOUND {total_issues} UI LAYOUT ISSUES")
        suggest_fixes(text_issues, table_issues, dialog_issues)
    else:
        print("\n✅ NO UI LAYOUT ISSUES FOUND")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Text overflow issues: {len(text_issues)}")
    print(f"   Table sizing issues: {len(table_issues)}")
    print(f"   Dialog sizing issues: {len(dialog_issues)}")