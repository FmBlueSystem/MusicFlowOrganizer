#!/usr/bin/env python3
"""
MusicFlow Organizer - Master Test Runner 360°
============================================
Ejecuta todas las pruebas comprehensivas y genera un reporte maestro completo.

PRIORIDAD: MÁXIMA - Validación completa del sistema para uso profesional

Author: Claude Code
Date: 2025-07-13
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime

class MasterTestRunner360:
    """
    Master test runner that executes all 360° test suites
    and generates comprehensive quality report.
    """
    
    def __init__(self):
        self.test_suites = [
            {
                'name': 'Performance & Load Testing',
                'file': 'performance_load_test.py',
                'priority': 'CRITICAL',
                'category': 'Performance'
            },
            {
                'name': 'Error Recovery & Resilience Testing',
                'file': 'error_recovery_resilience_test.py',
                'priority': 'CRITICAL',
                'category': 'Stability'
            },
            {
                'name': 'Audio Compatibility Testing',
                'file': 'audio_compatibility_test.py',
                'priority': 'HIGH',
                'category': 'Compatibility'
            },
            {
                'name': 'Security & Data Integrity Testing',
                'file': 'security_data_integrity_test.py',
                'priority': 'CRITICAL',
                'category': 'Security'
            },
            {
                'name': 'UI Synchronization & Integration Testing',
                'file': 'ui_synchronization_test.py',
                'priority': 'CRITICAL',
                'category': 'UI/UX'
            },
            {
                'name': 'User Workflow End-to-End Testing',
                'file': 'user_workflow_test.py',
                'priority': 'CRITICAL',
                'category': 'Workflows'
            },
            {
                'name': 'DJ Engine Plugin Complete Testing',
                'file': 'dj_engine_complete_test.py',
                'priority': 'HIGH',
                'category': 'Features'
            },
            {
                'name': 'Cross-Platform & Environment Testing',
                'file': 'cross_platform_environment_test.py',
                'priority': 'MEDIUM',
                'category': 'Compatibility'
            },
            {
                'name': 'Usability & UX Testing',
                'file': 'usability_ux_test.py',
                'priority': 'MEDIUM',
                'category': 'UI/UX'
            }
        ]
        
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        self.logger = logging.getLogger("MasterTestRunner360")
        
        # Test execution statistics
        self.statistics = {
            'total_suites': len(self.test_suites),
            'executed_suites': 0,
            'passed_suites': 0,
            'failed_suites': 0,
            'error_suites': 0,
            'skipped_suites': 0,
            'total_execution_time': 0
        }
        
        # Categories for analysis
        self.categories = {
            'Performance': {'suites': 0, 'passed': 0, 'score': 0},
            'Stability': {'suites': 0, 'passed': 0, 'score': 0},
            'Security': {'suites': 0, 'passed': 0, 'score': 0},
            'UI/UX': {'suites': 0, 'passed': 0, 'score': 0},
            'Workflows': {'suites': 0, 'passed': 0, 'score': 0},
            'Features': {'suites': 0, 'passed': 0, 'score': 0},
            'Compatibility': {'suites': 0, 'passed': 0, 'score': 0}
        }
        
    def run_all_tests_360(self):
        """Execute all 360° test suites."""
        print("🚀 MUSICFLOW ORGANIZER - MASTER TEST RUNNER 360°")
        print("=" * 80)
        print("🎯 Ejecutando validación completa del sistema para uso profesional de DJ")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Plataforma: {sys.platform}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # Execute each test suite
        for suite in self.test_suites:
            print(f"\n{'=' * 80}")
            print(f"🧪 EJECUTANDO: {suite['name']}")
            print(f"📁 Archivo: {suite['file']}")
            print(f"⚡ Prioridad: {suite['priority']}")
            print(f"📊 Categoría: {suite['category']}")
            print("-" * 80)
            
            result = self._execute_test_suite(suite)
            self.test_results[suite['name']] = result
            
            # Update statistics
            self.statistics['executed_suites'] += 1
            
            if result['status'] == 'PASS':
                self.statistics['passed_suites'] += 1
                self.categories[suite['category']]['passed'] += 1
            elif result['status'] == 'FAIL':
                self.statistics['failed_suites'] += 1
            elif result['status'] == 'ERROR':
                self.statistics['error_suites'] += 1
            elif result['status'] == 'SKIPPED':
                self.statistics['skipped_suites'] += 1
            
            self.categories[suite['category']]['suites'] += 1
            
            # Brief pause between suites
            time.sleep(1)
        
        self.end_time = time.time()
        self.statistics['total_execution_time'] = self.end_time - self.start_time
        
        # Generate master report
        self._generate_master_report()
    
    def _execute_test_suite(self, suite: Dict[str, str]) -> Dict[str, Any]:
        """Execute a single test suite and capture results."""
        test_file = Path(suite['file'])
        
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return {
                'status': 'ERROR',
                'error': 'Test file not found',
                'execution_time': 0
            }
        
        try:
            suite_start_time = time.time()
            
            # Execute test suite
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per suite
            )
            
            suite_end_time = time.time()
            execution_time = suite_end_time - suite_start_time
            
            # Parse results from output
            output = result.stdout
            error_output = result.stderr
            
            # Extract test results
            test_status = self._parse_test_status(output)
            test_score = self._extract_test_score(output)
            
            # Determine overall status
            if result.returncode == 0 and test_status in ['PASS', 'EXCELLENT', 'GOOD']:
                status = 'PASS'
            elif test_status == 'SKIPPED':
                status = 'SKIPPED'
            elif result.returncode != 0 or test_status in ['FAIL', 'POOR']:
                status = 'FAIL'
            else:
                status = 'ERROR'
            
            # Extract summary information
            summary = self._extract_summary(output)
            
            return {
                'status': status,
                'execution_time': execution_time,
                'return_code': result.returncode,
                'test_score': test_score,
                'summary': summary,
                'output_preview': output[-1000:] if len(output) > 1000 else output,
                'error_output': error_output[-500:] if error_output else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'ERROR',
                'error': 'Test suite timeout (>5 minutes)',
                'execution_time': 300
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'execution_time': 0
            }
    
    def _parse_test_status(self, output: str) -> str:
        """Parse test status from output."""
        output_upper = output.upper()
        
        # Look for verdict patterns
        if 'EXCELLENT' in output_upper and 'VERDICT' in output_upper:
            return 'EXCELLENT'
        elif 'GOOD' in output_upper and 'VERDICT' in output_upper:
            return 'GOOD'
        elif 'FAIR' in output_upper and 'VERDICT' in output_upper:
            return 'FAIR'
        elif 'POOR' in output_upper and 'VERDICT' in output_upper:
            return 'POOR'
        elif 'PASS' in output_upper:
            return 'PASS'
        elif 'FAIL' in output_upper:
            return 'FAIL'
        elif 'SKIPPED' in output_upper:
            return 'SKIPPED'
        
        return 'UNKNOWN'
    
    def _extract_test_score(self, output: str) -> float:
        """Extract test score from output."""
        import re
        
        # Look for score patterns
        score_patterns = [
            r'score:\s*(\d+\.?\d*)%',
            r'(\d+\.?\d*)%\s*\)',
            r'Tests Passed:\s*\d+/\d+\s*\((\d+\.?\d*)%\)',
            r'success_rate:\s*(\d+\.?\d*)'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        
        return 0.0
    
    def _extract_summary(self, output: str) -> str:
        """Extract summary information from output."""
        lines = output.split('\n')
        summary_lines = []
        
        # Look for summary sections
        in_summary = False
        for line in lines:
            if any(keyword in line.upper() for keyword in ['SUMMARY', 'VERDICT', 'REPORT']):
                in_summary = True
            
            if in_summary and line.strip():
                summary_lines.append(line)
                
                # Stop after collecting reasonable summary
                if len(summary_lines) > 10:
                    break
        
        return '\n'.join(summary_lines[-10:]) if summary_lines else 'No summary available'
    
    def _generate_master_report(self):
        """Generate comprehensive master test report."""
        print(f"\n{'=' * 80}")
        print("📊 GENERANDO REPORTE MAESTRO 360°")
        print("=" * 80)
        
        # Calculate overall metrics
        overall_success_rate = (
            self.statistics['passed_suites'] / self.statistics['total_suites'] * 100
            if self.statistics['total_suites'] > 0 else 0
        )
        
        # Calculate category scores
        for category, data in self.categories.items():
            if data['suites'] > 0:
                data['score'] = (data['passed'] / data['suites']) * 100
        
        # Generate report sections
        self._print_executive_summary(overall_success_rate)
        self._print_test_suite_results()
        self._print_category_analysis()
        self._print_critical_findings()
        self._print_performance_metrics()
        self._print_final_verdict(overall_success_rate)
        self._save_detailed_report()
    
    def _print_executive_summary(self, overall_success_rate: float):
        """Print executive summary."""
        print(f"\n🎯 RESUMEN EJECUTIVO")
        print("=" * 80)
        print(f"📅 Fecha de prueba: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Tiempo total de ejecución: {self._format_time(self.statistics['total_execution_time'])}")
        print(f"📊 Suites ejecutadas: {self.statistics['executed_suites']}/{self.statistics['total_suites']}")
        print(f"✅ Suites exitosas: {self.statistics['passed_suites']}")
        print(f"❌ Suites fallidas: {self.statistics['failed_suites']}")
        print(f"💥 Suites con error: {self.statistics['error_suites']}")
        print(f"⏭️  Suites omitidas: {self.statistics['skipped_suites']}")
        print(f"\n🎯 TASA DE ÉXITO GLOBAL: {overall_success_rate:.1f}%")
        
        # Quality bar visualization
        self._print_quality_bar(overall_success_rate)
    
    def _print_quality_bar(self, percentage: float):
        """Print visual quality bar."""
        bar_length = 50
        filled_length = int(bar_length * percentage / 100)
        
        if percentage >= 90:
            color = "🟩"
        elif percentage >= 75:
            color = "🟨"
        elif percentage >= 60:
            color = "🟧"
        else:
            color = "🟥"
        
        bar = color * filled_length + "⬜" * (bar_length - filled_length)
        print(f"\n[{bar}] {percentage:.1f}%")
    
    def _print_test_suite_results(self):
        """Print individual test suite results."""
        print(f"\n📋 RESULTADOS POR SUITE DE PRUEBAS")
        print("=" * 80)
        print(f"{'Suite':<40} {'Status':<12} {'Score':<10} {'Time':<10} {'Priority':<10}")
        print("-" * 80)
        
        for suite in self.test_suites:
            name = suite['name']
            result = self.test_results.get(name, {})
            
            status = result.get('status', 'UNKNOWN')
            score = result.get('test_score', 0)
            exec_time = result.get('execution_time', 0)
            priority = suite['priority']
            
            # Status icon
            status_icon = {
                'PASS': '✅',
                'FAIL': '❌',
                'ERROR': '💥',
                'SKIPPED': '⏭️',
                'UNKNOWN': '❓'
            }.get(status, '❓')
            
            # Format row
            name_short = name[:37] + "..." if len(name) > 40 else name
            status_str = f"{status_icon} {status}"
            score_str = f"{score:.1f}%" if score > 0 else "N/A"
            time_str = self._format_time(exec_time)
            
            print(f"{name_short:<40} {status_str:<12} {score_str:<10} {time_str:<10} {priority:<10}")
    
    def _print_category_analysis(self):
        """Print analysis by category."""
        print(f"\n📊 ANÁLISIS POR CATEGORÍA")
        print("=" * 80)
        print(f"{'Categoría':<20} {'Suites':<10} {'Exitosas':<10} {'Tasa':<10} {'Estado':<20}")
        print("-" * 80)
        
        for category, data in sorted(self.categories.items(), 
                                    key=lambda x: x[1]['score'], 
                                    reverse=True):
            if data['suites'] > 0:
                rate = data['score']
                
                # Status determination
                if rate >= 90:
                    status = "🟢 Excelente"
                elif rate >= 75:
                    status = "🟡 Bueno"
                elif rate >= 60:
                    status = "🟠 Regular"
                else:
                    status = "🔴 Crítico"
                
                print(f"{category:<20} {data['suites']:<10} {data['passed']:<10} "
                      f"{rate:.1f}%{'':<6} {status:<20}")
    
    def _print_critical_findings(self):
        """Print critical findings and issues."""
        print(f"\n⚠️  HALLAZGOS CRÍTICOS")
        print("=" * 80)
        
        critical_issues = []
        
        # Analyze failed tests with CRITICAL priority
        for suite in self.test_suites:
            if suite['priority'] == 'CRITICAL':
                result = self.test_results.get(suite['name'], {})
                if result.get('status') in ['FAIL', 'ERROR']:
                    critical_issues.append({
                        'suite': suite['name'],
                        'category': suite['category'],
                        'status': result.get('status'),
                        'error': result.get('error', 'Test failed')
                    })
        
        if critical_issues:
            print("🚨 Se encontraron los siguientes problemas críticos:\n")
            for i, issue in enumerate(critical_issues, 1):
                print(f"{i}. {issue['suite']} ({issue['category']})")
                print(f"   Estado: {issue['status']}")
                print(f"   Detalle: {issue['error']}")
                print()
        else:
            print("✅ No se encontraron problemas críticos en las pruebas prioritarias")
    
    def _print_performance_metrics(self):
        """Print performance metrics."""
        print(f"\n⚡ MÉTRICAS DE RENDIMIENTO")
        print("=" * 80)
        
        # Find performance-related results
        perf_suite = next((s for s in self.test_suites if 'Performance' in s['name']), None)
        if perf_suite:
            result = self.test_results.get(perf_suite['name'], {})
            print(f"Suite de rendimiento: {result.get('status', 'UNKNOWN')}")
            if result.get('summary'):
                print("\nResumen de rendimiento:")
                print(result['summary'][-500:])  # Last 500 chars of summary
    
    def _print_final_verdict(self, overall_success_rate: float):
        """Print final system verdict."""
        print(f"\n🏆 VEREDICTO FINAL DEL SISTEMA")
        print("=" * 80)
        
        # Determine overall system quality
        if overall_success_rate >= 95:
            verdict = "EXCEPCIONAL"
            emoji = "🥇"
            recommendation = "Sistema listo para producción profesional sin reservas"
        elif overall_success_rate >= 85:
            verdict = "EXCELENTE"
            emoji = "🥈"
            recommendation = "Sistema listo para producción con ajustes menores"
        elif overall_success_rate >= 75:
            verdict = "BUENO"
            emoji = "🥉"
            recommendation = "Sistema funcional pero requiere optimizaciones"
        elif overall_success_rate >= 60:
            verdict = "ACEPTABLE"
            emoji = "⚠️"
            recommendation = "Sistema necesita mejoras significativas"
        else:
            verdict = "INSUFICIENTE"
            emoji = "🚫"
            recommendation = "Sistema NO recomendado para uso profesional"
        
        print(f"\n{emoji} CALIDAD DEL SISTEMA: {verdict}")
        print(f"📊 Puntuación Global: {overall_success_rate:.1f}%")
        print(f"💡 Recomendación: {recommendation}")
        
        # Professional DJ readiness assessment
        print(f"\n🎧 EVALUACIÓN PARA USO PROFESIONAL DE DJ:")
        
        critical_categories = ['Performance', 'Stability', 'Security', 'Workflows']
        critical_scores = [self.categories[cat]['score'] for cat in critical_categories 
                          if cat in self.categories and self.categories[cat]['suites'] > 0]
        
        if critical_scores:
            critical_average = sum(critical_scores) / len(critical_scores)
            
            if critical_average >= 90:
                print("✅ APTO para uso profesional intensivo en eventos")
            elif critical_average >= 80:
                print("✅ APTO para uso profesional con precauciones")
            elif critical_average >= 70:
                print("⚠️  USO PROFESIONAL con limitaciones conocidas")
            else:
                print("❌ NO APTO para uso profesional en este momento")
        
        # Certification statement
        print(f"\n📜 CERTIFICACIÓN DE CALIDAD 360°")
        print(f"Este sistema ha sido evaluado comprehensivamente en {self.statistics['total_suites']} "
              f"dimensiones críticas")
        print(f"con un total de {self.statistics['executed_suites']} suites de pruebas ejecutadas.")
        print(f"\nFirmado digitalmente: MusicFlow QA System")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _format_time(self, seconds: float) -> str:
        """Format time in human-readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    def _save_detailed_report(self):
        """Save detailed report to file."""
        report_file = f"musicflow_360_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'platform': sys.platform,
                'python_version': sys.version,
                'total_execution_time': self.statistics['total_execution_time']
            },
            'statistics': self.statistics,
            'categories': self.categories,
            'test_results': self.test_results,
            'overall_success_rate': (
                self.statistics['passed_suites'] / self.statistics['total_suites'] * 100
                if self.statistics['total_suites'] > 0 else 0
            )
        }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Reporte detallado guardado en: {report_file}")
        except Exception as e:
            print(f"\n❌ Error guardando reporte: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Iniciando Master Test Runner 360°...")
    print("🎯 MusicFlow Organizer - Validación Completa del Sistema")
    
    runner = MasterTestRunner360()
    runner.run_all_tests_360()
    
    print(f"\n{'=' * 80}")
    print("🏁 PRUEBAS 360° COMPLETADAS")
    print("=" * 80)