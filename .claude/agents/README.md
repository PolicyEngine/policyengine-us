# Multi-Agent Development System for PolicyEngine-US

## Overview

This directory contains instructions for a multi-agent development system designed to ensure accurate, well-tested implementation of government benefit programs. The system uses isolated development with multiple specialized agents to prevent contamination between test creation and implementation.

## Key Innovation: Isolation Through Separation

The core principle is that **tests and implementation are developed in complete isolation**:
- Test creators never see the implementation
- Rules engineers never see the test expectations
- Both work from the same authoritative documents
- Only the verifier sees everything, after development is complete

This prevents "teaching to the test" and ensures genuine implementation from first principles.

## The Agents

### 1. Supervisor Agent (`supervisor.md`)
- Orchestrates the entire process
- Manages information flow between agents
- Ensures isolation is maintained
- Creates and manages git branches/worktrees

### 2. Document Collector Agent (`document_collector.md`)
- Gathers statutes, regulations, and program manuals
- Creates authoritative documentation package
- Works in isolated branch: `feature/<program>-docs`

### 3. Test Creator Agent (`test_creator.md`)
- Creates integration tests from documents only
- Never sees implementation code
- Works in isolated branch: `feature/<program>-tests`
- Produces the "answer key" for validation

### 4. Rules Engineer Agent (`rules_engineer.md`)
- Implements parameters and variables from documents
- Uses Test-Driven Development with own unit tests
- Never sees integration test expectations
- Works in isolated branch: `feature/<program>-rules`

### 5. Verifier Agent (`verifier.md`)
- First point where tests and implementation meet
- Validates everything matches documentation
- Runs all tests and checks references
- Works on merged branch: `feature/<program>-verify`

## Workflow

See `workflow.md` for detailed technical implementation.

### Quick Start

1. **Supervisor** creates isolated branches and worktrees
2. **Document Collector** gathers all program documentation
3. **Test Creator** and **Rules Engineer** work in parallel:
   - Both receive documents only
   - Neither can see the other's work
   - Complete isolation via separate worktrees
4. **Supervisor** merges all branches for verification
5. **Verifier** validates the complete implementation
6. If issues found, **Supervisor** routes fixes without breaking isolation

## Directory Structure

```
docs/agents/
├── README.md              # This file
├── supervisor.md          # Supervisor agent instructions
├── document_collector.md  # Document collector instructions
├── test_creator.md        # Test creator instructions
├── rules_engineer.md      # Rules engineer instructions
├── verifier.md           # Verifier instructions
├── workflow.md           # Technical workflow details
└── sources/              # Program documentation (created by agents)
    └── <program>/        # Documents for each program
```

## Example Usage

To implement a new program (e.g., SNAP):

```bash
# Supervisor sets up isolation
git checkout -b feature/snap-docs
git checkout -b feature/snap-tests
git checkout -b feature/snap-rules

# Create isolated worktrees
git worktree add ../pe-snap-docs feature/snap-docs
git worktree add ../pe-snap-tests feature/snap-tests
git worktree add ../pe-snap-rules feature/snap-rules

# Each agent works in their isolated environment
# Document Collector works in ../pe-snap-docs/
# Test Creator works in ../pe-snap-tests/
# Rules Engineer works in ../pe-snap-rules/

# After completion, merge for verification
git checkout -b feature/snap-verify
git merge feature/snap-docs feature/snap-tests feature/snap-rules

# Verifier validates on merged branch
```

## Benefits

1. **Accuracy**: Implementation based on regulations, not test expectations
2. **Completeness**: Independent test creation ensures all cases covered
3. **Traceability**: Every line of code traces to documentation
4. **Quality**: Multiple validation points catch errors
5. **Audit Trail**: Complete record of isolated development

## Principles

- **No Contamination**: Agents cannot see each other's work during development
- **Document-Driven**: All development based on authoritative sources
- **Test-First**: Rules engineer uses TDD with unit tests
- **Independent Validation**: Test creator provides independent check
- **Comprehensive Verification**: Verifier ensures everything aligns

## Getting Started

1. Read `supervisor.md` to understand orchestration
2. Review `workflow.md` for technical details
3. Each agent should only read their specific instruction file
4. Maintain strict isolation throughout development

## Important Notes

- This system requires discipline to maintain isolation
- The Supervisor must never share test values with Rules Engineer
- The Supervisor must never share implementation with Test Creator
- Physical isolation through git worktrees prevents accidental contamination
- All communication between agents goes through the Supervisor

## Success Metrics

A successful implementation will have:
- ✅ All tests passing without the implementation ever seeing them during development
- ✅ All parameter values traceable to documentation
- ✅ Complete test coverage of documented scenarios
- ✅ No hardcoded values or test-specific logic
- ✅ Full audit trail showing isolation was maintained

## Contact

For questions or improvements to this multi-agent system, please file an issue or PR.