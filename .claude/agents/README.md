# PolicyEngine Agent System

## Overview

This directory contains specialized agents for PolicyEngine development. These agents ensure accurate implementation of government benefit programs through isolated development and comprehensive review.

## Available Agents

### Multi-Agent Development System
For implementing new programs with maximum accuracy:
- **supervisor.md** - Orchestrates isolated development workflow
- **document_collector.md** - Gathers authoritative sources
- **test_creator.md** - Creates tests from documentation (in isolation)
- **rules_engineer.md** - Implements from documentation (in isolation)
- **verifier.md** - Validates merged implementation

See **workflow.md** for detailed technical implementation of the multi-agent system.

### Standalone Agents
- **policyengine-reviewer.md** - Unified reviewer for all PolicyEngine PRs
  - Verifies source documentation
  - Checks vectorization
  - Validates test quality
  - Can also act as verifier in multi-agent system

### Shared Resources
- **policyengine-standards.md** - Core standards all agents follow
  - Source citation requirements
  - Vectorization rules
  - Common pitfalls
  - Testing standards

## Quick Start

### For Regular PR Review
Use the `policyengine-reviewer` agent to review any PolicyEngine PR.

### For New Program Implementation
1. Start with the `supervisor` agent
2. Follow the multi-agent workflow in `workflow.md`
3. Maintain isolation between test creator and rules engineer
4. Use verifier (or policyengine-reviewer in verifier mode) for validation

## Key Principles

1. **Source Authority**: Statutes > Regulations > Websites
2. **Isolation**: Tests and implementation developed separately
3. **Vectorization**: No if-elif-else with household data
4. **Documentation**: Every value traces to primary source
5. **Testing**: Document calculations with regulation references

## Note

These agents are designed for PolicyEngine's rule engine implementation. They focus on accurate transcription of laws and regulations into code, not scientific research or analysis.