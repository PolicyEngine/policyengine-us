#!/bin/bash
# Claude Code Hook - Enforces agent isolation in multi-agent development
# This hook prevents agents from accessing each other's work directories

# Determine which agent is running based on current directory or environment
CURRENT_DIR=$(pwd)
COMMAND="$1"
ARGS="${@:2}"

# Function to check if a path is being accessed
check_path_access() {
    local path="$1"
    local agent="$2"
    local forbidden_patterns="$3"
    
    for pattern in $forbidden_patterns; do
        if [[ "$path" =~ $pattern ]]; then
            echo "❌ ERROR: $agent cannot access $pattern files/directories"
            echo "Isolation violation: $agent must work only with authorized files"
            echo "Attempted access: $path"
            return 1
        fi
    done
    return 0
}

# Detect which agent based on worktree location
if [[ "$CURRENT_DIR" =~ "pe-.*-tests" ]] || [[ "$CLAUDE_AGENT" == "test_creator" ]]; then
    AGENT="Test Creator"
    FORBIDDEN="pe-.*-rules|rules_engineer|/variables/|/parameters/"
    
elif [[ "$CURRENT_DIR" =~ "pe-.*-rules" ]] || [[ "$CLAUDE_AGENT" == "rules_engineer" ]]; then
    AGENT="Rules Engineer"
    FORBIDDEN="pe-.*-tests|test_creator|/tests/.*integration|integration.*\.yaml"
    
elif [[ "$CLAUDE_AGENT" == "document_collector" ]]; then
    AGENT="Document Collector"
    FORBIDDEN="pe-.*-tests|pe-.*-rules|test_creator|rules_engineer"
    
else
    # Supervisor or reviewer can access everything
    exit 0
fi

# Check command for file access attempts
case "$COMMAND" in
    cat|less|more|head|tail|grep|find|ls|cd|open|code|vim|nano|emacs)
        for arg in $ARGS; do
            check_path_access "$arg" "$AGENT" "$FORBIDDEN" || exit 1
        done
        ;;
    *)
        # For other commands, check if arguments contain forbidden paths
        for arg in $ARGS; do
            if [[ -e "$arg" ]]; then
                check_path_access "$arg" "$AGENT" "$FORBIDDEN" || exit 1
            fi
        done
        ;;
esac

# Log access attempts for audit trail
if [[ -n "$AGENT" ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $AGENT: $COMMAND $ARGS" >> ~/.claude/agent_audit.log
fi

# Allow command to proceed
exit 0