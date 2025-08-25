#!/usr/bin/env python
"""
Measure execution time for individual PolicyEngine tests.
Identifies which tests are slow vs fast.
"""

import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List
import sys
import signal
import os

def timeout_handler(signum, frame):
    raise TimeoutError("Test timed out")

def run_single_test_with_timing(test_path: str, timeout_seconds: int = 30) -> Dict:
    """Run a single test and measure its execution time."""
    start_time = time.time()
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        # Run the test
        result = subprocess.run(
            ["policyengine-core", "test", test_path, "-c", "policyengine_us"],
            capture_output=True,
            text=True
        )
        
        # Cancel timeout
        signal.alarm(0)
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "path": test_path,
            "duration": round(duration, 2),
            "success": result.returncode == 0,
            "timeout": False,
            "error": result.stderr if result.returncode != 0 else None
        }
    
    except TimeoutError:
        signal.alarm(0)
        return {
            "path": test_path,
            "duration": timeout_seconds,
            "success": False,
            "timeout": True,
            "error": f"Timeout after {timeout_seconds} seconds"
        }
    
    except Exception as e:
        signal.alarm(0)
        return {
            "path": test_path,
            "duration": time.time() - start_time,
            "success": False,
            "timeout": False,
            "error": str(e)
        }

def find_test_files(base_path: str, pattern: str = None, limit: int = None) -> List[str]:
    """Find test YAML files."""
    test_files = []
    base = Path(base_path)
    
    for yaml_file in base.rglob("*.yaml"):
        file_path = str(yaml_file)
        # Skip non-test files
        if "/parameters/" in file_path or "/variables/" in file_path:
            continue
        if pattern and pattern not in file_path:
            continue
        test_files.append(file_path)
        if limit and len(test_files) >= limit:
            break
    
    return test_files

def analyze_test_complexity(test_path: str) -> Dict:
    """Quick analysis of test complexity without running it."""
    try:
        with open(test_path, 'r') as f:
            content = f.read()
        
        # Count indicators
        test_cases = content.count("- name:")
        people = content.count("person")
        years = len(set([y for y in range(2020, 2030) if str(y) in content]))
        size_kb = os.path.getsize(test_path) / 1024
        
        # Complexity indicators
        is_integration = "integration" in test_path.lower()
        is_microsim = "microsim" in test_path.lower()
        has_households = "household" in content
        has_multiple_units = "spm_unit" in content and "tax_unit" in content
        
        return {
            "test_cases": test_cases,
            "people_mentions": people,
            "years": years,
            "size_kb": round(size_kb, 2),
            "is_integration": is_integration,
            "is_microsim": is_microsim,
            "has_households": has_households,
            "has_multiple_units": has_multiple_units
        }
    except:
        return {}

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Measure PolicyEngine test execution times")
    parser.add_argument("--path", default="policyengine_us/tests/policy/baseline", 
                        help="Base path for tests")
    parser.add_argument("--limit", type=int, help="Limit number of tests")
    parser.add_argument("--pattern", help="Pattern to filter test files")
    parser.add_argument("--timeout", type=int, default=30, 
                        help="Timeout per test in seconds")
    parser.add_argument("--focus", choices=["slow", "integration", "state"], 
                        help="Focus on specific test types")
    
    args = parser.parse_args()
    
    # Determine which tests to run
    if args.focus == "integration":
        pattern = "integration"
    elif args.focus == "state":
        pattern = "/states/"
    else:
        pattern = args.pattern
    
    print(f"Finding test files...")
    test_files = find_test_files(args.path, pattern, args.limit)
    
    if not test_files:
        print("No test files found!")
        sys.exit(1)
    
    print(f"Found {len(test_files)} test files to analyze")
    
    # If we're testing many files, do a quick sample first
    if len(test_files) > 50 and not args.limit:
        print("\n⚠️  Many tests found. Sampling for quick analysis...")
        # Sample: Take every Nth file to get a representative sample
        sample_rate = len(test_files) // 30
        test_files = test_files[::sample_rate]
        print(f"Sampled {len(test_files)} tests for timing analysis")
    
    results = []
    slow_tests = []
    
    print(f"\nTiming {len(test_files)} tests (timeout: {args.timeout}s each)...")
    print("-" * 60)
    
    for i, test_path in enumerate(test_files, 1):
        # Show progress
        rel_path = test_path.replace("policyengine_us/tests/policy/baseline/", "")
        print(f"[{i}/{len(test_files)}] Testing: {rel_path}...", end="", flush=True)
        
        # Run timing test
        result = run_single_test_with_timing(test_path, args.timeout)
        results.append(result)
        
        # Show result
        if result["timeout"]:
            print(f" TIMEOUT ({args.timeout}s)")
            slow_tests.append(result)
        elif result["duration"] > 10:
            print(f" SLOW ({result['duration']}s)")
            slow_tests.append(result)
        elif result["success"]:
            print(f" OK ({result['duration']}s)")
        else:
            print(f" FAILED ({result['duration']}s)")
    
    # Sort by duration
    results.sort(key=lambda x: x["duration"], reverse=True)
    
    print("\n" + "=" * 80)
    print("SLOWEST TESTS")
    print("=" * 80)
    print(f"{'Test Path':<70} {'Time (s)':>10}")
    print("-" * 80)
    
    for r in results[:20]:
        path = r["path"].replace("policyengine_us/tests/policy/baseline/", "")
        if len(path) > 70:
            path = "..." + path[-67:]
        status = "⏱️" if r["timeout"] else ("✓" if r["success"] else "✗")
        print(f"{status} {path:<68} {r['duration']:>9.1f}s")
    
    # Analyze slow tests for patterns
    print("\n" + "=" * 80)
    print("SLOW TEST ANALYSIS")
    print("=" * 80)
    
    very_slow = [r for r in results if r["duration"] > 10]
    moderate = [r for r in results if 5 < r["duration"] <= 10]
    fast = [r for r in results if r["duration"] <= 5]
    
    print(f"Very slow (>10s): {len(very_slow)} tests")
    print(f"Moderate (5-10s): {len(moderate)} tests")
    print(f"Fast (<5s): {len(fast)} tests")
    
    if very_slow:
        print("\n📊 Analyzing very slow tests for patterns...")
        for test in very_slow[:5]:
            complexity = analyze_test_complexity(test["path"])
            rel_path = test["path"].replace("policyengine_us/tests/policy/baseline/", "")
            print(f"\n{rel_path}:")
            print(f"  Duration: {test['duration']}s")
            if complexity:
                print(f"  Test cases: {complexity.get('test_cases', 0)}")
                print(f"  Size: {complexity.get('size_kb', 0)} KB")
                print(f"  Integration: {complexity.get('is_integration', False)}")
                print(f"  Multiple units: {complexity.get('has_multiple_units', False)}")
    
    # Statistical summary
    if results:
        total_time = sum(r["duration"] for r in results)
        avg_time = total_time / len(results)
        
        print("\n" + "=" * 80)
        print("STATISTICS")
        print("=" * 80)
        print(f"Total tests timed: {len(results)}")
        print(f"Total execution time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"Average time per test: {avg_time:.2f}s")
        print(f"Tests that timed out: {len([r for r in results if r['timeout']])}")
        print(f"Tests that failed: {len([r for r in results if not r['success'] and not r['timeout']])}")
    
    # Save results
    output_file = "test_timing_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "summary": {
                "total_tests": len(results),
                "very_slow": len(very_slow),
                "moderate": len(moderate),
                "fast": len(fast),
                "total_time_seconds": sum(r["duration"] for r in results),
                "average_time_seconds": sum(r["duration"] for r in results) / len(results) if results else 0
            },
            "slowest_tests": results[:30],
            "all_results": results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to {output_file}")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if very_slow:
        print("⚠️  Found very slow tests that should be optimized or run separately:")
        for test in very_slow[:3]:
            rel_path = test["path"].replace("policyengine_us/tests/policy/baseline/", "")
            print(f"   - {rel_path} ({test['duration']}s)")
        
        print("\nSuggested fixes:")
        print("1. Run these tests in a separate CI job with longer timeout")
        print("2. Investigate why they're slow (complex calculations? large datasets?)")
        print("3. Consider splitting large test files into smaller ones")
        print("4. Add caching for repeated calculations")

if __name__ == "__main__":
    main()