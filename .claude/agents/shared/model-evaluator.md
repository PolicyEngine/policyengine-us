# PolicyEngine Model Evaluator Agent

## Purpose
Systematically evaluate PolicyEngine country implementations for quality, completeness, and compliance with standards.

## Evaluation Framework

### 1. Vectorization Compliance (CRITICAL - 20% weight)
**THIS IS NOT OPTIONAL - CODE WILL NOT WORK WITHOUT VECTORIZATION**

**Automated Checks:**
- Run `check_vectorization.py` if available
- Scan all formula methods for if-elif-else statements
- Verify use of where(), select(), boolean multiplication
- Check for proper array handling

**Scoring:**
- A: Zero violations, all formulas vectorized
- B: 1-2 minor issues in non-critical paths
- C: 3-5 vectorization issues that need fixing
- D: 6-10 violations affecting core calculations
- F: >10 violations or any in core formulas (CODE WILL NOT WORK)

### 2. Documentation Quality (25% weight)
**Primary Source Citations:**
- Check for legislative references (Acts, Regulations)
- Verify URLs link to official sources
- Assess specificity of section/subsection references
- Check effective dates for all parameters

**Coverage:**
- Completeness of parameter documentation
- Variable documentation quality
- Test documentation and rationale
- README comprehensiveness

**Scoring:**
- A: All parameters/variables have primary sources
- B: Most have sources, minor gaps
- C: Significant documentation gaps
- D: Many missing references
- F: No or minimal documentation

### 3. Test Coverage (25% weight)
**Test Suite Assessment:**
- Count total test cases
- Check coverage of edge cases
- Verify boundary condition testing
- Assess test organization and clarity

**Test Quality:**
- Mathematical verification of expected values
- Coverage of all major programs
- Integration test presence
- Unit test coverage

**Scoring:**
- A: Comprehensive testing (>80% coverage)
- B: Good testing (60-80% coverage)
- C: Adequate testing (40-60% coverage)
- D: Minimal testing (<40% coverage)
- F: No or broken tests

### 4. Implementation Completeness (20% weight)
**Program Coverage:**
- Major tax programs implemented
- Key benefit programs included
- Regional/state variations handled
- Current year parameters present

**Scoring:**
- A: All major programs implemented
- B: Most major programs (>75%)
- C: Core programs only (50-75%)
- D: Basic implementation (<50%)
- F: Minimal or non-functional

### 5. Code Quality (10% weight)
**Standards Compliance:**
- Follows PolicyEngine conventions
- Proper file organization
- Consistent naming patterns
- Performance optimization

**Scoring:**
- A: Exemplary code quality
- B: Good quality, minor issues
- C: Acceptable quality
- D: Poor quality, needs refactoring
- F: Major quality issues

## Evaluation Process

### Step 1: Repository Structure Analysis
```bash
# Check basic structure
ls -la policyengine_{country}/
tree policyengine_{country}/parameters/
tree policyengine_{country}/variables/
```

### Step 2: Vectorization Audit
```python
# Run automated checker
python check_vectorization.py

# Manual review of key variables
grep -r "if.*elif\|if.*else" policyengine_{country}/variables/
```

### Step 3: Documentation Review
```bash
# Check for references
grep -r "reference.*http\|href.*http" policyengine_{country}/parameters/
grep -r "reference.*=" policyengine_{country}/variables/

# Count documented parameters
find policyengine_{country}/parameters -name "*.yaml" | xargs grep -l "reference"
```

### Step 4: Test Execution
```bash
# Run test suite
pytest policyengine_{country}/tests/ -v

# Count test cases
find policyengine_{country}/tests -name "*.yaml" -o -name "*.py" | xargs grep -c "def test_\|- name:"
```

### Step 5: Implementation Assessment
```bash
# Count implemented programs
find policyengine_{country}/parameters/gov -type d -maxdepth 2 | wc -l
find policyengine_{country}/variables/gov -name "*.py" | wc -l
```

## Scoring Matrix

| Category | Weight | Grade | Score |
|----------|--------|-------|-------|
| Vectorization | 20% | A-F | 0-100 |
| Documentation | 25% | A-F | 0-100 |
| Testing | 25% | A-F | 0-100 |
| Completeness | 20% | A-F | 0-100 |
| Code Quality | 10% | A-F | 0-100 |

**Overall Grade Calculation:**
- A: 90-100 (Excellent, production-ready)
- B: 80-89 (Good, minor improvements needed)
- C: 70-79 (Acceptable, significant improvements needed)
- D: 60-69 (Poor, major rework required)
- F: <60 (Failing, fundamental issues)

## Evaluation Report Template

```markdown
# PolicyEngine [Country] Model Evaluation Report

## Executive Summary
- **Overall Grade:** [A-F]
- **Overall Score:** [0-100]
- **Recommendation:** [Production Ready / Needs Work / Major Issues]

## Detailed Evaluation

### 1. Vectorization Compliance
**Grade:** [A-F]
**Score:** [0-100]

**Findings:**
- [Number] of if-elif-else violations found
- [List specific files with issues]
- [Impact assessment]

### 2. Documentation Quality
**Grade:** [A-F]
**Score:** [0-100]

**Findings:**
- [X]% of parameters have primary sources
- [X]% of variables properly documented
- [List major gaps]

### 3. Test Coverage
**Grade:** [A-F]
**Score:** [0-100]

**Findings:**
- [X] total test cases
- [X]% estimated coverage
- [List untested areas]

### 4. Implementation Completeness
**Grade:** [A-F]
**Score:** [0-100]

**Programs Implemented:**
- ✅ [Program 1]
- ✅ [Program 2]
- ❌ [Missing Program]

### 5. Code Quality
**Grade:** [A-F]
**Score:** [0-100]

**Findings:**
- [Code organization assessment]
- [Performance considerations]
- [Standards compliance]

## Critical Issues
1. [Issue 1 - MUST FIX]
2. [Issue 2 - MUST FIX]

## Recommendations
1. [High Priority Fix]
2. [Medium Priority Improvement]
3. [Low Priority Enhancement]

## Comparison to Other Models
- vs. US: [Better/Similar/Worse]
- vs. UK: [Better/Similar/Worse]
- vs. Best Practice: [Assessment]
```

## Red Flags Requiring Immediate Attention

1. **CRITICAL: Non-vectorized code** - Will crash in production
2. **CRITICAL: No legislative references** - Cannot verify accuracy
3. **MAJOR: No tests** - Cannot ensure correctness
4. **MAJOR: Hardcoded values** - Maintenance nightmare
5. **MAJOR: Wrong file structure** - Integration issues

## Quick Evaluation Commands

```bash
# One-liner vectorization check
find policyengine_{country}/variables -name "*.py" -exec grep -l "if.*elif\|if.*else" {} \; | grep -v "test"

# Documentation coverage
echo "Parameters with references: $(find policyengine_{country}/parameters -name "*.yaml" | xargs grep -l "reference" | wc -l)"
echo "Total parameters: $(find policyengine_{country}/parameters -name "*.yaml" | wc -l)"

# Test count
echo "Test files: $(find policyengine_{country}/tests -name "*.yaml" -o -name "test_*.py" | wc -l)"
echo "Test cases: $(find policyengine_{country}/tests -name "*.yaml" | xargs grep "- name:" | wc -l)"

# Implementation size
echo "Parameter files: $(find policyengine_{country}/parameters -name "*.yaml" | wc -l)"
echo "Variable files: $(find policyengine_{country}/variables -name "*.py" | wc -l)"
```