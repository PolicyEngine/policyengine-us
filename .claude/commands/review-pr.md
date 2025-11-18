---
description: Review an existing PR and post findings to GitHub (does not make code changes)
---

# Reviewing PR: $ARGUMENTS

**READ-ONLY MODE**: This command analyzes the PR and posts a comprehensive review to GitHub WITHOUT making any code changes.

Use `/fix-pr` to apply fixes automatically.

## Important: Avoiding Duplicate Reviews

**Before posting**, check if you already have an active review on this PR. If you do AND there are no replies from others:
- Delete your old comments
- Post a single updated review
- DO NOT create multiple review comments

Only post additional reviews if others have engaged with your previous review.

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

## Phase 1: PR Analysis

Gather context about the PR:

```bash
gh pr view $PR_NUMBER --comments
gh pr checks $PR_NUMBER
gh pr diff $PR_NUMBER
```

Document findings:
- Current CI status
- Existing review comments
- Files changed
- Type of implementation (new program, bug fix, enhancement)

## Phase 2: Comprehensive Validation (Read-Only)

Run validators to COLLECT issues (do not fix):

### Step 1: Domain Validation
Invoke **policy-domain-validator** to identify:
- Federal/state jurisdiction issues
- Variable naming violations
- Hard-coded values
- Performance optimization opportunities
- Documentation gaps
- PolicyEngine pattern violations

**IMPORTANT**: Instruct agent to ONLY report issues, not fix them.

### Step 2: Reference Validation
Invoke **reference-validator** to check:
- Missing parameter references
- References that don't corroborate values
- Incorrect source types (federal vs state)
- Generic/vague citations

### Step 3: Implementation Validation
Invoke **implementation-validator** to identify:
- Hard-coded values in formulas
- Incomplete implementations (TODOs, stubs)
- Entity usage errors
- Formula pattern violations

### Step 4: Test Coverage Analysis
Invoke **edge-case-generator** to identify:
- Missing boundary tests
- Untested edge cases
- Parameter combinations not tested

### Step 5: Documentation Review
Invoke **documentation-enricher** to find:
- Missing docstrings
- Lack of calculation examples
- Missing regulatory references
- Unclear variable descriptions

## Phase 3: Collect and Organize Findings

Aggregate all issues into structured format:

```json
{
  "overall_summary": "Brief summary of PR quality and main concerns",
  "severity": "APPROVE|COMMENT|REQUEST_CHANGES",
  "line_comments": [
    {
      "path": "policyengine_us/variables/gov/states/ma/dta/ccfa/income.py",
      "line": 42,
      "body": "💡 **Hard-coded value detected**\n\nThis value should be parameterized:\n\n```suggestion\nmax_income = parameters(period).gov.states.ma.dta.ccfa.max_income\n```\n\n📚 See: [Parameter Guidelines](https://github.com/PolicyEngine/policyengine-us/blob/master/CLAUDE.md#parameter-structure-best-practices)"
    },
    {
      "path": "policyengine_us/tests/variables/gov/states/ma/dta/ccfa/test_eligibility.yaml",
      "line": 15,
      "body": "🧪 **Missing edge case test**\n\nConsider adding a test for income exactly at the threshold:\n\n```yaml\n- name: At threshold\n  period: 2024-01\n  input:\n    household_income: 75_000\n  output:\n    ma_ccfa_eligible: true\n```"
    }
  ],
  "general_comments": [
    "Consider adding integration tests for multi-child households",
    "Documentation could benefit from real-world calculation examples"
  ]
}
```

## Phase 4: Check for Existing Reviews

**IMPORTANT**: Before posting a new review, check if you already have an active review:

```bash
# Check for existing reviews from you (Claude)
EXISTING_REVIEWS=$(gh api "/repos/{owner}/{repo}/pulls/$PR_NUMBER/reviews" \
  --jq '[.[] | select(.user.login == "MaxGhenis") | {id: .id, state: .state, submitted_at: .submitted_at}]')

# Check if there are any comments/replies from others since your last review
LATEST_REVIEW_TIME=$(echo "$EXISTING_REVIEWS" | jq -r '.[0].submitted_at // empty')

if [ -n "$LATEST_REVIEW_TIME" ]; then
  # Check for comments after your review
  COMMENTS_AFTER=$(gh api "/repos/{owner}/{repo}/issues/$PR_NUMBER/comments" \
    --jq "[.[] | select(.created_at > \"$LATEST_REVIEW_TIME\" and .user.login != \"MaxGhenis\")]")

  if [ -z "$COMMENTS_AFTER" ] || [ "$COMMENTS_AFTER" == "[]" ]; then
    echo "Existing review found with no replies from others"
    echo "STRATEGY: Delete old comments and post single updated review"

    # Delete old comment-only reviews/comments
    gh api "/repos/{owner}/{repo}/issues/$PR_NUMBER/comments" \
      --jq '.[] | select(.user.login == "MaxGhenis") | .id' | \
      while read comment_id; do
        gh api --method DELETE "/repos/{owner}/{repo}/issues/comments/$comment_id"
      done
  else
    echo "Others have replied to your review - will add new review"
  fi
fi
```

## Phase 5: Post GitHub Review

Post the review using GitHub CLI:

```bash
# Create review comments JSON
cat > /tmp/review_comments.json <<'EOF'
[FORMATTED_COMMENTS_ARRAY]
EOF

# Post the review with inline comments
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/{owner}/{repo}/pulls/$PR_NUMBER/reviews" \
  -f body="$OVERALL_SUMMARY" \
  -f event="$SEVERITY" \
  -F comments=@/tmp/review_comments.json
```

### Severity Guidelines

- **APPROVE**: Minor suggestions only, no critical issues
- **COMMENT**: Has issues but not blocking (educational feedback)
- **REQUEST_CHANGES**: Has critical issues that must be fixed:
  - Hard-coded values
  - Missing tests for core functionality
  - Incorrect implementations
  - Missing required documentation

## Phase 6: Post Summary Comment

Add a comprehensive summary as a regular comment:

```bash
gh pr comment $PR_NUMBER --body "## 📋 Review Summary

### ✅ Strengths
- [List positive aspects]
- Well-structured variable organization
- Clear parameter names

### 🔍 Issues Found

#### Critical (Must Fix)
- [ ] 3 hard-coded values in income calculations
- [ ] Missing edge case tests for boundary conditions
- [ ] Parameter references not corroborated by sources

#### Suggestions (Optional)
- [ ] Consider vectorization in \`calculate_benefit()\`
- [ ] Add calculation walkthrough to documentation
- [ ] Extract shared logic into helper variable

### 📊 Validation Results
- **Domain Validation**: X issues
- **Reference Validation**: X issues
- **Implementation Validation**: X issues
- **Test Coverage**: X gaps identified
- **Documentation**: X improvements suggested

### 🚀 Next Steps

To apply these fixes automatically, run:
\`\`\`bash
/fix-pr $PR_NUMBER
\`\`\`

Or address manually and re-request review when ready.

---
💡 **Tip**: Use \`/fix-pr\` to automatically apply all suggested fixes."
```

## Phase 6: CI Status Check

If CI is failing, include CI failure summary:

```bash
gh pr checks $PR_NUMBER --json name,status,conclusion \
  --jq '.[] | select(.conclusion == "failure") | "❌ " + .name'
```

Add to review:
```
### ⚠️ CI Failures
- ❌ lint: Black formatting issues
- ❌ test: 3 test failures in test_income.py

Run `/fix-pr` to automatically fix these issues.
```

## Command Options

### Usage Examples
- `/review-pr` - Review PR for current branch
- `/review-pr 6390` - Review PR #6390
- `/review-pr "Massachusetts CCFA"` - Search for and review PR by title

### Validation Modes

#### Standard Review (Default)
- All validators run
- Comprehensive analysis
- Balanced severity

#### Quick Review
`/review-pr [PR] --quick`
- Skip deep validation
- Focus on CI failures and critical issues
- Faster turnaround

#### Strict Review
`/review-pr [PR] --strict`
- Maximum scrutiny
- Flag even minor style issues
- Request changes for any violations

## Output Format

The review will include:

1. **Overall Summary**: High-level assessment
2. **Inline Comments**: Specific issues at exact lines
3. **Code Suggestions**: GitHub suggestion blocks where applicable
4. **Summary Comment**: Checklist of all issues
5. **Next Steps**: How to address findings

## Review Categories

### 🔴 Critical Issues (Always flag)
- Hard-coded values in formulas
- Missing parameter references
- Incorrect formula implementations
- Missing tests for core functionality
- CI failures

### 🟡 Suggestions (Optional improvements)
- Performance optimizations
- Documentation enhancements
- Code style improvements
- Additional test coverage
- Refactoring opportunities

### 🟢 Positive Feedback
- Well-implemented patterns
- Good test coverage
- Clear documentation
- Proper parameterization

## Success Criteria

A good review should:
- ✅ Identify all hard-coded values
- ✅ Flag missing/incorrect references
- ✅ Suggest specific improvements with examples
- ✅ Provide actionable next steps
- ✅ Be respectful and constructive
- ✅ Include code suggestion blocks for easy application

## Common Review Patterns

### Hard-coded Value
```markdown
💡 **Hard-coded value detected**

This value should be parameterized. Create a parameter:

\`\`\`yaml
# policyengine_us/parameters/gov/states/ma/program/threshold.yaml
values:
  2024-01-01: 75000
metadata:
  unit: currency-USD
  period: year
  reference: [Link to source]
\`\`\`

Then use in formula:
\`\`\`suggestion
threshold = parameters(period).gov.states.ma.program.threshold
\`\`\`
```

### Missing Test
```markdown
🧪 **Missing edge case test**

Add test for boundary condition:

\`\`\`yaml
- name: At exact threshold
  period: 2024-01
  input:
    income: 75_000
  output:
    eligible: false  # Just above threshold
\`\`\`
```

### Missing Documentation
```markdown
📚 **Documentation enhancement**

Add docstring with example:

\`\`\`suggestion
def formula(person, period, parameters):
    """
    Calculate benefit amount.

    Example:
        Income $50,000 → Benefit $2,400
        Income $75,000 → Benefit $1,200

    Reference: MA DTA Regulation 106 CMR 702.310
    """
\`\`\`
```

### Performance Issue
```markdown
⚡ **Vectorization opportunity**

Replace loop with vectorized operation:

\`\`\`suggestion
return where(
    household_size == 1,
    base_amount,
    base_amount * household_size * 0.7
)
\`\`\`
```

## Error Handling

If validation agents fail:
1. Run basic validation manually
2. Document what couldn't be checked
3. Note limitations in review
4. Still post whatever findings were collected

## Pre-Flight Checklist

Before starting, confirm:
- [ ] I will NOT make any code changes
- [ ] I will ONLY analyze and post reviews
- [ ] I will collect findings from all validators
- [ ] I will format findings as GitHub review comments
- [ ] I will provide actionable suggestions
- [ ] I will be constructive and respectful

Start by determining which PR to review, then proceed to Phase 1: Analyze the PR.
