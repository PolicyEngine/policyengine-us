#!/bin/bash
# Script to test if memory fixes prevent Killed:9 errors

echo "================================"
echo "Testing Memory Fix for PolicyEngine"
echo "================================"
echo ""

# Check initial memory
echo "Initial system memory:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    vm_stat | grep "Pages free"
    sysctl hw.memsize | awk '{print "Total RAM: " $2/1024/1024/1024 " GB"}'
else
    free -h
fi
echo ""

# Test 1: Run the command that was getting killed
echo "Test 1: Running make test-yaml-no-structural (this was getting Killed:9)"
echo "--------------------------------------------------------------"
timeout 300 make test-yaml-no-structural
EXIT_CODE=$?

if [ $EXIT_CODE -eq 137 ] || [ $EXIT_CODE -eq 9 ]; then
    echo "❌ FAILED: Still getting killed (exit code: $EXIT_CODE)"
    echo ""
    echo "Test 2: Trying with optimized version"
    echo "--------------------------------------------------------------"
    timeout 300 make test-yaml-no-structural-optimized
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 137 ] || [ $EXIT_CODE -eq 9 ]; then
        echo "❌ FAILED: Optimized version also killed"
        echo ""
        echo "Test 3: Trying batch runner directly"
        echo "--------------------------------------------------------------"
        timeout 300 python scripts/batch_test_runner.py --path policyengine_us/tests/policy/baseline --limit 50 --batch-size 10
        EXIT_CODE=$?
        
        if [ $EXIT_CODE -eq 137 ] || [ $EXIT_CODE -eq 9 ]; then
            echo "❌ FAILED: Even batch runner is getting killed"
        else
            echo "✅ SUCCESS: Batch runner completed without being killed!"
        fi
    else
        echo "✅ SUCCESS: Optimized version completed without being killed!"
    fi
elif [ $EXIT_CODE -eq 124 ]; then
    echo "⏱️  Test timed out after 5 minutes (but not killed for memory!)"
else
    echo "✅ SUCCESS: Test completed without being killed (exit code: $EXIT_CODE)"
fi

echo ""
echo "Final system memory:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    vm_stat | grep "Pages free"
else
    free -h
fi

echo ""
echo "================================"
echo "Test Complete"
echo "================================"