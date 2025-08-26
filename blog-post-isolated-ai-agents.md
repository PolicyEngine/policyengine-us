# How PolicyEngine Uses Isolated AI Agents to Build Trustworthy Rules-as-Code

*December 2024*

Government benefit calculations affect millions of lives. A miscalculated food assistance benefit isn't just a bug—it's a family's grocery budget. An incorrect tax credit isn't just an error—it's someone's ability to pay rent. That's why at PolicyEngine, we've developed a revolutionary approach to ensure AI-generated code accurately implements government regulations: isolated multi-agent development.

## The Problem: AI Takes Shortcuts

When you ask an AI to implement a government program, it faces a fundamental challenge. Given a test that expects a benefit of $500, the AI might:

- Hardcode `return 500` to pass the test
- Guess at parameter values instead of checking regulations
- Implement a simplified version that works for test cases but fails in production
- Hallucinate thresholds and rates that sound plausible but don't match the law

Traditional development—even with AI assistance—can't prevent these issues because the AI can see both the tests and the implementation. It's like a student who has access to both the exam questions and the answer key: they might get the right answers without actually learning the material.

## Our Solution: Enforced Isolation

We've developed a multi-agent system where specialized AI agents work in complete isolation from each other. Here's how it works:

### The Cast of Agents

**1. Document Collector**  
This agent's sole job is gathering authoritative sources: statutes, regulations, program manuals. It finds the actual text of laws like 42 USC § 1381 or 7 CFR 273.9, not summaries or websites. These documents become the single source of truth.

**2. Test Creator**  
Working only from the documents, this agent creates comprehensive tests. It never sees any implementation code. It calculates expected values by hand from the regulations, showing its work:
```yaml
# Per 7 CFR 273.9(d)(6)(ii):
# Shelter costs: $1,200
# Minus half of income after deductions: $500
# Excess shelter: $700
# Capped at: $597
expected_shelter_deduction: 597
```

**3. Rules Engineer**  
Also working only from documents, this agent implements the actual code. It never sees the integration tests. Every parameter links to a specific regulation. Every calculation step traces to legal text. No guessing, no shortcuts.

**4. Reviewer**  
Only after the isolated agents complete their work does the Reviewer see everything. It validates that both tests and implementation correctly interpret the regulations. When issues are found, they're routed back through the Supervisor without breaking isolation.

### The Key: Information Barriers

The Supervisor orchestrates everything while maintaining strict information barriers:

- ❌ Test Creator never sees implementation code
- ❌ Rules Engineer never sees test expected values
- ✅ Both work from the same authoritative documents
- ✅ Supervisor can see everything but carefully controls information flow

This isolation is enforced through separate git branches and working directories. It's not just a suggestion—it's architecturally impossible for the agents to see each other's work.

## Why This Works

### 1. No Teaching to the Test

When the Rules Engineer doesn't know what values the tests expect, it must implement the actual regulation. There's no shortcut available. It must read that the standard deduction is $198 per month from the official table, not guess it from a test.

### 2. Independent Verification

The Test Creator provides an independent implementation of the regulations. When both agents working from the same documents arrive at the same answer, we have high confidence it's correct. When they disagree, we've caught an error.

### 3. Comprehensive Coverage

The Test Creator, unburdened by implementation complexity, creates tests for every scenario mentioned in regulations. The Rules Engineer, unaware of which cases are tested, must handle all documented situations. Neither can skip edge cases.

### 4. Traceable Implementation

Every line of code traces to a regulation. Every test expectation cites its source. When auditors ask "why does the system calculate $597?"—we can point to the exact paragraph in the Code of Federal Regulations.

## Real Results: Multiple Rounds to Perfection

This system rarely produces perfect code on the first try—and that's a feature, not a bug. Here's a typical development cycle:

**Round 1**: 15 issues found
- Parameter values don't match source documents
- Missing edge cases for elderly households  
- Calculation order incorrect for deductions

**Round 2**: 3 issues found
- Monthly vs. annual confusion in one calculation
- Missing cap on shelter deduction
- Test calculation error for mixed households

**Round 3**: 1 issue found
- Rounding difference in percentage calculation

**Round 4**: ✅ All tests pass, all citations verified

Each round makes the implementation more robust. The isolation ensures fixes address root causes, not symptoms.

## Beyond Accuracy: Building Trust

This approach does more than produce correct code—it builds trust in AI systems:

### For Government Agencies
"We can trace every calculation to statute. No black boxes, no unexplained values."

### For Engineers  
"The AI can't take shortcuts. It must implement the actual specification."

### For Auditors
"Complete documentation trail from law to code. Every decision is justified."

### For Citizens
"The system calculating my benefits follows the actual law, not approximations."

## The Bigger Picture: AI Safety Through Architecture

Our isolated agent system demonstrates a crucial principle for AI safety: architectural constraints are more reliable than training or prompting. We don't ask the AI to avoid shortcuts—we make shortcuts impossible.

This has implications beyond government benefits:

- **Medical Diagnosis**: Separate agents for symptoms, tests, and treatment ensure comprehensive evaluation
- **Legal Analysis**: Isolated research and argumentation prevent cherry-picking precedents
- **Financial Modeling**: Independent validation of assumptions and calculations
- **Safety-Critical Systems**: Multiple isolated verifications before deployment

## Open Source and Available Now

Our multi-agent system is open source and available in the PolicyEngine-US repository. The agents are configured and ready to use for any government program implementation. We're not just talking about safe AI development—we're practicing it every day.

## What's Next

This Thursday, we're hosting a live webinar where we'll implement a state LIHEAP program from scratch using this system. We'll pick a state we've never modeled, gather its regulations, and build the implementation live—showing every step of the isolated development process.

It's one thing to read about the theory. It's another to watch AI agents build accurate, traceable, regulation-compliant code in real-time, without shortcuts or hallucinations.

## Conclusion: The Future of Rules-as-Code

As governments increasingly turn to AI for digitizing regulations, the stakes couldn't be higher. Benefits, taxes, and regulatory compliance affect everyone. We can't afford AI that hallucinates parameters or takes shortcuts to pass tests.

Our isolated agent approach proves that AI can be both powerful and trustworthy. By enforcing separation between test creation and implementation, we ensure AI systems that don't just work—they work correctly, traceably, and in full compliance with the law.

The technology exists today. The methodology is proven. The only question is: how quickly can we deploy these safer AI systems to serve citizens better?

---

*PolicyEngine is building the future of computational public policy. Our open-source platform models tax and benefit systems with unprecedented accuracy and transparency. Learn more at [policyengine.org](https://policyengine.org).*

*Join our webinar "PolicyEngine's Isolated AI Agents: Safe Rules-as-Code Development" this Thursday at 2 PM ET to see this system in action.*