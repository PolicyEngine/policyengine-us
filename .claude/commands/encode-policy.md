---
description: Orchestrates multi-agent workflow to implement new government benefit programs
---

# Implementing $ARGUMENTS in PolicyEngine

Coordinate the multi-agent workflow to implement $ARGUMENTS as a complete, production-ready government benefit program.

## Phase 1: Issue and PR Setup
Invoke @issue-manager agent to:
- Search for existing issue or create new one for $ARGUMENTS
- Create draft PR immediately for early visibility
- Return issue number and PR URL for tracking

## Phase 2: Variable Naming Convention
Invoke @naming-coordinator agent to:
- Analyze existing naming patterns in the codebase
- Establish variable naming convention for $ARGUMENTS
- Post naming decisions to GitHub issue for all agents to reference

**Quality Gate**: Naming convention must be posted before proceeding to ensure consistency across parallel development.

## Phase 3: Document Collection
Invoke @document-collector agent to gather official $ARGUMENTS documentation and post to the GitHub issue.

**Quality Gate**: Documentation must include:
- Official program guidelines or state plan
- Income limits and benefit schedules
- Eligibility criteria and priority groups
- Seasonal/temporal rules if applicable

## Phase 4: Parallel Development (SIMULTANEOUS)
After documentation is ready, invoke BOTH agents IN PARALLEL:
- @test-creator: Create integration tests from documentation only
- @rules-engineer: Implement rules from documentation (will internally use @parameter-architect if needed)

**CRITICAL**: These must run simultaneously in separate conversations to maintain isolation. Neither can see the other's work.

**Quality Requirements**:
- rules-engineer: ZERO hard-coded values, complete implementations only
- test-creator: Use only existing PolicyEngine variables, test realistic calculations

## Phase 5: Branch Integration
Invoke @integration-agent to:
- Merge test and implementation branches
- Fix basic integration issues (entity mismatches, naming)
- Verify tests can run with implementation
- Prepare unified codebase for validation

**Why Critical**: The next phases need to work on integrated code to catch real issues.

## Phase 6: Pre-Push Validation
Invoke @pr-pusher agent to:
- Ensure changelog entry exists
- Run formatters (black, isort)
- Fix any linting issues
- Run local tests for quick validation
- Push branch and report initial CI status

**Quality Gate**: Branch must be properly formatted and have changelog before continuing.

## Phase 7: Required Fixes and Validations (SEQUENTIAL)

**MANDATORY**: These agents fix critical issues. Invoke them SEQUENTIALLY:

### Step 1: Edge Case Testing

- @edge-case-generator: Generate comprehensive boundary tests
- Commit generated tests before proceeding

### Step 2: Cross-Program Validation

- @cross-program-validator: Check interactions with other benefits
- Fix any cliff effects or integration issues found
- Commit fixes before proceeding

### Step 3: Documentation Enhancement

- @documentation-enricher: Add examples and regulatory citations
- Commit documentation improvements

### Step 4: Performance Optimization

- @performance-optimizer: Vectorize and optimize calculations
- Run tests to ensure no regressions
- Commit optimizations

**Why Sequential**: Each enhancement builds on the previous work and modifying the same files in parallel would cause conflicts.

**Quality Requirements**:
- All edge cases covered
- No benefit cliffs or integration issues
- Complete documentation with examples
- Fully vectorized, no performance issues

## Phase 8: Implementation Validation
Invoke @implementation-validator agent to check for:
- Hard-coded values in variables
- Placeholder or incomplete implementations
- Federal/state parameter organization
- Test quality and coverage
- Performance and vectorization issues

**Quality Gate**: Must pass ALL critical validations before proceeding

## Phase 9: Review
Invoke @rules-reviewer to validate the complete implementation against documentation.

**Review Criteria**:
- Accuracy to source documents
- Complete coverage of all rules
- Proper parameter usage
- Edge case handling

## Phase 10: CI Fix & PR Finalization
**CRITICAL: ALWAYS invoke @ci-fixer agent - do NOT manually fix issues**

Invoke @ci-fixer agent to:
- Find the draft PR created in Phase 0
- Merge test-creator and rules-engineer branches
- Monitor CI pipeline for ALL failures
- Fix failing tests, linting, formatting automatically
- Address any entity-level issues in tests
- Fix parameter validation errors
- Clean up working_references.md
- Iterate until ALL CI checks pass
- Mark PR as ready for review

**Success Metrics**:
- All CI checks passing (tests, lint, format)
- Test and implementation branches merged
- PR marked ready (not draft)
- Clean commit history showing agent work


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

## Execution Instructions

**YOUR ROLE**: You are an orchestrator ONLY. You must:
1. Invoke agents using the Task tool
2. Wait for their completion
3. Check quality gates
4. Proceed to next phase

**YOU MUST NOT**:
- Write any code yourself
- Fix any issues manually
- Run tests directly
- Edit files

**Start Implementation**:
1. Phase 1: Invoke @issue-manager agent
2. Phase 2: Invoke @naming-coordinator agent to establish naming conventions
3. Phase 3: Invoke @document-collector agent for $ARGUMENTS  
4. Phase 4: Invoke @test-creator AND @rules-engineer in parallel
5. Phase 5: Invoke @integration-agent to merge branches
6. Phase 6: Invoke @pr-pusher to validate and push branch
7. Phase 7: Invoke fix agents sequentially (@edge-case-generator, @cross-program-validator, etc.)
8. Phase 8: Invoke @implementation-validator to check for issues
9. Phase 9: Invoke @rules-reviewer for final validation
10. Phase 10: Invoke @ci-fixer to handle CI pipeline

**CRITICAL**: You MUST complete ALL phases. Do NOT skip any phases - they are ALL REQUIRED:

- Phase 5 ensures branches work together
- Phase 7 fixes critical issues (NOT optional enhancements)
- Phase 8-9 validate correctness
- Phase 10 ensures CI passes

If any agent fails, report the failure but DO NOT attempt to fix it yourself.
