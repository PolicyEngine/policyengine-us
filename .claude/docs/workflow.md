# Multi-Agent Development Workflow

## Architecture Overview

This workflow ensures complete isolation between agents during development, preventing any agent from seeing another's work until the appropriate phase.

## Branch and Worktree Isolation

### Initial Setup (Supervisor Agent)

```bash
# Create base branch
git checkout master
git pull origin master
git checkout -b feature/<program>-base

# Create isolated branches for each agent
git checkout -b feature/<program>-docs
git checkout -b feature/<program>-tests  
git checkout -b feature/<program>-rules

# Create separate worktrees for complete isolation
git worktree add ../pe-<program>-docs feature/<program>-docs
git worktree add ../pe-<program>-tests feature/<program>-tests
git worktree add ../pe-<program>-rules feature/<program>-rules
```

### Agent Isolation Rules

1. **Document Collector**
   - Works in: `../pe-<program>-docs/`
   - Branch: `feature/<program>-docs`
   - Can see: Only base PolicyEngine code
   - Creates: Documentation in `docs/agents/sources/<program>/`

2. **Test Creator**
   - Works in: `../pe-<program>-tests/`
   - Branch: `feature/<program>-tests`
   - Can see: Only base PolicyEngine code (NOT the implementation)
   - Receives: Document files via supervisor (copied to their worktree)
   - Creates: Integration tests

3. **Rules Engineer**
   - Works in: `../pe-<program>-rules/`
   - Branch: `feature/<program>-rules`
   - Can see: Only base PolicyEngine code (NOT the tests)
   - Receives: Document files via supervisor (copied to their worktree)
   - Creates: Parameters and variables with unit tests

4. **Reviewer** (acting as verifier)
   - Works in: Main repository after merge
   - Branch: `feature/<program>-verify`
   - Can see: Everything after supervisor merges
   - Validates: All components together

## Important CI Notes

- **Draft PRs DO run CI**: GitHub Actions will run on draft PRs, not just ready PRs
- **CI failures are expected initially**: The workflow includes fixing CI issues iteratively
- **Always check CI status**: Use `gh pr checks` to monitor, even on drafts

## Workflow Phases

### Phase 1: Document Collection

```bash
# Supervisor starts Document Collector in isolated environment
cd ../pe-<program>-docs
# Document Collector works here, creates documents
git add docs/agents/sources/<program>/
git commit -m "Add <program> documentation"
git push origin feature/<program>-docs
```

### Phase 2: Parallel Development

Supervisor distributes documents WITHOUT merging branches:

```bash
# Copy documents to Test Creator worktree
cp -r ../pe-<program>-docs/docs/agents/sources/<program>/ \
      ../pe-<program>-tests/docs/agents/sources/<program>/

# Copy documents to Rules Engineer worktree  
cp -r ../pe-<program>-docs/docs/agents/sources/<program>/ \
      ../pe-<program>-rules/docs/agents/sources/<program>/
```

**Test Creator** (in isolated worktree):
```bash
cd ../pe-<program>-tests
# Creates tests based ONLY on documents
# CANNOT see any implementation in feature/<program>-rules
git add policyengine_us/tests/
git commit -m "Add <program> integration tests"
git push origin feature/<program>-tests
```

**Rules Engineer** (in isolated worktree):
```bash
cd ../pe-<program>-rules
# Creates implementation based ONLY on documents
# CANNOT see any tests in feature/<program>-tests
git add policyengine_us/parameters/ policyengine_us/variables/
git commit -m "Implement <program> rules"
git push origin feature/<program>-rules
```

### Phase 3: Integration and Verification

Only now does Supervisor merge everything:

```bash
# Create verification branch
git checkout master
git checkout -b feature/<program>-verify

# Merge all work (first time components see each other)
git merge --no-ff feature/<program>-docs
git merge --no-ff feature/<program>-rules  
git merge --no-ff feature/<program>-tests

# Now Reviewer can see everything and validate
```

### Phase 4: Verification

Reviewer works on the merged branch:
- Validates documentation compliance
- Runs all tests
- Checks references
- **Can now see both tests and implementation together**

### Phase 5: Iteration (Multiple Rounds Expected)

The development process is inherently iterative. Expect 3-5 rounds of verification and fixes for complex programs.

#### Iteration Round Structure:

```bash
# Round 1: Initial Verification
git checkout feature/<program>-verify
git merge --no-ff feature/<program>-docs
git merge --no-ff feature/<program>-rules  
git merge --no-ff feature/<program>-tests
# Reviewer finds 15 issues

# Round 1: Fixes
cd ../pe-<program>-rules
# Rules Engineer fixes 10 issues based on document references
git add -A && git commit -m "Round 1: Fix parameter values and calculation logic"
git push

cd ../pe-<program>-tests  
# Test Creator fixes 5 issues based on document references
git add -A && git commit -m "Round 1: Add missing test cases and fix calculations"
git push

# Round 2: Re-verification
git checkout feature/<program>-verify
git reset --hard origin/master
git merge --no-ff feature/<program>-docs
git merge --no-ff feature/<program>-rules  # Updated
git merge --no-ff feature/<program>-tests  # Updated
# Reviewer finds 3 issues

# Round 2: Fixes
cd ../pe-<program>-rules
# Rules Engineer fixes remaining issues
git add -A && git commit -m "Round 2: Handle edge cases"
git push

# Round 3: Final Verification
git checkout feature/<program>-verify
git reset --hard origin/master
git merge --no-ff feature/<program>-docs
git merge --no-ff feature/<program>-rules  # Final
git merge --no-ff feature/<program>-tests  # Final
# Reviewer confirms: ALL TESTS PASS ✓
```

#### Maintaining Isolation During Iterations:

Each agent continues working in their isolated worktree:
- Rules Engineer never sees test expectations, even during fixes
- Test Creator never sees implementation, even during fixes
- Supervisor translates issues into document-based fix requests

#### Example Fix Request Translation:

```markdown
❌ WRONG (breaks isolation):
"The test expects $450 but implementation returns $500"

✅ CORRECT (maintains isolation):
"Review the shelter deduction calculation in 7 CFR 273.9(d)(6)(ii), 
particularly the order of applying the cap versus the 50% calculation"
```

## Information Flow Control

### What Each Agent Receives

| Agent | Receives | Never Sees (Until Verification) |
|-------|----------|----------------------------------|
| Document Collector | Program requirements | Tests, Implementation |
| Test Creator | Documents only | Implementation, Parameters |
| Rules Engineer | Documents only | Integration tests, Expected values |
| Reviewer | Everything (after merge) | N/A |

### Supervisor's Role in Isolation

The Supervisor must:
1. **Never** share test values with Rules Engineer
2. **Never** share implementation with Test Creator
3. **Only** share documents between agents
4. Manage all branch merging
5. Route fix requests without revealing why

### Example Fix Request Routing

❌ **Wrong** (reveals test information):
```
"Rules Engineer: The benefit calculation returns $450 but should return $500"
```

✅ **Correct** (references documentation only):
```
"Rules Engineer: Please review the shelter deduction calculation 
against 7 CFR 273.9(d)(6)(ii). Ensure the excess shelter amount 
is calculated as specified in the regulation."
```

## Audit Trail

Supervisor maintains audit log:

```markdown
# <Program> Development Audit Log

## Phase 1: Documents
- Collector started: 2024-01-10 09:00
- Documents completed: 2024-01-10 11:00
- Files created: 6 documents

## Phase 2: Parallel Development  
- Documents distributed: 2024-01-10 11:30
- Test Creator started: 2024-01-10 11:35
- Rules Engineer started: 2024-01-10 11:35
- Tests completed: 2024-01-10 14:00
- Rules completed: 2024-01-10 15:00

## Information Isolation Verified:
- Test Creator worktree never had access to rules branch ✓
- Rules Engineer worktree never had access to tests branch ✓
- Only documents were shared between agents ✓

## Phase 3: Verification
- Branches merged: 2024-01-10 15:30
- Reviewer started: 2024-01-10 15:35
- Issues found: 3
- All issues resolved: 2024-01-10 17:00
```

## Technical Implementation

### Using Git Worktrees for Isolation

```bash
# Setup script for Supervisor
#!/bin/bash
PROGRAM=$1

# Create branches
git checkout -b feature/${PROGRAM}-docs
git checkout -b feature/${PROGRAM}-tests
git checkout -b feature/${PROGRAM}-rules

# Create isolated worktrees
git worktree add ../pe-${PROGRAM}-docs feature/${PROGRAM}-docs
git worktree add ../pe-${PROGRAM}-tests feature/${PROGRAM}-tests
git worktree add ../pe-${PROGRAM}-rules feature/${PROGRAM}-rules

echo "Isolated environments created:"
echo "  Docs: ../pe-${PROGRAM}-docs/"
echo "  Tests: ../pe-${PROGRAM}-tests/"
echo "  Rules: ../pe-${PROGRAM}-rules/"
```

### Cleanup After Development

```bash
# Remove worktrees
git worktree remove ../pe-<program>-docs
git worktree remove ../pe-<program>-tests
git worktree remove ../pe-<program>-rules

# Delete branches after PR is merged
git branch -d feature/<program>-docs
git branch -d feature/<program>-tests
git branch -d feature/<program>-rules
```

## Benefits of This Approach

1. **True Isolation**: Physical separation via worktrees
2. **Parallel Development**: Test and rules developed simultaneously
3. **No Contamination**: Impossible for agents to see each other's work
4. **Audit Trail**: Clear record of isolation maintained
5. **Quality Assurance**: Independent development ensures accuracy

## Summary

This workflow ensures that:
- Test Creator never sees implementation until verification
- Rules Engineer never sees expected test values until verification
- Both work from the same authoritative documents
- Reviewer validates everything works together correctly
- Complete audit trail proves isolation was maintained

The physical separation through git worktrees makes it technically impossible for agents to violate isolation rules.