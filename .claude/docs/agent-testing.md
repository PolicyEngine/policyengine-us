# Testing Claude Subagents - TDD Approach

## Testing Strategies

### 1. Dry Run Testing
Test agents on actual PR code without applying changes:
```bash
# Example: Test policy-domain-validator on Idaho LIHEAP
/invoke policy-domain-validator "Check the Idaho LIHEAP implementation in PR #6444 for domain issues but DO NOT make any changes, just report what you find"
```

### 2. Test Case Files
Create test scenarios for agents to validate against:

```yaml
# .claude/tests/hard-coding-test.py
def calculate_benefit(income):
    # TEST CASE: Should flag these hard-coded values
    if income < 1000:  # Should be parameter
        return 500  # Should be parameter
    return income * 0.5  # 0.5 should be parameter
```

### 3. Agent Unit Tests
Test specific agent capabilities:

```markdown
## Test: policy-domain-validator catches federal/state mixing

### Input Code:
```python
# In state file
class id_liheap_income_limit(Variable):
    def formula(person, period, parameters):
        # Federal percentage hardcoded in state file
        return person("fpg", period) * 1.5  # Should flag: 1.5 is federal
```

### Expected Output:
- ❌ Federal parameter 1.5 should be in federal folder
- Suggest: Move to /parameters/gov/hhs/liheap/income_percentage.yaml
```

### 4. Integration Testing
Test agent combinations:

```bash
# Test Sequence:
1. Run policy-domain-validator → Find issues
2. Run parameter-architect → Design fixes  
3. Run reference-validator → Verify references
4. Check: Did they work together correctly?
```

## Practical Test Commands

### Test 1: Hard-Coded Value Detection
```bash
# Create test file with known issues
cat > test_hardcoding.py << 'EOF'
class benefit(Variable):
    def formula(person, period, parameters):
        eligible = person("eligible", period)
        # These should all be flagged
        base = 500  
        factor = 0.33
        months = [10, 11, 12, 1, 2, 3]
        age_limit = 60
        return base * factor
EOF

# Test the validator
/invoke policy-domain-validator "Scan test_hardcoding.py for hard-coded values"
```

### Test 2: Reference Validation
```bash
# Create parameter with bad reference
cat > test_param.yaml << 'EOF'
description: Test parameter
values:
  2024-01-01: 1000
metadata:
  reference:
    - title: Generic Document  # Too vague!
      # Missing href!
EOF

# Test the reference-validator
/invoke reference-validator "Check test_param.yaml for reference issues"
```

### Test 3: Federal/State Separation
```bash
# Test federal param in state location
/invoke policy-domain-validator "Check if federal poverty guideline percentage (150%) should be in state folder at /parameters/gov/states/id/liheap/fpg_percentage.yaml"
```

## TDD Workflow for New Agents

### Step 1: Write the Test First
```markdown
# Test Spec for new 'formula-optimizer' agent

## Test Case 1: Detect inefficient calculations
Input:
```python
def formula(person, period, parameters):
    result = 0
    for i in range(len(person.age)):
        if person.age[i] > 65:
            result += 1
    return result
```

Expected Output:
- Suggest: Use vectorized `(person("age", period) > 65).sum()`
```

### Step 2: Run Test Against Current Agent
```bash
/invoke formula-optimizer "Test on inefficient loop code"
# Should fail initially
```

### Step 3: Improve Agent Until Test Passes
Edit agent instructions to handle the case

### Step 4: Add Edge Cases
- Empty arrays
- Mixed data types  
- Complex nested operations

## Automated Test Suite

Create a test runner:
```bash
#!/bin/bash
# .claude/tests/run_tests.sh

echo "Testing policy-domain-validator..."
# Test 1: Hard-coding detection
result=$(/invoke policy-domain-validator "Check test_cases/hardcoding.py")
if [[ $result == *"hard-coded"* ]]; then
    echo "✅ Hard-coding detection passed"
else
    echo "❌ Failed to detect hard-coding"
fi

# Test 2: Federal/state separation
result=$(/invoke policy-domain-validator "Check test_cases/federal_state.py")
if [[ $result == *"federal parameter"* ]]; then
    echo "✅ Federal/state separation passed"
else
    echo "❌ Failed to detect federal/state issue"
fi
```

## Regression Testing

Keep a library of known issues:
```yaml
# .claude/tests/regression/idaho_liheap_issues.yaml
test_cases:
  - name: "Crisis benefit factor hard-coded"
    file: "variables/id_liheap_crisis.py"
    line: 23
    issue: "0.5 should be parameter"
    
  - name: "Federal percentage in state file"
    file: "parameters/gov/states/id/fpg_limit.yaml"
    issue: "150% is federal, should reference federal param"
    
  - name: "Missing age reference"
    file: "parameters/elderly_age.yaml"
    issue: "Reference doesn't mention age 60"
```

## Mock PR Testing

Test against a mock PR:
```bash
# Create a mock PR with known issues
git checkout -b test-agent-validation
# Add files with deliberate issues
# Run agents
/review-pr test-agent-validation --dry-run
# Check if all issues were caught
```

## Success Metrics

Track agent performance:
- Detection rate: Issues found / Total issues
- False positive rate: Invalid flags / Total flags
- Fix success rate: Working fixes / Total fixes attempted
- Time to resolution: From issue detection to working fix

## Example: Testing the Idaho LIHEAP Fixes

```bash
# 1. Checkout the problematic PR
git checkout idaho-liheap

# 2. Run validators in test mode
/invoke policy-domain-validator "Analyze variables/id_liheap.py and list all issues found. DO NOT fix anything."

# 3. Compare against known issues
# Expected to find:
# - 0.5 multiplier hard-coded
# - Months [10, 3] hard-coded  
# - Federal parameters in state files
# - Missing/incomplete references

# 4. Test the fix generation
/invoke parameter-architect "Design parameters for these hard-coded values: 0.5, months 10 and 3"

# 5. Validate the fixes would work
/invoke reference-validator "Check if these new parameters have proper references"
```

This approach lets you develop and refine agents iteratively, ensuring they catch real issues before deploying them on actual PRs.