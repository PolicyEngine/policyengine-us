---
description: Review and fix issues in an existing PR, addressing GitHub comments
---

# Reviewing PR: $ARGUMENTS

## Determining Which PR to Review

First, determine which PR to review based on the arguments:

```bash
# If no arguments provided, use current branch's PR
if [ -z "$ARGUMENTS" ]; then
    CURRENT_BRANCH=$(git branch --show-current)
    PR_NUMBER=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number')
    if [ -z "$PR_NUMBER" ]; then
        echo "No PR found for current branch $CURRENT_BRANCH"
        exit 1
    fi
# If argument is a number, use it directly
elif [[ "$ARGUMENTS" =~ ^[0-9]+$ ]]; then
    PR_NUMBER=$ARGUMENTS
# Otherwise, search for PR by description/title
else
    PR_NUMBER=$(gh pr list --search "$ARGUMENTS" --json number,title --jq '.[0].number')
    if [ -z "$PR_NUMBER" ]; then
        echo "No PR found matching: $ARGUMENTS"
        exit 1
    fi
fi

echo "Reviewing PR #$PR_NUMBER"
```

Orchestrate agents to review, validate, and fix issues in PR #$PR_NUMBER, addressing all GitHub review comments.

## ⚠️ CRITICAL: Agent Usage is MANDATORY

**You are a coordinator, NOT an implementer. You MUST:**
1. **NEVER make direct code changes** - always use agents
2. **INVOKE agents with specific, detailed instructions**
3. **WAIT for each agent to complete** before proceeding
4. **VERIFY agent outputs** before moving to next phase

**If you find yourself using Edit, Write, or MultiEdit directly, STOP and invoke the appropriate agent instead.**

## Phase 1: PR Analysis
After determining PR_NUMBER above, gather context about the PR and review comments:

```bash
gh pr view $PR_NUMBER --comments
gh pr checks $PR_NUMBER  # Note: CI runs on draft PRs too!
gh pr diff $PR_NUMBER
```

Document findings:
- Current CI status (even draft PRs have CI)
- Review comments to address
- Files changed
- Type of implementation (new program, bug fix, enhancement)

## Phase 2: Enhanced Domain Validation
Run comprehensive validation using specialized agents:

### Step 1: Domain-Specific Validation
Invoke **policy-domain-validator** to check:
- Federal/state jurisdiction separation
- Variable naming conventions and duplicates
- Hard-coded value patterns
- Performance optimization opportunities
- Documentation placement
- PolicyEngine-specific patterns

### Step 2: Reference Validation
Invoke **reference-validator** to verify:
- All parameters have references
- References actually corroborate values
- Federal sources for federal params
- State sources for state params
- Specific citations, not generic links

### Step 3: Implementation Validation
Invoke **implementation-validator** to check:
- No hard-coded values in formulas
- Complete implementations (no TODOs)
- Proper entity usage
- Correct formula patterns

Create a comprehensive checklist:
- [ ] Domain validation issues
- [ ] Reference validation issues
- [ ] Implementation issues
- [ ] Review comments to address
- [ ] CI failures to fix

## Phase 3: Sequential Fix Application

**CRITICAL: You MUST use agents for ALL fixes. DO NOT make direct edits yourself.**

Based on issues found, invoke agents IN ORDER to avoid conflicts.

**Why Sequential**: Unlike initial implementation where we need isolation, PR fixes must be applied sequentially because:
- Each fix builds on the previous one
- Avoids merge conflicts
- Tests need to see the fixed implementation
- Documentation needs to reflect the final code

**MANDATORY AGENT USAGE - Apply fixes in this exact order:**

### Step 1: Fix Domain & Parameter Issues
```markdown
YOU MUST INVOKE THESE AGENTS - DO NOT FIX DIRECTLY:

1. First, invoke policy-domain-validator:
   "Scan all files in this PR and create a comprehensive list of all domain violations"

2. Then invoke parameter-architect (REQUIRED for ANY hard-coded values):
   "Design parameter structure for these hard-coded values found: [list all values]
    Create the YAML parameter files with proper federal/state separation"

3. Then invoke rules-engineer (REQUIRED for code changes):
   "Refactor all variables to use the new parameters created by parameter-architect.
    Fix all hard-coded values in: [list files]"

4. Then invoke reference-validator:
   "Add proper references to all new parameters created"

5. ONLY AFTER all agents complete: Commit changes
```

### Step 2: Add Missing Tests (MANDATORY)
```markdown
REQUIRED - Must generate tests even if none were failing:

1. Invoke edge-case-generator:
   "Generate boundary tests for all parameters created in Step 1.
    Test edge cases for: [list all new parameters]"

2. Invoke test-creator:
   "Create integration tests for the refactored Idaho LIHEAP implementation.
    Include tests for all new parameter files created."

3. VERIFY tests pass before committing
4. Commit test additions
```

### Step 3: Enhance Documentation
1. **documentation-enricher**: Add examples and references to updated code
2. Commit documentation improvements

### Step 4: Optimize Performance (if needed)
1. **performance-optimizer**: Vectorize and optimize calculations
2. Run tests to ensure no regressions
3. Commit optimizations

### Step 5: Validate Integrations
1. **cross-program-validator**: Check benefit interactions
2. Fix any cliff effects or integration issues found
3. Commit integration fixes

## Phase 4: Apply Fixes
For each issue identified:

1. **Read current implementation**
   ```bash
   gh pr checkout $PR_NUMBER
   ```

2. **Apply agent-generated fixes**
   - Use Edit/MultiEdit for targeted fixes
   - Preserve existing functionality
   - Add only what's needed

3. **Verify fixes locally**
   ```bash
   make test
   make format
   ```

## Phase 5: Address Review Comments
For each GitHub comment:

1. **Parse comment intent**
   - Is it requesting a change?
   - Is it asking for clarification?
   - Is it pointing out an issue?

2. **Generate response**
   - If change requested: Apply fix and confirm
   - If clarification: Add documentation/comment
   - If issue: Fix and explain approach

3. **Post response on GitHub**
   ```bash
   gh pr comment $PR_NUMBER --body "Addressed: [explanation of fix]"
   ```

## Phase 6: CI Validation
Invoke ci-fixer to ensure all checks pass:

1. **Push fixes**
   ```bash
   git add -A
   git commit -m "Address review comments

   - Fixed hard-coded values identified in review
   - Added missing tests for edge cases
   - Enhanced documentation with examples
   - Optimized performance issues
   
   Addresses comments from @reviewer"
   git push
   ```

2. **Monitor CI**
   ```bash
   gh pr checks $PR_NUMBER --watch
   ```

3. **Fix any CI failures**
   - Format issues: `make format`
   - Test failures: Fix with targeted agents
   - Lint issues: Apply corrections

## Phase 7: Final Review & Summary
Invoke rules-reviewer for final validation:
- All comments addressed?
- All tests passing?
- No regressions introduced?

Post summary comment:
```bash
gh pr comment $PR_NUMBER --body "## Summary of Changes

### Issues Addressed
✅ Fixed hard-coded values in [files]
✅ Added parameterization for [values]
✅ Enhanced test coverage (+X tests)
✅ Improved documentation
✅ All CI checks passing

### Review Comments Addressed
- @reviewer1: [Issue] → [Fix applied]
- @reviewer2: [Question] → [Clarification added]

### Ready for Re-Review
All identified issues have been addressed. The implementation now:
- Uses parameters for all configurable values
- Has comprehensive test coverage  
- Includes documentation with examples
- Passes all CI checks"
```

## Command Options

### Usage Examples
- `/review-pr` - Review PR for current branch
- `/review-pr 6444` - Review PR #6444
- `/review-pr "Idaho LIHEAP"` - Search for and review PR by title/description

### Quick Fix Mode
`/review-pr [PR] --quick`
- Only fix CI failures
- Skip comprehensive review
- Focus on getting checks green

### Deep Review Mode  
`/review-pr [PR] --deep`
- Run all validators
- Generate comprehensive tests
- Full documentation enhancement
- Cross-program validation

### Comment Only Mode
`/review-pr [PR] --comments-only`
- Only address GitHub review comments
- Skip additional validation
- Faster turnaround

## Success Metrics

The PR is ready when:
- ✅ All CI checks passing
- ✅ All review comments addressed
- ✅ No hard-coded values
- ✅ Comprehensive test coverage
- ✅ Documentation complete
- ✅ No performance issues

## Common Review Patterns

### "Hard-coded value" Comment
1. Identify the value
2. Create parameter with parameter-architect
3. Update implementation with rules-engineer
4. Add test with test-creator

### "Missing test" Comment  
1. Identify the scenario
2. Use edge-case-generator for boundaries
3. Use test-creator for integration tests
4. Verify with implementation-validator

### "Needs documentation" Comment
1. Use documentation-enricher
2. Add calculation examples
3. Add regulatory references
4. Explain edge cases

### "Performance issue" Comment
1. Use performance-optimizer
2. Vectorize operations
3. Remove redundant calculations
4. Test with large datasets

## Error Handling

If agents produce conflicting fixes:
1. Prioritize fixes that address review comments
2. Ensure no regressions
3. Maintain backward compatibility
4. Document any tradeoffs

## Pre-Flight Checklist

Before starting, confirm:
- [ ] I will NOT make direct edits (no Edit/Write/MultiEdit by coordinator)
- [ ] I will invoke agents for ALL changes
- [ ] I will wait for each agent to complete
- [ ] I will generate tests even if current tests pass
- [ ] I will commit after each agent phase

Start with determining which PR to review, then proceed to Phase 1: Analyze the PR and review comments.