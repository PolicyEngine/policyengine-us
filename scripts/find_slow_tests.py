#!/usr/bin/env python
"""
Quick script to identify potentially slow tests based on file characteristics.
Since all tests have ~15-30s overhead from PolicyEngine initialization,
we're looking for tests that would be EXTRA slow on top of that.
"""

import os
import yaml
from pathlib import Path
import json

def analyze_test_file(file_path):
    """Analyze a test file for slowness indicators."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            data = yaml.safe_load(content)
        
        if not isinstance(data, list):
            return None
            
        # Count test cases
        num_tests = len(data)
        
        # Analyze complexity of each test case
        max_people = 0
        total_calculations = 0
        has_multiple_years = False
        complex_variables = []
        
        for test in data:
            if not isinstance(test, dict):
                continue
                
            # Count people in this test
            people_in_test = 0
            if 'input' in test and 'people' in test.get('input', {}):
                people_in_test = len(test['input']['people'])
                max_people = max(max_people, people_in_test)
            
            # Check for multiple periods
            if 'period' in test:
                period = str(test['period'])
                if '-' not in period:  # Year-only periods often mean multiple calculations
                    has_multiple_years = True
            
            # Count output variables (more outputs = more calculations)
            if 'output' in test:
                total_calculations += len(test.get('output', {}))
                
                # Look for expensive variables
                for var in test.get('output', {}).keys():
                    if any(word in var for word in ['microsimulation', 'poverty', 'household_net_income', 
                                                     'benefits', 'taxes', 'disposable_income']):
                        complex_variables.append(var)
        
        # Calculate slowness score
        slowness_score = 0
        
        # Each test case adds ~1-2 seconds on top of initialization
        slowness_score += num_tests * 1.5
        
        # Many people means more calculations
        if max_people > 4:
            slowness_score += (max_people - 4) * 2
        
        # Integration tests are slower
        if 'integration' in file_path.lower():
            slowness_score += 10
        
        # Multiple years means running multiple periods
        if has_multiple_years:
            slowness_score += 5
        
        # Complex variables require full household calculations
        if complex_variables:
            slowness_score += len(set(complex_variables)) * 2
        
        # Large files tend to be slower
        file_size_kb = os.path.getsize(file_path) / 1024
        if file_size_kb > 50:
            slowness_score += file_size_kb / 10
        
        return {
            'path': file_path,
            'num_tests': num_tests,
            'max_people': max_people,
            'total_calculations': total_calculations,
            'has_multiple_years': has_multiple_years,
            'complex_variables': list(set(complex_variables)),
            'file_size_kb': round(file_size_kb, 2),
            'slowness_score': round(slowness_score, 2),
            'estimated_seconds': round(16 + slowness_score, 1)  # 16s base + slowness
        }
        
    except Exception as e:
        return None

def main():
    base_path = "policyengine_us/tests/policy/baseline"
    
    print("Analyzing test files for potential slowness...")
    results = []
    
    for yaml_file in Path(base_path).rglob("*.yaml"):
        file_path = str(yaml_file)
        if "/parameters/" in file_path or "/variables/" in file_path:
            continue
            
        analysis = analyze_test_file(file_path)
        if analysis:
            results.append(analysis)
    
    # Sort by estimated time
    results.sort(key=lambda x: x['estimated_seconds'], reverse=True)
    
    print(f"\nAnalyzed {len(results)} test files")
    print("\n" + "="*80)
    print("TOP 30 POTENTIALLY SLOWEST TESTS")
    print("="*80)
    print(f"{'Test File':<60} {'Est. Time':>10} {'Tests':>7} {'People':>7}")
    print("-"*80)
    
    for r in results[:30]:
        path = r['path'].replace('policyengine_us/tests/policy/baseline/', '')
        if len(path) > 60:
            path = "..." + path[-57:]
        print(f"{path:<60} {r['estimated_seconds']:>9.1f}s {r['num_tests']:>7} {r['max_people']:>7}")
    
    # Find patterns
    print("\n" + "="*80)
    print("SLOWNESS PATTERNS")
    print("="*80)
    
    very_slow = [r for r in results if r['estimated_seconds'] > 60]
    integration_tests = [r for r in results if 'integration' in r['path'].lower()]
    many_people = [r for r in results if r['max_people'] > 10]
    many_tests = [r for r in results if r['num_tests'] > 20]
    
    print(f"Very slow (>60s estimated): {len(very_slow)} files")
    print(f"Integration tests: {len(integration_tests)} files")
    print(f"Tests with >10 people: {len(many_people)} files")
    print(f"Files with >20 test cases: {len(many_tests)} files")
    
    # Show details of slowest
    if very_slow:
        print("\n" + "="*80)
        print("DETAILS OF SLOWEST TESTS (>60s)")
        print("="*80)
        
        for test in very_slow[:5]:
            path = test['path'].replace('policyengine_us/tests/policy/baseline/', '')
            print(f"\n{path}")
            print(f"  Estimated time: {test['estimated_seconds']}s")
            print(f"  Test cases: {test['num_tests']}")
            print(f"  Max people: {test['max_people']}")
            print(f"  File size: {test['file_size_kb']} KB")
            if test['complex_variables']:
                print(f"  Complex vars: {', '.join(test['complex_variables'][:3])}")
    
    # Save results
    with open('slow_tests_analysis.json', 'w') as f:
        json.dump({
            'total_files': len(results),
            'very_slow': [r['path'] for r in very_slow],
            'top_30': results[:30]
        }, f, indent=2)
    
    print("\n💾 Full analysis saved to slow_tests_analysis.json")
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    print("Based on the analysis:")
    print("1. ALL tests have ~15-30s overhead from PolicyEngine initialization")
    print("2. Tests with many test cases (>20) will be proportionally slower")
    print("3. Integration tests with multiple households take longest")
    print("4. For GitHub Actions, the issue is cumulative time, not individual tests")
    print("\nSolutions:")
    print("- Batch tests to reuse PolicyEngine initialization")
    print("- Run integration tests separately with more resources")
    print("- Consider splitting large test files into smaller ones")
    print("- Add more swap space in CI for memory-intensive tests")

if __name__ == "__main__":
    main()