#!/usr/bin/env python
"""
Analyze test files and create optimal chunks for parallel CI execution.
This helps distribute tests evenly across GitHub Actions jobs.
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess
import time

def count_test_cases_in_yaml(file_path: str) -> int:
    """Count number of test cases in a YAML file."""
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            if isinstance(data, list):
                return len(data)
            return 1
    except:
        return 1

def estimate_test_complexity(file_path: str) -> int:
    """Estimate test complexity based on file content."""
    complexity = 1
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Higher complexity for certain keywords
            if 'microsimulation' in content.lower():
                complexity *= 5
            if 'integration' in file_path.lower():
                complexity *= 3
            if 'household' in content:
                complexity *= 2
            if 'period' in content and 'year' in content:
                complexity *= 1.5
                
            # More test cases = higher complexity
            test_count = content.count('- name:')
            complexity *= max(1, test_count / 5)
            
    except:
        pass
    
    return int(complexity)

def find_all_test_files(base_path: str) -> List[Dict]:
    """Find all test files and gather metadata."""
    test_files = []
    base = Path(base_path)
    
    for yaml_file in base.rglob("*.yaml"):
        file_path = str(yaml_file)
        
        # Skip non-test files
        if "/parameters/" in file_path or "/variables/" in file_path:
            continue
            
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Count test cases
        test_count = count_test_cases_in_yaml(file_path)
        
        # Estimate complexity
        complexity = estimate_test_complexity(file_path)
        
        # Determine test category
        if "microsimulation" in file_path:
            category = "microsimulation"
        elif "integration" in file_path:
            category = "integration"
        elif "/states/" in file_path:
            state = file_path.split("/states/")[1].split("/")[0]
            category = f"state_{state}"
        elif "/irs/" in file_path:
            category = "irs"
        elif "/hhs/" in file_path:
            category = "hhs"
        else:
            category = "other"
        
        test_files.append({
            "path": file_path,
            "size_kb": round(file_size / 1024, 2),
            "test_count": test_count,
            "complexity": complexity,
            "category": category,
            "relative_path": str(yaml_file.relative_to(base))
        })
    
    return test_files

def create_balanced_chunks(test_files: List[Dict], num_chunks: int = 5) -> List[List[Dict]]:
    """Create balanced chunks based on complexity."""
    # Sort by complexity (highest first)
    sorted_files = sorted(test_files, key=lambda x: x["complexity"], reverse=True)
    
    # Initialize chunks with complexity tracking
    chunks = [[] for _ in range(num_chunks)]
    chunk_complexities = [0] * num_chunks
    
    # Distribute files using greedy algorithm
    for file_info in sorted_files:
        # Find chunk with lowest complexity
        min_idx = chunk_complexities.index(min(chunk_complexities))
        chunks[min_idx].append(file_info)
        chunk_complexities[min_idx] += file_info["complexity"]
    
    return chunks

def create_category_based_chunks(test_files: List[Dict]) -> Dict[str, List[Dict]]:
    """Group tests by category."""
    chunks = {}
    
    for file_info in test_files:
        category = file_info["category"]
        if category not in chunks:
            chunks[category] = []
        chunks[category].append(file_info)
    
    # Split large categories
    MAX_FILES_PER_CHUNK = 100
    final_chunks = {}
    
    for category, files in chunks.items():
        if len(files) > MAX_FILES_PER_CHUNK:
            # Split into multiple chunks
            for i in range(0, len(files), MAX_FILES_PER_CHUNK):
                chunk_name = f"{category}_part{i//MAX_FILES_PER_CHUNK + 1}"
                final_chunks[chunk_name] = files[i:i+MAX_FILES_PER_CHUNK]
        else:
            final_chunks[category] = files
    
    return final_chunks

def generate_github_matrix(chunks: List[List[Dict]]) -> Dict:
    """Generate GitHub Actions matrix configuration."""
    matrix = {
        "include": []
    }
    
    for i, chunk in enumerate(chunks):
        # Create test paths list
        test_paths = [f["relative_path"] for f in chunk]
        
        # Calculate chunk stats
        total_complexity = sum(f["complexity"] for f in chunk)
        total_tests = sum(f["test_count"] for f in chunk)
        
        matrix["include"].append({
            "chunk_id": i + 1,
            "chunk_name": f"chunk_{i + 1}",
            "test_count": len(chunk),
            "total_tests": total_tests,
            "complexity": total_complexity,
            "test_paths": test_paths
        })
    
    return matrix

def analyze_test_distribution(test_files: List[Dict], chunks: List[List[Dict]]) -> None:
    """Print analysis of test distribution."""
    print("\n" + "=" * 80)
    print("TEST DISTRIBUTION ANALYSIS")
    print("=" * 80)
    
    # Overall statistics
    total_files = len(test_files)
    total_tests = sum(f["test_count"] for f in test_files)
    total_complexity = sum(f["complexity"] for f in test_files)
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"  Total test files: {total_files}")
    print(f"  Total test cases: {total_tests}")
    print(f"  Total complexity: {total_complexity}")
    
    # Category breakdown
    categories = {}
    for f in test_files:
        cat = f["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "complexity": 0}
        categories[cat]["count"] += 1
        categories[cat]["complexity"] += f["complexity"]
    
    print(f"\n📁 BY CATEGORY:")
    for cat, stats in sorted(categories.items()):
        print(f"  {cat:<20} {stats['count']:>5} files, complexity: {stats['complexity']:>6}")
    
    # Chunk analysis
    print(f"\n📦 CHUNK DISTRIBUTION ({len(chunks)} chunks):")
    print("-" * 60)
    print(f"{'Chunk':<10} {'Files':<10} {'Tests':<10} {'Complexity':<12} {'Balance':<10}")
    print("-" * 60)
    
    chunk_complexities = []
    for i, chunk in enumerate(chunks):
        files = len(chunk)
        tests = sum(f["test_count"] for f in chunk)
        complexity = sum(f["complexity"] for f in chunk)
        chunk_complexities.append(complexity)
        
    avg_complexity = sum(chunk_complexities) / len(chunk_complexities)
    
    for i, chunk in enumerate(chunks):
        files = len(chunk)
        tests = sum(f["test_count"] for f in chunk)
        complexity = sum(f["complexity"] for f in chunk)
        balance = complexity / avg_complexity
        
        print(f"Chunk {i+1:<4} {files:<10} {tests:<10} {complexity:<12} {balance:<10.2f}x")
    
    # Identify potentially problematic tests
    high_complexity = sorted(test_files, key=lambda x: x["complexity"], reverse=True)[:10]
    
    print(f"\n⚠️  HIGHEST COMPLEXITY TESTS:")
    print("-" * 60)
    for f in high_complexity:
        path = f["relative_path"]
        if len(path) > 50:
            path = "..." + path[-47:]
        print(f"  {path:<50} complexity: {f['complexity']:>5}")

def save_chunk_configuration(chunks: List[List[Dict]], output_file: str = "test_chunks.json") -> None:
    """Save chunk configuration for CI use."""
    config = {
        "chunks": [],
        "metadata": {
            "total_files": sum(len(chunk) for chunk in chunks),
            "num_chunks": len(chunks),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    
    for i, chunk in enumerate(chunks):
        chunk_data = {
            "id": i + 1,
            "name": f"chunk_{i + 1}",
            "files": [f["relative_path"] for f in chunk],
            "complexity": sum(f["complexity"] for f in chunk),
            "test_count": sum(f["test_count"] for f in chunk)
        }
        config["chunks"].append(chunk_data)
    
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 Chunk configuration saved to: {output_file}")

def generate_github_workflow(chunks: List[List[Dict]], output_file: str = ".github/workflows/test-chunked.yml") -> None:
    """Generate optimized GitHub Actions workflow."""
    
    workflow = """name: Test (Chunked)

on: [push, pull_request]

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v3
      - id: set-matrix
        run: |
          echo "matrix=$(cat test_chunks.json | jq -c '.chunks | map({\"chunk_id\": .id, \"chunk_name\": .name})')" >> $GITHUB_OUTPUT

  test:
    needs: prepare
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include: ${{ fromJson(needs.prepare.outputs.matrix) }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e .[dev]
      
      - name: Increase swap space
        run: |
          sudo swapoff -a
          sudo fallocate -l 8G /swapfile
          sudo chmod 600 /swapfile
          sudo mkswap /swapfile
          sudo swapon /swapfile
          free -h
      
      - name: Run tests for chunk ${{ matrix.chunk_name }}
        run: |
          # Get test files for this chunk
          CHUNK_ID=${{ matrix.chunk_id }}
          TEST_FILES=$(cat test_chunks.json | jq -r ".chunks[] | select(.id == $CHUNK_ID) | .files[]")
          
          # Run tests
          for test_file in $TEST_FILES; do
            echo "Testing: $test_file"
            policyengine-core test "policyengine_us/tests/policy/baseline/$test_file" -c policyengine_us || exit 1
          done
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results-${{ matrix.chunk_name }}
          path: test-results/
"""
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(workflow)
    
    print(f"📝 GitHub workflow saved to: {output_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze and chunk PolicyEngine tests")
    parser.add_argument(
        "--path",
        default="policyengine_us/tests/policy/baseline",
        help="Base path for tests"
    )
    parser.add_argument(
        "--chunks",
        type=int,
        default=5,
        help="Number of chunks to create"
    )
    parser.add_argument(
        "--strategy",
        choices=["balanced", "category"],
        default="balanced",
        help="Chunking strategy"
    )
    parser.add_argument(
        "--output",
        default="test_chunks.json",
        help="Output file for chunk configuration"
    )
    parser.add_argument(
        "--generate-workflow",
        action="store_true",
        help="Generate GitHub Actions workflow"
    )
    
    args = parser.parse_args()
    
    # Find all test files
    print(f"Scanning for test files in: {args.path}")
    test_files = find_all_test_files(args.path)
    
    if not test_files:
        print("No test files found!")
        sys.exit(1)
    
    print(f"Found {len(test_files)} test files")
    
    # Create chunks based on strategy
    if args.strategy == "balanced":
        chunks = create_balanced_chunks(test_files, args.chunks)
    else:
        category_chunks = create_category_based_chunks(test_files)
        chunks = list(category_chunks.values())
    
    # Analyze distribution
    analyze_test_distribution(test_files, chunks)
    
    # Save configuration
    save_chunk_configuration(chunks, args.output)
    
    # Generate GitHub workflow if requested
    if args.generate_workflow:
        generate_github_workflow(chunks)
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()