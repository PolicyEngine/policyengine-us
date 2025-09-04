# PolicyEngine Claude Agents

This repository contains specialized Claude agents for PolicyEngine development across different types of repositories.

## Repository Structure

```
agents/
├── country-models/     # Agents for country packages (policyengine-us, policyengine-uk, etc.)
│   ├── rules-reviewer.md      # Reviews rules implementations
│   ├── test_creator.md         # Creates tests from documentation
│   ├── rules_engineer.md      # Implements rules from documentation
│   ├── document_collector.md   # Collects authoritative sources
│   ├── supervisor.md           # Orchestrates multi-agent development
│   └── workflow.md            # Multi-agent workflow documentation
├── api/               # Agents for policyengine-api
│   └── api-reviewer.md        # Reviews API implementations
├── app/               # Agents for policyengine-app
│   └── app-reviewer.md        # Reviews React app code
└── shared/            # Shared resources across all repos
    ├── policyengine-standards.md  # Common standards and patterns
    └── model-evaluator.md         # Evaluates model outputs
```

## Usage

Each PolicyEngine repository should add this as a git submodule:

```bash
git submodule add https://github.com/PolicyEngine/.claude.git .claude
```

Then agents will be available at `.claude/agents/[category]/[agent].md`

## Agent Categories

### Country Models (policyengine-us, policyengine-uk, etc.)
These agents support the multi-agent development workflow for implementing tax and benefit rules with proper isolation and verification.

### API (policyengine-api)
Agents focused on Flask API development, performance, security, and proper REST practices.

### App (policyengine-app)
Agents for React application development, focusing on component quality, performance, and user experience.

### Shared
Resources and agents that apply across all PolicyEngine repositories.

## Multi-Agent Workflow (Country Models)
For country model development, we use an isolated multi-agent approach:
1. **Document Collector** gathers authoritative sources
2. **Test Creator** writes tests (without seeing implementation)
3. **Rules Engineer** implements rules (without seeing test expectations)
4. **Rules Reviewer** verifies implementation matches documentation
5. **Supervisor** orchestrates and ensures quality

See `country-models/workflow.md` for detailed workflow documentation.

## Key Principles

1. **Source Authority**: Statutes > Regulations > Websites
2. **Isolation**: Tests and implementation developed separately
3. **Vectorization**: No if-elif-else with household data
4. **Documentation**: Every value traces to primary source
5. **Testing**: Document calculations with regulation references