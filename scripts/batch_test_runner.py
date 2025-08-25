#!/usr/bin/env python
"""
Optimized batch test runner for PolicyEngine that:
1. Reuses the PolicyEngine instance across multiple test files
2. Properly cleans up memory between tests
3. Batches test execution to minimize initialization overhead
"""

import os
import sys
import gc
import yaml
import traceback
from pathlib import Path
from typing import List, Dict, Any
import time
import psutil
import json

# Import PolicyEngine components
from policyengine_core.simulations import Simulation
from policyengine_us import CountryTaxBenefitSystem
from policyengine_core.tools.test_runner import run_tests as core_run_tests

# Global system instance to reuse
SYSTEM = None
SYSTEM_INIT_TIME = None

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def init_system():
    """Initialize the PolicyEngine system once."""
    global SYSTEM, SYSTEM_INIT_TIME
    if SYSTEM is None:
        print("Initializing PolicyEngine system (one-time cost)...")
        start = time.time()
        SYSTEM = CountryTaxBenefitSystem()
        SYSTEM_INIT_TIME = time.time() - start
        print(f"  System initialized in {SYSTEM_INIT_TIME:.1f}s")
        print(f"  Memory after init: {get_memory_usage():.1f} MB")
    return SYSTEM

def cleanup_memory():
    """Force garbage collection and clear caches."""
    # Clear any simulation caches
    gc.collect()
    
    # Force collection of cyclic references
    gc.collect(2)
    
    # If memory usage is high, do aggressive cleanup
    if get_memory_usage() > 2000:  # If over 2GB
        print(f"  High memory detected ({get_memory_usage():.1f} MB), forcing cleanup...")
        # Clear all module-level caches that might exist
        import sys
        for module_name in list(sys.modules.keys()):
            if 'policyengine' in module_name:
                module = sys.modules[module_name]
                if hasattr(module, '_cache'):
                    module._cache.clear()
        gc.collect()
        print(f"  Memory after cleanup: {get_memory_usage():.1f} MB")

def run_single_test(test_data: Dict, system: Any) -> Dict:
    """Run a single test case using the shared system instance."""
    try:
        # Create simulation with the shared system
        simulation = Simulation(
            tax_benefit_system=system,
            situation=test_data.get('input', {}),
            period=test_data.get('period', '2024')
        )
        
        # Check outputs
        outputs = test_data.get('output', {})
        passed = True
        failures = []
        
        for variable, expected in outputs.items():
            try:
                actual = simulation.calculate(variable, test_data.get('period', '2024'))
                # Simple comparison (you might need more sophisticated comparison)
                if hasattr(actual, '__len__'):
                    actual = actual[0] if len(actual) == 1 else list(actual)
                
                if abs(float(actual) - float(expected)) > 0.01:
                    passed = False
                    failures.append(f"{variable}: expected {expected}, got {actual}")
            except Exception as e:
                passed = False
                failures.append(f"{variable}: {str(e)}")
        
        return {'passed': passed, 'failures': failures}
        
    except Exception as e:
        return {'passed': False, 'failures': [str(e)]}

def run_test_file(file_path: str, system: Any) -> Dict:
    """Run all tests in a single YAML file using the shared system."""
    try:
        with open(file_path, 'r') as f:
            test_cases = yaml.safe_load(f)
        
        if not isinstance(test_cases, list):
            test_cases = [test_cases]
        
        results = {
            'file': file_path,
            'total': len(test_cases),
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
        for i, test_case in enumerate(test_cases):
            result = run_single_test(test_case, system)
            if result['passed']:
                results['passed'] += 1
            else:
                results['failed'] += 1
                if result['failures']:
                    test_name = test_case.get('name', f'Test {i+1}')
                    results['errors'].append({
                        'test': test_name,
                        'failures': result['failures']
                    })
        
        return results
        
    except Exception as e:
        return {
            'file': file_path,
            'total': 0,
            'passed': 0,
            'failed': 1,
            'errors': [{'test': 'File load', 'failures': [str(e)]}]
        }

def batch_run_tests(test_files: List[str], batch_size: int = 10, cleanup_frequency: int = 5):
    """
    Run tests in batches, reusing the system instance.
    
    Args:
        test_files: List of test file paths
        batch_size: Number of files to run before reporting progress
        cleanup_frequency: Run memory cleanup every N batches
    """
    # Initialize system once
    system = init_system()
    
    total_files = len(test_files)
    all_results = []
    start_time = time.time()
    initial_memory = get_memory_usage()
    
    print(f"\nRunning {total_files} test files in batches of {batch_size}...")
    print(f"Initial memory: {initial_memory:.1f} MB")
    print("-" * 60)
    
    for batch_num, i in enumerate(range(0, total_files, batch_size)):
        batch = test_files[i:i+batch_size]
        batch_results = []
        
        print(f"\nBatch {batch_num + 1} ({i+1}-{min(i+batch_size, total_files)} of {total_files})")
        
        for file_path in batch:
            # Run test file
            rel_path = file_path.replace('policyengine_us/tests/policy/baseline/', '')
            print(f"  Testing: {rel_path}...", end='', flush=True)
            
            file_start = time.time()
            result = run_test_file(file_path, system)
            file_time = time.time() - file_start
            
            result['time'] = file_time
            batch_results.append(result)
            all_results.append(result)
            
            # Print result
            if result['failed'] == 0:
                print(f" ✓ ({result['passed']}/{result['total']}) in {file_time:.1f}s")
            else:
                print(f" ✗ ({result['passed']}/{result['total']}) in {file_time:.1f}s")
        
        # Memory cleanup every N batches
        if (batch_num + 1) % cleanup_frequency == 0:
            current_memory = get_memory_usage()
            print(f"\n  Memory before cleanup: {current_memory:.1f} MB")
            cleanup_memory()
            after_memory = get_memory_usage()
            print(f"  Memory after cleanup: {after_memory:.1f} MB (freed {current_memory - after_memory:.1f} MB)")
    
    # Final statistics
    total_time = time.time() - start_time
    final_memory = get_memory_usage()
    
    total_tests = sum(r['total'] for r in all_results)
    total_passed = sum(r['passed'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    
    print("\n" + "=" * 60)
    print("BATCH TEST RESULTS")
    print("=" * 60)
    print(f"Files tested: {total_files}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success rate: {(total_passed/total_tests*100):.1f}%")
    print(f"\nExecution time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    print(f"Average per file: {total_time/total_files:.1f}s")
    print(f"Time saved from batching: ~{(total_files * 20 - total_time):.0f}s")
    print(f"\nMemory usage:")
    print(f"  Initial: {initial_memory:.1f} MB")
    print(f"  Final: {final_memory:.1f} MB")
    print(f"  Increase: {final_memory - initial_memory:.1f} MB")
    
    if SYSTEM_INIT_TIME:
        print(f"\nSystem init time (one-time): {SYSTEM_INIT_TIME:.1f}s")
        print(f"Amortized init cost per file: {SYSTEM_INIT_TIME/total_files:.2f}s")
    
    # Save results
    with open('batch_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'files': total_files,
                'tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'time_seconds': total_time,
                'memory_start_mb': initial_memory,
                'memory_end_mb': final_memory
            },
            'results': all_results
        }, f, indent=2)
    
    return all_results

def find_test_files(base_path: str, pattern: str = None) -> List[str]:
    """Find all test YAML files."""
    test_files = []
    for yaml_file in Path(base_path).rglob("*.yaml"):
        file_path = str(yaml_file)
        if "/parameters/" not in file_path and "/variables/" not in file_path:
            if pattern is None or pattern in file_path:
                test_files.append(file_path)
    return test_files

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch test runner for PolicyEngine")
    parser.add_argument("--path", default="policyengine_us/tests/policy/baseline",
                        help="Base path for tests")
    parser.add_argument("--pattern", help="Pattern to filter test files")
    parser.add_argument("--batch-size", type=int, default=10,
                        help="Number of files per batch")
    parser.add_argument("--cleanup-frequency", type=int, default=5,
                        help="Run memory cleanup every N batches")
    parser.add_argument("--limit", type=int, help="Limit number of files to test")
    
    args = parser.parse_args()
    
    # Find test files
    print(f"Finding test files in {args.path}...")
    test_files = find_test_files(args.path, args.pattern)
    
    if args.limit:
        test_files = test_files[:args.limit]
    
    if not test_files:
        print("No test files found!")
        sys.exit(1)
    
    print(f"Found {len(test_files)} test files")
    
    # Run batch tests
    results = batch_run_tests(
        test_files,
        batch_size=args.batch_size,
        cleanup_frequency=args.cleanup_frequency
    )
    
    # Exit with error if tests failed
    total_failed = sum(r['failed'] for r in results)
    sys.exit(0 if total_failed == 0 else 1)

if __name__ == "__main__":
    main()