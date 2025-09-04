# Enforcing Agent Isolation - Technical Options

## Current Approach: Trust + Git Worktrees
Agents work in separate worktrees and are instructed not to access others. This relies on compliance.

## Stronger Enforcement Options

### 1. Claude Code Hooks (Immediate)
Add to `.claude/claude_code_hook.sh`:
```bash
# Block access to other agent worktrees
if [[ "$CLAUDE_AGENT" == "test_creator" ]]; then
  if [[ "$1" =~ "pe-.*-rules" ]] || grep -q "rules_engineer" "$@" 2>/dev/null; then
    echo "ERROR: Test Creator cannot access Rules Engineer files"
    exit 1
  fi
fi

if [[ "$CLAUDE_AGENT" == "rules_engineer" ]]; then
  if [[ "$1" =~ "pe-.*-tests" ]] || grep -q "test_creator" "$@" 2>/dev/null; then
    echo "ERROR: Rules Engineer cannot access Test Creator files"
    exit 1
  fi
fi
```

### 2. File System Permissions (Stronger)
```bash
# Create users for each agent
sudo useradd -m test_creator
sudo useradd -m rules_engineer
sudo useradd -m supervisor

# Set worktree ownership
sudo chown -R test_creator:test_creator ../pe-program-tests
sudo chown -R rules_engineer:rules_engineer ../pe-program-rules
sudo chmod 700 ../pe-program-tests  # Only owner can access
sudo chmod 700 ../pe-program-rules

# Supervisor gets read access to all
sudo usermod -a -G test_creator,rules_engineer supervisor
```

### 3. Docker Containers (Strongest)
```dockerfile
# Dockerfile.test_creator
FROM ubuntu:latest
WORKDIR /workspace
COPY docs/agents/sources /sources
# No access to other code
```

```bash
# Run agents in isolated containers
docker run -v $(pwd)/docs:/sources test_creator
docker run -v $(pwd)/docs:/sources rules_engineer
```

### 4. Git Hooks (Repository Level)
`.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Prevent cross-contamination commits

BRANCH=$(git branch --show-current)
FILES=$(git diff --cached --name-only)

if [[ "$BRANCH" == "feature/*-tests" ]]; then
  if echo "$FILES" | grep -E "(rules|parameters|variables)"; then
    echo "ERROR: Test branch cannot modify implementation files"
    exit 1
  fi
fi

if [[ "$BRANCH" == "feature/*-rules" ]]; then
  if echo "$FILES" | grep -E "tests.*integration"; then
    echo "ERROR: Rules branch cannot modify integration tests"
    exit 1
  fi
fi
```

### 5. GitHub Actions (CI/CD Enforcement)
`.github/workflows/isolation-check.yml`:
```yaml
name: Verify Isolation
on: pull_request

jobs:
  check-isolation:
    runs-on: ubuntu-latest
    steps:
      - name: Check branch isolation
        run: |
          if [[ "${{ github.head_ref }}" == *"-tests" ]]; then
            # Verify no implementation files modified
            git diff --name-only origin/main..HEAD | grep -E "variables|parameters" && exit 1
          fi
```

## Recommended Approach

For PolicyEngine's purposes, I recommend:

1. **Start with Claude Code hooks** - Easy to implement immediately
2. **Add git hooks** - Prevent accidental commits
3. **Document in agent instructions** - Clear boundaries
4. **Monitor in CI** - Catch violations in PR review

This provides "defense in depth" without overly complex infrastructure.

## Implementation in Agent Instructions

Update each agent's instructions to include:

```markdown
## Isolation Enforcement

Your workspace is protected by technical controls:
- File access outside your worktree will be blocked
- Commits to wrong file types will be rejected
- The Supervisor monitors all access attempts

Stay within your designated directory:
- Test Creator: `../pe-<program>-tests/`
- Rules Engineer: `../pe-<program>-rules/`
```

This makes it architecturally enforced, not just suggested!