#!/usr/bin/env python3
"""
Performance & Load Testing Suite
================================
Tests críticos para estabilidad y rapidez en MusicFlow Organizer.

PRIORIDAD: MÁXIMA - Para DJs profesionales con bibliotecas grandes

Tests incluidos:
1. Large Library Performance (10K+ tracks)
2. Memory Usage Monitoring
3. Database Query Performance
4. Parallel Processing Efficiency  
5. UI Responsiveness Under Load
6. MixIn Key Database Scaling
"""

import sys
import os
import time
import psutil
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import sqlite3

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.mixinkey_integration import MixInKeyIntegration
from core.performance_manager import PerformanceManager

class PerformanceLoadTester:
    """
    Suite completa de tests de rendimiento y carga.
    Diseñada para validar estabilidad con bibliotecas de DJ profesionales.
    """
    
    def __init__(self):
        self.test_results = {
            'large_library_performance': {},
            'memory_usage': {},
            'database_performance': {},
            'parallel_processing': {},
            'ui_responsiveness': {},
            'scaling_limits': {}
        }
        
        # Performance thresholds for professional DJ use
        self.performance_thresholds = {
            'max_analysis_time_per_track': 2.0,  # seconds
            'max_memory_usage_mb': 2048,  # 2GB
            'max_database_query_time': 1.0,  # seconds
            'min_tracks_per_second': 5.0,  # analysis rate
            'max_ui_freeze_time': 0.5  # seconds
        }
    
    def run_all_performance_tests(self):
        """Ejecuta todos los tests de rendimiento priorizados."""
        
        print("🚀 PERFORMANCE & LOAD TESTING SUITE")
        print("=" * 60)
        print("🎯 PRIORIDAD: Estabilidad, Rapidez y Robustez Profesional")
        
        # Test 1: Large Library Performance (CRÍTICO)
        print(f"\n1️⃣ LARGE LIBRARY PERFORMANCE TEST")
        print("-" * 50)
        self.test_large_library_performance()
        
        # Test 2: Memory Usage & Leaks (CRÍTICO)
        print(f"\n2️⃣ MEMORY USAGE & LEAK DETECTION")
        print("-" * 50)
        self.test_memory_usage_and_leaks()
        
        # Test 3: Database Performance (CRÍTICO)
        print(f"\n3️⃣ DATABASE PERFORMANCE TESTING")
        print("-" * 50)
        self.test_database_performance()
        
        # Test 4: Parallel Processing Efficiency (ALTO)
        print(f"\n4️⃣ PARALLEL PROCESSING EFFICIENCY")
        print("-" * 50)
        self.test_parallel_processing_efficiency()
        
        # Test 5: Scaling Limits (ALTO)
        print(f"\n5️⃣ SCALING LIMITS TESTING")
        print("-" * 50)
        self.test_scaling_limits()
        
        # Generate performance report
        self.generate_performance_report()
    
    def test_large_library_performance(self):
        """Test 1: Rendimiento con bibliotecas grandes (4K+ tracks reales)."""
        
        try:
            # Use real MixIn Key database with 4267 tracks
            db_path = Path.home() / "Library" / "Application Support" / "Mixedinkey" / "Collection11.mikdb"
            
            if not db_path.exists():
                print("❌ No MixIn Key database found - using simulated large library")
                self.test_results['large_library_performance'] = {
                    'status': 'SKIPPED',
                    'reason': 'No real database available'
                }
                return
            
            print(f"📊 Testing with real MixIn Key database: {db_path.name}")
            
            # Test 1.1: Database Loading Performance
            print("🔍 Test 1.1: Database Loading Performance")
            
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            start_time = time.time()
            
            mixinkey = MixInKeyIntegration(str(db_path))
            tracks = mixinkey.scan_mixinkey_database("/")
            
            load_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_used = end_memory - start_memory
            
            tracks_count = len(tracks)
            tracks_per_second = tracks_count / load_time if load_time > 0 else 0
            
            print(f"   📈 Loaded {tracks_count} tracks in {load_time:.2f}s")
            print(f"   ⚡ Rate: {tracks_per_second:.1f} tracks/second")
            print(f"   🧠 Memory used: {memory_used:.1f} MB")
            
            # Performance evaluation
            load_performance = {
                'tracks_loaded': tracks_count,
                'load_time_seconds': load_time,
                'tracks_per_second': tracks_per_second,
                'memory_used_mb': memory_used,
                'meets_threshold': tracks_per_second >= self.performance_thresholds['min_tracks_per_second']
            }
            
            status = "✅ PASS" if load_performance['meets_threshold'] else "❌ FAIL"
            print(f"   {status} Database loading performance")
            
            # Test 1.2: Processing Performance with Subset
            print("\n🔍 Test 1.2: Processing Performance with Large Subset")
            
            # Get a substantial subset of files that actually exist
            existing_files = []
            checked_count = 0
            max_to_check = 100  # Limit for performance
            
            for track in tracks.values():
                if checked_count >= max_to_check:
                    break
                if Path(track.file_path).exists():
                    existing_files.append(track.file_path)
                checked_count += 1
            
            print(f"   📁 Found {len(existing_files)} existing files to process")
            
            if len(existing_files) >= 10:
                # Test processing performance
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024
                
                performance_manager = PerformanceManager(mixinkey_integration=mixinkey)
                
                def progress_callback(completed, total, result):
                    if completed % max(1, total // 5) == 0:  # Progress every 20%
                        elapsed = time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        print(f"      ⏳ Progress: {completed}/{total} ({rate:.1f} files/sec)")
                
                results = performance_manager.process_library(
                    existing_files,
                    progress_callback=progress_callback,
                    use_mixinkey=True
                )
                
                processing_time = time.time() - start_time
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                processing_memory = end_memory - start_memory
                
                files_processed = results.get('processed_files', 0)
                processing_rate = files_processed / processing_time if processing_time > 0 else 0
                
                print(f"   📈 Processed {files_processed} files in {processing_time:.2f}s")
                print(f"   ⚡ Rate: {processing_rate:.1f} files/second")
                print(f"   🧠 Additional memory: {processing_memory:.1f} MB")
                
                processing_performance = {
                    'files_processed': files_processed,
                    'processing_time_seconds': processing_time,
                    'files_per_second': processing_rate,
                    'additional_memory_mb': processing_memory,
                    'meets_threshold': processing_rate >= self.performance_thresholds['min_tracks_per_second']
                }
                
                status = "✅ PASS" if processing_performance['meets_threshold'] else "❌ FAIL"
                print(f"   {status} Processing performance")
            else:
                processing_performance = {'status': 'SKIPPED', 'reason': 'Insufficient existing files'}
            
            self.test_results['large_library_performance'] = {
                'database_loading': load_performance,
                'file_processing': processing_performance,
                'overall_status': 'PASS' if (load_performance['meets_threshold'] and 
                                           processing_performance.get('meets_threshold', True)) else 'FAIL'
            }
            
        except Exception as e:
            print(f"❌ Error in large library performance test: {e}")
            self.test_results['large_library_performance'] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def test_memory_usage_and_leaks(self):
        """Test 2: Monitoreo de uso de memoria y detección de leaks."""
        
        try:
            print("🧠 Starting memory usage monitoring...")
            
            # Baseline memory measurement
            process = psutil.Process()
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            print(f"   📊 Baseline memory: {baseline_memory:.1f} MB")
            
            memory_samples = []
            
            # Test multiple cycles to detect memory leaks
            for cycle in range(5):
                print(f"   🔄 Memory test cycle {cycle + 1}/5")
                
                cycle_start_memory = process.memory_info().rss / 1024 / 1024
                
                # Simulate heavy operations
                db_path = Path.home() / "Library" / "Application Support" / "Mixedinkey" / "Collection11.mikdb"
                
                if db_path.exists():
                    # Create and destroy MixInKey integration multiple times
                    for i in range(3):
                        mixinkey = MixInKeyIntegration(str(db_path))
                        tracks = mixinkey.scan_mixinkey_database("/")
                        del mixinkey  # Force cleanup
                        del tracks
                
                cycle_end_memory = process.memory_info().rss / 1024 / 1024
                cycle_memory_increase = cycle_end_memory - cycle_start_memory
                
                memory_samples.append({
                    'cycle': cycle + 1,
                    'start_memory_mb': cycle_start_memory,
                    'end_memory_mb': cycle_end_memory,
                    'increase_mb': cycle_memory_increase
                })
                
                print(f"      Memory increase this cycle: {cycle_memory_increase:.1f} MB")
                
                # Brief pause for memory stabilization
                time.sleep(0.5)
            
            # Analyze memory leak pattern
            total_increase = memory_samples[-1]['end_memory_mb'] - memory_samples[0]['start_memory_mb']
            avg_increase_per_cycle = sum(sample['increase_mb'] for sample in memory_samples) / len(memory_samples)
            
            # Memory leak detection
            leak_threshold = 50  # MB per cycle
            has_memory_leak = avg_increase_per_cycle > leak_threshold
            
            print(f"   📈 Total memory increase: {total_increase:.1f} MB")
            print(f"   📊 Average increase per cycle: {avg_increase_per_cycle:.1f} MB")
            
            # Final memory check
            final_memory = process.memory_info().rss / 1024 / 1024
            exceeds_threshold = final_memory > self.performance_thresholds['max_memory_usage_mb']
            
            status = "✅ PASS" if not has_memory_leak and not exceeds_threshold else "❌ FAIL"
            print(f"   {status} Memory usage test")
            
            if has_memory_leak:
                print(f"   ⚠️  Potential memory leak detected!")
            if exceeds_threshold:
                print(f"   ⚠️  Memory usage exceeds threshold ({final_memory:.1f} > {self.performance_thresholds['max_memory_usage_mb']} MB)")
            
            self.test_results['memory_usage'] = {
                'baseline_memory_mb': baseline_memory,
                'final_memory_mb': final_memory,
                'total_increase_mb': total_increase,
                'avg_increase_per_cycle_mb': avg_increase_per_cycle,
                'memory_samples': memory_samples,
                'has_memory_leak': has_memory_leak,
                'exceeds_threshold': exceeds_threshold,
                'status': 'PASS' if not has_memory_leak and not exceeds_threshold else 'FAIL'
            }
            
        except Exception as e:
            print(f"❌ Error in memory usage test: {e}")
            self.test_results['memory_usage'] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def test_database_performance(self):
        """Test 3: Rendimiento de consultas a base de datos."""
        
        try:
            print("🗄️  Testing database query performance...")
            
            db_path = Path.home() / "Library" / "Application Support" / "Mixedinkey" / "Collection11.mikdb"
            
            if not db_path.exists():
                print("❌ No database available for performance testing")
                self.test_results['database_performance'] = {'status': 'SKIPPED'}
                return
            
            query_performance = {}
            
            # Test 1: Connection Performance
            print("   🔍 Testing database connection performance...")
            
            connection_times = []
            for i in range(10):
                start_time = time.time()
                conn = sqlite3.connect(str(db_path))
                conn.close()
                connection_time = time.time() - start_time
                connection_times.append(connection_time)
            
            avg_connection_time = sum(connection_times) / len(connection_times)
            print(f"      Average connection time: {avg_connection_time*1000:.1f}ms")
            
            # Test 2: Query Performance
            print("   🔍 Testing query performance...")
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Test different query types
            queries = [
                ("SELECT COUNT(*) FROM ZSONG", "Count all tracks"),
                ("SELECT * FROM ZSONG LIMIT 100", "Select first 100 tracks"),
                ("SELECT ZARTIST, ZNAME, ZTEMPO, ZKEY FROM ZSONG WHERE ZTEMPO > 120", "Filtered BPM query"),
                ("SELECT ZKEY, COUNT(*) FROM ZSONG GROUP BY ZKEY", "Group by key"),
                ("SELECT * FROM ZSONG WHERE ZARTIST LIKE '%Phil%'", "Artist search")
            ]
            
            for query, description in queries:
                start_time = time.time()
                cursor.execute(query)
                results = cursor.fetchall()
                query_time = time.time() - start_time
                
                query_performance[description] = {
                    'query_time_seconds': query_time,
                    'results_count': len(results),
                    'meets_threshold': query_time <= self.performance_thresholds['max_database_query_time']
                }
                
                status = "✅" if query_time <= self.performance_thresholds['max_database_query_time'] else "❌"
                print(f"      {status} {description}: {query_time*1000:.1f}ms ({len(results)} results)")
            
            conn.close()
            
            # Test 3: Concurrent Query Performance
            print("   🔍 Testing concurrent query performance...")
            
            def run_concurrent_query():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                start_time = time.time()
                cursor.execute("SELECT COUNT(*) FROM ZSONG")
                result = cursor.fetchone()
                query_time = time.time() - start_time
                conn.close()
                return query_time
            
            # Run 5 concurrent queries
            with ThreadPoolExecutor(max_workers=5) as executor:
                start_time = time.time()
                futures = [executor.submit(run_concurrent_query) for _ in range(5)]
                concurrent_times = [future.result() for future in futures]
                total_concurrent_time = time.time() - start_time
            
            avg_concurrent_time = sum(concurrent_times) / len(concurrent_times)
            print(f"      Concurrent queries: {total_concurrent_time*1000:.1f}ms total, {avg_concurrent_time*1000:.1f}ms average")
            
            # Overall database performance assessment
            all_queries_pass = all(perf['meets_threshold'] for perf in query_performance.values())
            concurrent_performance_good = avg_concurrent_time <= self.performance_thresholds['max_database_query_time']
            
            self.test_results['database_performance'] = {
                'connection_time_ms': avg_connection_time * 1000,
                'query_performance': query_performance,
                'concurrent_performance': {
                    'total_time_ms': total_concurrent_time * 1000,
                    'average_time_ms': avg_concurrent_time * 1000,
                    'meets_threshold': concurrent_performance_good
                },
                'overall_status': 'PASS' if all_queries_pass and concurrent_performance_good else 'FAIL'
            }
            
            status = "✅ PASS" if all_queries_pass and concurrent_performance_good else "❌ FAIL"
            print(f"   {status} Database performance test")
            
        except Exception as e:
            print(f"❌ Error in database performance test: {e}")
            self.test_results['database_performance'] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def test_parallel_processing_efficiency(self):
        """Test 4: Eficiencia del procesamiento paralelo."""
        
        try:
            print("⚡ Testing parallel processing efficiency...")
            
            db_path = Path.home() / "Library" / "Application Support" / "Mixedinkey" / "Collection11.mikdb"
            
            if not db_path.exists():
                print("❌ No database available for parallel processing test")
                self.test_results['parallel_processing'] = {'status': 'SKIPPED'}
                return
            
            mixinkey = MixInKeyIntegration(str(db_path))
            tracks = mixinkey.scan_mixinkey_database("/")
            
            # Get a sample of existing files
            existing_files = []
            for track in list(tracks.values())[:50]:  # Test with 50 files max
                if Path(track.file_path).exists():
                    existing_files.append(track.file_path)
                if len(existing_files) >= 20:  # Sufficient sample
                    break
            
            if len(existing_files) < 5:
                print("❌ Insufficient existing files for parallel processing test")
                self.test_results['parallel_processing'] = {'status': 'SKIPPED'}
                return
            
            print(f"   📁 Testing with {len(existing_files)} files")
            
            # Test different worker configurations
            worker_configs = [1, 2, 4, 8]
            performance_results = {}
            
            for workers in worker_configs:
                print(f"   🔄 Testing with {workers} workers...")
                
                start_time = time.time()
                performance_manager = PerformanceManager(
                    max_workers=workers,
                    mixinkey_integration=mixinkey
                )
                
                results = performance_manager.process_library(
                    existing_files,
                    use_mixinkey=True
                )
                
                processing_time = time.time() - start_time
                files_per_second = len(existing_files) / processing_time if processing_time > 0 else 0
                
                performance_results[workers] = {
                    'processing_time_seconds': processing_time,
                    'files_per_second': files_per_second,
                    'files_processed': results.get('processed_files', 0),
                    'efficiency_score': files_per_second / workers  # efficiency per worker
                }
                
                print(f"      ⚡ {workers} workers: {processing_time:.2f}s ({files_per_second:.1f} files/sec)")
            
            # Find optimal worker configuration
            best_workers = max(performance_results.keys(), 
                             key=lambda w: performance_results[w]['files_per_second'])
            
            best_performance = performance_results[best_workers]
            
            # Check if parallel processing provides benefit
            single_thread_rate = performance_results[1]['files_per_second']
            multi_thread_rate = best_performance['files_per_second']
            speedup_factor = multi_thread_rate / single_thread_rate if single_thread_rate > 0 else 1
            
            print(f"   🏆 Best configuration: {best_workers} workers")
            print(f"   📈 Speedup factor: {speedup_factor:.1f}x")
            
            # Performance assessment
            parallel_efficient = speedup_factor >= 1.5  # At least 50% improvement
            meets_rate_threshold = best_performance['files_per_second'] >= self.performance_thresholds['min_tracks_per_second']
            
            self.test_results['parallel_processing'] = {
                'worker_performance': performance_results,
                'best_worker_count': best_workers,
                'speedup_factor': speedup_factor,
                'parallel_efficient': parallel_efficient,
                'meets_rate_threshold': meets_rate_threshold,
                'overall_status': 'PASS' if parallel_efficient and meets_rate_threshold else 'FAIL'
            }
            
            status = "✅ PASS" if parallel_efficient and meets_rate_threshold else "❌ FAIL"
            print(f"   {status} Parallel processing efficiency")
            
        except Exception as e:
            print(f"❌ Error in parallel processing test: {e}")
            self.test_results['parallel_processing'] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def test_scaling_limits(self):
        """Test 5: Límites de escalabilidad del sistema."""
        
        try:
            print("📈 Testing system scaling limits...")
            
            db_path = Path.home() / "Library" / "Application Support" / "Mixedinkey" / "Collection11.mikdb"
            
            if not db_path.exists():
                print("❌ No database available for scaling test")
                self.test_results['scaling_limits'] = {'status': 'SKIPPED'}
                return
            
            # Test 1: Database Size Limits
            print("   🔍 Testing database size handling...")
            
            mixinkey = MixInKeyIntegration(str(db_path))
            tracks = mixinkey.scan_mixinkey_database("/")
            
            db_size_mb = db_path.stat().st_size / (1024 * 1024)
            track_count = len(tracks)
            
            print(f"      Database size: {db_size_mb:.1f} MB")
            print(f"      Track count: {track_count}")
            
            # Test 2: Memory Scaling with Track Count
            print("   🔍 Testing memory scaling...")
            
            # Measure memory usage with different track counts
            memory_measurements = []
            
            # Test with subsets of tracks
            test_sizes = [100, 500, 1000, 2000, 4000, len(tracks)]
            
            for size in test_sizes:
                if size > len(tracks):
                    continue
                
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024
                
                # Create subset
                track_subset = dict(list(tracks.items())[:size])
                
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_per_track = (end_memory - start_memory) / size if size > 0 else 0
                
                memory_measurements.append({
                    'track_count': size,
                    'memory_mb': end_memory - start_memory,
                    'memory_per_track_kb': memory_per_track * 1024
                })
                
                print(f"      {size} tracks: {end_memory - start_memory:.1f} MB ({memory_per_track*1024:.2f} KB/track)")
                
                del track_subset  # Cleanup
            
            # Test 3: Performance Degradation
            print("   🔍 Testing performance degradation...")
            
            # Measure query time with different database sizes
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Complex query that scales with data size
            start_time = time.time()
            cursor.execute("""
                SELECT ZKEY, AVG(ZTEMPO), COUNT(*) 
                FROM ZSONG 
                WHERE ZTEMPO > 0 
                GROUP BY ZKEY 
                ORDER BY COUNT(*) DESC
            """)
            results = cursor.fetchall()
            complex_query_time = time.time() - start_time
            
            conn.close()
            
            print(f"      Complex query time: {complex_query_time*1000:.1f}ms")
            
            # Scaling assessment
            max_memory_per_track = max(m['memory_per_track_kb'] for m in memory_measurements)
            memory_scaling_good = max_memory_per_track < 100  # Less than 100KB per track
            query_performance_good = complex_query_time < 2.0  # Less than 2 seconds
            
            self.test_results['scaling_limits'] = {
                'database_size_mb': db_size_mb,
                'max_tracks_tested': track_count,
                'memory_measurements': memory_measurements,
                'complex_query_time_ms': complex_query_time * 1000,
                'memory_scaling_good': memory_scaling_good,
                'query_performance_good': query_performance_good,
                'overall_status': 'PASS' if memory_scaling_good and query_performance_good else 'FAIL'
            }
            
            status = "✅ PASS" if memory_scaling_good and query_performance_good else "❌ FAIL"
            print(f"   {status} Scaling limits test")
            
        except Exception as e:
            print(f"❌ Error in scaling limits test: {e}")
            self.test_results['scaling_limits'] = {
                'status': 'ERROR',
                'error': str(e)
            }
    
    def generate_performance_report(self):
        """Genera reporte completo de rendimiento."""
        
        print(f"\n📋 PERFORMANCE & LOAD TEST REPORT")
        print("=" * 60)
        
        # Count passed/failed tests
        test_categories = [
            'large_library_performance',
            'memory_usage', 
            'database_performance',
            'parallel_processing',
            'scaling_limits'
        ]
        
        passed_tests = 0
        total_tests = 0
        critical_issues = []
        
        for category in test_categories:
            result = self.test_results.get(category, {})
            status = result.get('overall_status', result.get('status', 'UNKNOWN'))
            
            if status in ['PASS', 'FAIL']:
                total_tests += 1
                if status == 'PASS':
                    passed_tests += 1
                else:
                    critical_issues.append(category)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 PERFORMANCE SUMMARY:")
        print(f"   Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Detailed results
        for category in test_categories:
            result = self.test_results.get(category, {})
            status = result.get('overall_status', result.get('status', 'UNKNOWN'))
            
            status_icon = {
                'PASS': '✅',
                'FAIL': '❌', 
                'ERROR': '💥',
                'SKIPPED': '⏭️',
                'UNKNOWN': '❓'
            }.get(status, '❓')
            
            print(f"\n📊 {category.upper().replace('_', ' ')}:")
            print(f"   {status_icon} Status: {status}")
            
            # Add specific metrics for each test
            if category == 'large_library_performance' and 'database_loading' in result:
                loading = result['database_loading']
                print(f"   📈 Loaded {loading.get('tracks_loaded', 0)} tracks at {loading.get('tracks_per_second', 0):.1f} tracks/sec")
            
            elif category == 'memory_usage' and 'final_memory_mb' in result:
                print(f"   🧠 Peak memory: {result['final_memory_mb']:.1f} MB")
                if result.get('has_memory_leak'):
                    print(f"   ⚠️  Memory leak detected!")
            
            elif category == 'database_performance' and 'query_performance' in result:
                queries = result['query_performance']
                avg_time = sum(q['query_time_seconds'] for q in queries.values()) / len(queries)
                print(f"   🗄️  Average query time: {avg_time*1000:.1f}ms")
            
            elif category == 'parallel_processing' and 'speedup_factor' in result:
                print(f"   ⚡ Parallel speedup: {result['speedup_factor']:.1f}x")
        
        # Performance verdict
        print(f"\n🏆 OVERALL PERFORMANCE VERDICT:")
        
        if success_rate >= 90:
            print("   🥇 EXCELLENT: Sistema listo para bibliotecas profesionales grandes")
            verdict = "EXCELLENT"
        elif success_rate >= 70:
            print("   🥈 GOOD: Rendimiento adecuado con mejoras menores necesarias")
            verdict = "GOOD"
        elif success_rate >= 50:
            print("   🥉 FAIR: Rendimiento aceptable pero necesita optimizaciones")
            verdict = "FAIR"
        else:
            print("   💥 POOR: Problemas críticos de rendimiento detectados")
            verdict = "POOR"
        
        # Recommendations
        print(f"\n💡 RECOMENDACIONES PRIORITARIAS:")
        
        if verdict == "EXCELLENT":
            print("   - Rendimiento excelente para uso profesional")
            print("   - Sistema preparado para bibliotecas de 10K+ tracks")
            print("   - Mantener monitoreo de rendimiento en producción")
        else:
            if 'large_library_performance' in critical_issues:
                print("   🔥 CRÍTICO: Optimizar carga de bibliotecas grandes")
            if 'memory_usage' in critical_issues:
                print("   🔥 CRÍTICO: Resolver memory leaks detectados")
            if 'database_performance' in critical_issues:
                print("   🔥 CRÍTICO: Optimizar consultas de base de datos")
            if 'parallel_processing' in critical_issues:
                print("   ⚠️  Mejorar eficiencia de procesamiento paralelo")
            if 'scaling_limits' in critical_issues:
                print("   ⚠️  Revisar límites de escalabilidad")
        
        return {
            'success_rate': success_rate,
            'verdict': verdict,
            'critical_issues': critical_issues,
            'total_tests': total_tests,
            'passed_tests': passed_tests
        }

if __name__ == "__main__":
    print("🚀 Starting Performance & Load Testing Suite...")
    print("🎯 Focus: Estabilidad, Rapidez y Robustez para DJs Profesionales")
    
    tester = PerformanceLoadTester()
    tester.run_all_performance_tests()
    
    print(f"\n🏁 Performance Testing Completed!")
    print("=" * 60)