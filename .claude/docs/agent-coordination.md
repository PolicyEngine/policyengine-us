# Agent Coordination Guide

## The Problem We're Solving

In the test run of `/review-pr`, the command orchestrator:
- Made direct edits instead of using agents
- Skipped test generation
- Didn't leverage specialized agent expertise

## Mandatory Agent Usage Pattern

### 1. Validation Phase - Information Gathering
```markdown
ALWAYS invoke these three in sequence:
1. policy-domain-validator → Get list of all issues
2. reference-validator → Check all references  
3. implementation-validator → Find code problems

COLLECT all issues into a master list before fixing anything.
```

### 2. Fixing Phase - Specialized Agents Only

**NEVER do this (coordinator making direct changes):**
```python
# BAD - Coordinator using Edit directly
Edit(file="variable.py", old="return 0.5", new="return p.factor")
```

**ALWAYS do this (delegate to agents):**
```markdown
# GOOD - Invoke specialist agent
/invoke rules-engineer "Fix hard-coded 0.5 in variable.py line 23. 
The parameter-architect created 'adjustment_factor' parameter at 
gov/states/id/program/factors.yaml"
```

### 3. Agent Invocation Templates

#### For Parameter Extraction:
```markdown
/invoke parameter-architect "Extract these hard-coded values to parameters:
- File: variables/benefit.py, Line 15: 0.5 (adjustment factor)
- File: variables/eligible.py, Line 23: months [10,3] (heating season)
- File: variables/amount.py, Line 8: 7500 (8+ person limit)

Create parameter files with proper federal/state separation.
Use Idaho LIHEAP State Plan as reference."
```

#### For Code Refactoring:
```markdown
/invoke rules-engineer "Refactor these files to use parameters:
- variables/benefit.py: Use adjustment_factor from gov/states/id/liheap/factors.yaml
- variables/eligible.py: Use heating_season from gov/states/id/liheap/season.yaml
- variables/amount.py: Use income_limits.eight_plus from gov/states/id/liheap/limits.yaml

The parameter files were created by parameter-architect."
```

#### For Test Generation:
```markdown
/invoke test-creator "Create integration tests for:
- New parameter: gov/states/id/liheap/heating_season.yaml
- New parameter: gov/states/id/liheap/income_limits.yaml
- Refactored variable: id_liheap_seasonal_benefit.py

Test that parameters are correctly applied in calculations."
```

## Sequential Execution Rules

### Why Sequential Matters:
1. **Parameter-architect MUST run before rules-engineer**
   - Rules-engineer needs the parameter files to exist
   
2. **Rules-engineer MUST run before test-creator**
   - Tests need the refactored code to test against

3. **Each agent MUST commit before next agent**
   - Prevents merge conflicts
   - Allows next agent to see changes

### Proper Sequencing:
```bash
1. validation agents → identify all issues
2. git status → understand current state
3. parameter-architect → create ALL parameter files
4. git add && git commit → lock in parameters
5. rules-engineer → refactor ALL code
6. git add && git commit → lock in refactoring  
7. test-creator → generate tests
8. git add && git commit → lock in tests
9. reference-validator → final check
```

## Red Flags That You're Doing It Wrong

### 🚫 Coordinator Anti-Patterns:
- Using `Edit`, `Write`, or `MultiEdit` directly
- Creating parameter files yourself
- Refactoring code yourself
- Making "quick fixes" without agents
- Skipping test generation because "tests pass"

### ✅ Correct Patterns:
- Every code change goes through an agent
- Every parameter creation uses parameter-architect
- Every refactor uses rules-engineer
- Tests are ALWAYS generated, even if existing tests pass
- Agents are invoked with complete context

## Agent Communication Protocol

### Information Agents Must Share:

**From validator to architect:**
```markdown
"Found these hard-coded values:
- 0.5 at line 23 (appears to be crisis benefit reduction factor)
- [10, 3] at line 45 (heating season months)
- 7500 at line 67 (income limit for 8+ households)"
```

**From architect to engineer:**
```markdown
"Created these parameter files:
- gov/states/id/liheap/factors.yaml with 'crisis_reduction'
- gov/states/id/liheap/season.yaml with 'start_month' and 'end_month'
- gov/states/id/liheap/limits.yaml with 'eight_plus_person'"
```

**From engineer to test-creator:**
```markdown
"Refactored these variables to use parameters:
- id_liheap_crisis_benefit now uses factors.crisis_reduction
- id_liheap_seasonal_eligible now uses season.start_month/end_month
- id_liheap_income_eligible now uses limits.eight_plus_person"
```

## Measuring Success

### Good Review Run:
- 5+ agents invoked
- 0 direct edits by coordinator
- All hard-coded values parameterized
- Tests generated for all changes
- Each agent commits its work

### Bad Review Run:
- < 3 agents invoked
- Coordinator makes direct edits
- Some hard-coded values remain
- No new tests generated
- Single large commit with mixed changes

## Emergency Override

Only make direct changes if:
1. Agent repeatedly fails (3+ attempts)
2. Trivial typo fix (single character)
3. Urgent CI fix blocking everything

Even then, document why you overrode the agent system.

## The Golden Rule

**If you're typing code, you're doing it wrong.**

The coordinator should only:
- Read files to understand context
- Invoke agents with instructions
- Verify agent work
- Commit agent outputs
- Monitor CI

Everything else goes through agents.