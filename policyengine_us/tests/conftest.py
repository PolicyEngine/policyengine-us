"""
Pytest configuration for PolicyEngine US tests.
Implements memory cleanup and test optimization.
"""

import gc
import pytest
import psutil
import os

# Track memory usage
_initial_memory = None
_test_counter = 0
_cleanup_frequency = int(os.environ.get('POLICYENGINE_TEST_CLEANUP_FREQUENCY', '10'))

def get_memory_usage_mb():
    """Get current memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatically cleanup memory after each test."""
    global _test_counter
    
    # Run test
    yield
    
    # Increment counter
    _test_counter += 1
    
    # Cleanup periodically
    if _test_counter % _cleanup_frequency == 0:
        current_memory = get_memory_usage_mb()
        
        # Force garbage collection
        gc.collect()
        gc.collect(2)  # Collect cyclic references
        
        # Clear any caches in PolicyEngine modules
        import sys
        for module_name in list(sys.modules.keys()):
            if 'policyengine' in module_name:
                module = sys.modules[module_name]
                # Clear common cache attributes
                for cache_attr in ['_cache', '_parameters_cache', '_variables_cache']:
                    if hasattr(module, cache_attr):
                        cache = getattr(module, cache_attr)
                        if hasattr(cache, 'clear'):
                            cache.clear()
        
        after_memory = get_memory_usage_mb()
        if current_memory - after_memory > 100:  # If we freed more than 100MB
            print(f"\n  [Memory cleanup: {current_memory:.0f}MB → {after_memory:.0f}MB]")

@pytest.fixture(scope="session", autouse=True)
def monitor_memory_usage():
    """Monitor memory usage across the entire test session."""
    global _initial_memory
    
    # Record initial memory
    _initial_memory = get_memory_usage_mb()
    print(f"\n[Test session started - Initial memory: {_initial_memory:.0f}MB]")
    
    yield
    
    # Report final memory
    final_memory = get_memory_usage_mb()
    memory_increase = final_memory - _initial_memory
    
    print(f"\n[Test session ended - Final memory: {final_memory:.0f}MB (Δ{memory_increase:+.0f}MB)]")
    print(f"[Total tests run: {_test_counter}]")
    
    # Warn if memory increased significantly
    if memory_increase > 2000:  # More than 2GB increase
        print("\n⚠️  WARNING: Significant memory increase detected!")
        print("Consider running tests in smaller batches or increasing cleanup frequency.")

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--cleanup-frequency",
        action="store",
        default="10",
        help="Run memory cleanup every N tests"
    )
    parser.addoption(
        "--memory-limit",
        action="store",
        default="4000",
        help="Maximum memory usage in MB before forcing cleanup"
    )

def pytest_configure(config):
    """Configure pytest with our options."""
    global _cleanup_frequency
    _cleanup_frequency = int(config.getoption("--cleanup-frequency"))
    
    # Set environment variable for child processes
    os.environ['POLICYENGINE_TEST_CLEANUP_FREQUENCY'] = str(_cleanup_frequency)
    
    # Configure memory limit
    memory_limit = int(config.getoption("--memory-limit"))
    os.environ['POLICYENGINE_TEST_MEMORY_LIMIT'] = str(memory_limit)

# Hook to skip memory-intensive tests in CI if needed
def pytest_collection_modifyitems(config, items):
    """Modify test collection based on available memory."""
    if os.environ.get('CI') and get_memory_usage_mb() > 3000:
        # In CI with limited memory, skip certain heavy tests
        skip_heavy = pytest.mark.skip(reason="Skipping heavy test in CI due to memory constraints")
        for item in items:
            if "integration" in item.nodeid and "tax" in item.nodeid:
                item.add_marker(skip_heavy)