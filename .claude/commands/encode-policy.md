---
description: Orchestrates multi-agent workflow to implement new government benefit programs
---

# Implementing $ARGUMENTS in PolicyEngine

Coordinate the multi-agent workflow to implement $ARGUMENTS as a complete, production-ready government benefit program.

## Phase 1: Document Collection
Invoke document-collector agent to gather official $ARGUMENTS documentation.

**Quality Gate**: Documentation must include:
- Official program guidelines or state plan
- Income limits and benefit schedules
- Eligibility criteria and priority groups
- Seasonal/temporal rules if applicable

## Phase 2: Parallel Development (SIMULTANEOUS)
After documentation is ready, invoke BOTH agents IN PARALLEL:
- test-creator: Create integration tests from documentation only
- rules-engineer: Implement rules from documentation (will internally use parameter-architect if needed)

**CRITICAL**: These must run simultaneously in separate conversations to maintain isolation. Neither can see the other's work.

**Quality Requirements**:
- rules-engineer: ZERO hard-coded values, complete implementations only
- test-creator: Use only existing PolicyEngine variables, test realistic calculations

## Phase 3: Auto-Enhancement (SEQUENTIAL)

After initial implementation, invoke enhancement agents SEQUENTIALLY to avoid merge conflicts:

### Step 1: Edge Case Testing

- edge-case-generator: Generate comprehensive boundary tests
- Commit generated tests before proceeding

### Step 2: Cross-Program Validation

- cross-program-validator: Check interactions with other benefits
- Fix any cliff effects or integration issues found
- Commit fixes before proceeding

### Step 3: Documentation Enhancement

- documentation-enricher: Add examples and regulatory citations
- Commit documentation improvements

### Step 4: Performance Optimization

- performance-optimizer: Vectorize and optimize calculations
- Run tests to ensure no regressions
- Commit optimizations

**Why Sequential**: Each enhancement builds on the previous work and modifying the same files in parallel would cause conflicts.

**Quality Requirements**:
- All edge cases covered
- No benefit cliffs or integration issues
- Complete documentation with examples
- Fully vectorized, no performance issues

## Phase 4: Implementation Validation
Invoke implementation-validator agent to check for:
- Hard-coded values in variables
- Placeholder or incomplete implementations
- Federal/state parameter organization
- Test quality and coverage
- Performance and vectorization issues

**Quality Gate**: Must pass ALL critical validations before proceeding

## Phase 5: Review
Invoke rules-reviewer to validate the complete implementation against documentation.

**Review Criteria**:
- Accuracy to source documents
- Complete coverage of all rules
- Proper parameter usage
- Edge case handling

## Phase 6: CI Fix & PR Creation
Invoke ci-fixer to:
- Create draft PR with complete implementation
- Monitor CI pipeline for failures
- Fix any failing tests, linting, or formatting issues
- Address parameter validation errors
- Iterate until all CI checks pass
- Mark PR as ready for review

**Success Metrics**:
- All CI checks passing
- Zero hard-coded values
- Complete test coverage
- Proper documentation

## Expected Review Cycles

### Current Paradigm (Single Reviewer)
- **Initial Review**: 3-5 comments on hard-coding, parameters, organization
- **Second Review**: 1-2 comments on missed edge cases
- **Third Review**: Minor documentation updates
- **Total**: 3 review cycles, 4-8 total comments

### With Enhanced Agents + Auto-Enhancers (This Workflow)
- **Initial Review**: 0 comments expected (auto-merge capable)
- **Total**: 0 review cycles, 0 comments (70% probability)
- **Fallback**: 1 review cycle, 1 comment for policy clarifications (30% probability)
- **80% CI**: [0-2 comments]

### Alternative: Multiple Specialized Reviewers
**Option A: Domain Expert + Code Quality**
- Domain Expert: Validates accuracy to regulations (1-2 comments)
- Code Reviewer: Checks patterns and style (1-2 comments)
- **Total**: 1-2 review cycles, 2-4 total comments

**Option B: Full Review Board**
- Parameter Reviewer: Validates all parameters against sources (0-1 comments)
- Test Reviewer: Checks test coverage and realism (0-1 comments)
- Implementation Reviewer: Validates formula accuracy (0-1 comments)
- Integration Reviewer: Checks cross-program interactions (0-1 comments)
- **Total**: 1 review cycle, 0-4 total comments (parallel reviews)

## Anti-Patterns This Workflow Prevents

1. **Hard-coded values**: Rules-engineer enforces parameterization
2. **Incomplete implementations**: Validator catches before PR
3. **Federal/state mixing**: Proper parameter organization enforced
4. **Non-existent variables in tests**: Test creator uses only real variables
5. **Missing edge cases**: Edge-case-generator covers all boundaries
6. **Benefit cliffs**: Cross-program-validator identifies interactions
7. **Poor documentation**: Documentation-enricher adds examples
8. **Performance issues**: Performance-optimizer ensures vectorization
9. **Review delays**: Most issues caught and fixed automatically

## Start Implementation

Begin with Phase 1: Use Task tool to invoke document-collector agent for $ARGUMENTS.

Then proceed through each phase, ensuring quality gates are met before advancing.