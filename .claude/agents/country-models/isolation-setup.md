# Setting Up Agent Isolation Enforcement

## Quick Setup

1. **Enable the Claude Code Hook**
   ```bash
   # Make hook executable (already done)
   chmod +x .claude/claude_code_hook.sh
   ```

2. **Work in Designated Worktrees**
   The hook automatically detects which agent you are based on your worktree:
   ```bash
   # Test Creator works here
   cd ../pe-<program>-tests
   
   # Rules Engineer works here
   cd ../pe-<program>-rules
   ```

## What Gets Blocked

### Test Creator
- ❌ Cannot access `../pe-*-rules/` directories
- ❌ Cannot read files in `/variables/` or `/parameters/`
- ❌ Cannot open implementation code
- ✅ Can access test files and documentation

### Rules Engineer  
- ❌ Cannot access `../pe-*-tests/` directories
- ❌ Cannot read integration test files
- ❌ Cannot see test expected values
- ✅ Can access parameters, variables, and documentation

### Document Collector
- ❌ Cannot access test or implementation directories
- ✅ Can only work with documentation

### Supervisor/Reviewer
- ✅ Can access everything (no restrictions)

## Testing the Isolation

Try these commands to verify isolation is working:

```bash
# As Test Creator (should fail)
export CLAUDE_AGENT=test_creator
cat ../pe-program-rules/variables/program.py  # BLOCKED

# As Rules Engineer (should fail)  
export CLAUDE_AGENT=rules_engineer
cat ../pe-program-tests/integration/test.yaml  # BLOCKED

# As Supervisor (should work)
export CLAUDE_AGENT=supervisor
cat ../pe-program-tests/integration/test.yaml  # ALLOWED
```

## Audit Trail

All access attempts are logged to `~/.claude/agent_audit.log` for review:
```bash
tail -f ~/.claude/agent_audit.log
```

## Troubleshooting

If the hook isn't working:
1. Check it's executable: `ls -la .claude/claude_code_hook.sh`
2. Verify environment variable: `echo $CLAUDE_AGENT`
3. Check audit log for attempts: `cat ~/.claude/agent_audit.log`

## For Agents

Add this to each agent's instructions:

```markdown
## Workspace Isolation

You are the [AGENT NAME] agent. Your workspace is protected:
- You CANNOT access other agents' directories
- Attempts to read forbidden files will be blocked
- All access is logged for audit

Your workspace: `../pe-<program>-[tests|rules|docs]/`
```