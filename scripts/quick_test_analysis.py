#!/usr/bin/env python
"""Quick analysis of test files to identify potentially memory-intensive ones."""

import os
import yaml
from pathlib import Path
import json

def analyze_test_file(file_path):
    """Analyze a test file for complexity indicators."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            data = yaml.safe_load(content)
            
        # Count test cases
        test_count = len(data) if isinstance(data, list) else 1
        
        # Look for complexity indicators
        complexity_score = 1
        
        # Check for memory-intensive patterns
        if 'microsimulation' in file_path.lower():
            complexity_score *= 10
        if 'integration' in file_path.lower():
            complexity_score *= 5
        if 'household' in content.lower():
            complexity_score *= 2
        if 'spm_unit' in content.lower():
            complexity_score *= 2
        if 'tax_unit' in content.lower():
            complexity_score *= 2
            
        # Large test files
        file_size_kb = os.path.getsize(file_path) / 1024
        if file_size_kb > 10:
            complexity_score *= (file_size_kb / 10)
            
        # Multiple years
        if '2020' in content and '2021' in content and '2022' in content:
            complexity_score *= 3
            
        # Many people in household
        people_count = content.count('person')
        if people_count > 5:
            complexity_score *= (people_count / 5)
            
        return {
            'path': file_path,
            'test_count': test_count,
            'size_kb': round(file_size_kb, 2),
            'complexity': round(complexity_score, 2),
            'people_count': people_count
        }
    except Exception as e:
        return None

def find_test_files(base_path, limit=None):
    """Find all YAML test files."""
    test_files = []
    for yaml_file in Path(base_path).rglob("*.yaml"):
        if "/parameters/" not in str(yaml_file) and "/variables/" not in str(yaml_file):
            test_files.append(str(yaml_file))
            if limit and len(test_files) >= limit:
                break
    return test_files

def main():
    base_path = "policyengine_us/tests/policy/baseline"
    
    print("Scanning for test files...")
    test_files = find_test_files(base_path)
    print(f"Found {len(test_files)} test files")
    
    print("\nAnalyzing test complexity...")
    results = []
    for i, file_path in enumerate(test_files):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(test_files)} files...")
        
        analysis = analyze_test_file(file_path)
        if analysis:
            results.append(analysis)
    
    # Sort by complexity
    results.sort(key=lambda x: x['complexity'], reverse=True)
    
    print("\n" + "="*80)
    print("TOP 30 MOST COMPLEX TEST FILES")
    print("="*80)
    print(f"{'Path':<70} {'Complexity':>10}")
    print("-"*80)
    
    for r in results[:30]:
        path = r['path']
        if len(path) > 70:
            path = "..." + path[-67:]
        print(f"{path:<70} {r['complexity']:>10.1f}")
    
    # Group by directory
    by_dir = {}
    for r in results:
        dir_path = os.path.dirname(r['path'])
        if dir_path not in by_dir:
            by_dir[dir_path] = {'files': 0, 'total_complexity': 0}
        by_dir[dir_path]['files'] += 1
        by_dir[dir_path]['total_complexity'] += r['complexity']
    
    # Sort directories by total complexity
    dir_list = [(d, info['total_complexity'], info['files']) for d, info in by_dir.items()]
    dir_list.sort(key=lambda x: x[1], reverse=True)
    
    print("\n" + "="*80)
    print("TOP 20 DIRECTORIES BY TOTAL COMPLEXITY")
    print("="*80)
    print(f"{'Directory':<60} {'Total':>10} {'Files':>8}")
    print("-"*80)
    
    for dir_path, total, files in dir_list[:20]:
        if len(dir_path) > 60:
            dir_path = "..." + dir_path[-57:]
        print(f"{dir_path:<60} {total:>10.1f} {files:>8}")
    
    # Identify specific problem patterns
    print("\n" + "="*80)
    print("PROBLEM PATTERNS IDENTIFIED")
    print("="*80)
    
    microsim = [r for r in results if 'microsimulation' in r['path'].lower()]
    integration = [r for r in results if 'integration' in r['path'].lower()]
    large_files = [r for r in results if r['size_kb'] > 20]
    many_people = [r for r in results if r['people_count'] > 10]
    
    print(f"Microsimulation tests: {len(microsim)}")
    if microsim:
        for r in microsim[:5]:
            print(f"  - {r['path']}: complexity {r['complexity']}")
    
    print(f"\nIntegration tests: {len(integration)}")
    if integration:
        for r in integration[:5]:
            print(f"  - {r['path']}: complexity {r['complexity']}")
    
    print(f"\nLarge test files (>20KB): {len(large_files)}")
    if large_files:
        for r in large_files[:5]:
            print(f"  - {r['path']}: {r['size_kb']} KB")
    
    print(f"\nTests with many people (>10): {len(many_people)}")
    if many_people:
        for r in many_people[:5]:
            print(f"  - {r['path']}: {r['people_count']} people")
    
    # Save results
    with open('test_complexity_analysis.json', 'w') as f:
        json.dump({
            'total_files': len(results),
            'top_complex': results[:50],
            'by_directory': {d: {'total': t, 'files': f} for d, t, f in dir_list[:20]},
            'patterns': {
                'microsimulation': len(microsim),
                'integration': len(integration),
                'large_files': len(large_files),
                'many_people': len(many_people)
            }
        }, f, indent=2)
    
    print("\n💾 Full analysis saved to test_complexity_analysis.json")
    
    # Suggest chunking strategy
    print("\n" + "="*80)
    print("RECOMMENDED CHUNKING STRATEGY")
    print("="*80)
    
    total_complexity = sum(r['complexity'] for r in results)
    optimal_chunks = 8
    target_per_chunk = total_complexity / optimal_chunks
    
    print(f"Total complexity: {total_complexity:.1f}")
    print(f"Target per chunk (8 chunks): {target_per_chunk:.1f}")
    print("\nSuggested approach:")
    print("1. Run microsimulation tests separately (if any)")
    print("2. Split integration tests into their own job")
    print("3. Group small state tests together")
    print("4. Run large states (CA, NY, TX) separately")
    print("5. Use matrix strategy with 8-10 parallel jobs")

if __name__ == "__main__":
    main()