# Arkansas 2025 Income Tax — Implementation + Audit Plan

## Context

Branch `hua7450/issue7362` needs 2025 Arkansas income tax values added. Currently, most parameters stop at 2024-01-01 (rates, deductions) or 2021-01-01 (low-income tables, credits, exemptions). No 2025 values exist yet.

**Reference PDF:** [AR1000F/AR1000NR Instructions (2025)](https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf)

---

## Patterns Borrowed from encode-policy

The encode-policy plugin orchestrates 8-phase workflows for new benefit programs. Our task is narrower (updating existing parameters with 2025 values), but we borrow these patterns:

1. **Working references doc** — Create a single `sources/working_references.md` from the PDF that all agents use as their source of truth (avoids each agent re-reading the same PDF pages)
2. **Plugin agents where they fit** — Use `complete:country-models:implementation-validator` (Phase 1 cleanup), `complete:country-models:reference-validator` (Phase 2 audit), and `complete:country-models:ci-fixer` (test fixing)
3. **Regulatory checkpoints** — Gate between phases to verify correctness before proceeding
4. **Selective skill loading** — Each agent loads only the skills relevant to its role

**Why NOT use plugin agents for everything:** The `complete:country-models:parameter-architect` and `complete:country-models:rules-engineer` agents are designed for creating new program implementations from scratch. Our task is simpler — adding 2025-01-01 date entries to existing YAML files. General-purpose agents with focused instructions are better suited here.

---

## Pre-Work (Main Claude, before any agents)

1. Download PDF:
   ```bash
   curl -L -o /tmp/ar-2025-booklet.pdf "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf"
   ```
2. Extract text + render pages:
   ```bash
   pdftotext /tmp/ar-2025-booklet.pdf /tmp/ar-2025-booklet.txt
   pdftoppm -png -r 300 /tmp/ar-2025-booklet.pdf /tmp/ar-2025-page
   ```
3. Read extracted text → identify sections, page boundaries, page offset (cover/TOC vs instruction pages)
4. Identify "What's New for 2025" section
5. **Create working references doc** — Write a structured `sources/working_references.md` summarizing all 2025 values found in the PDF, organized by topic (rates, deductions, credits, exemptions, low-income tables). Include PDF page numbers. This becomes the single source of truth for all agents.

---

## Skills Strategy

**Selective loading per agent role:**

| Agent Role | Skills to Load | Why |
|------------|---------------|-----|
| Implementation (parameters) | `/policyengine-parameter-patterns`, `/policyengine-period-patterns` | Correct YAML structure, date formatting |
| Implementation (tests) | `/policyengine-testing-patterns`, `/policyengine-period-patterns` | Correct test YAML structure |
| Validation (`implementation-validator`) | None (has its own built-in patterns) | Plugin agent loads its own skills |
| Audit agents | **None** | Read-only comparison — no writing |

**How:** Each implementation agent's prompt will instruct it to call the `Skill` tool for its relevant skills before starting work.

---

## Phase 1: Implementation (Agent Team — 4 parallel agents)

All 4 agents run in parallel. Each receives:
- The working references doc (`sources/working_references.md`)
- Their assigned PDF page screenshots (300 DPI PNGs)
- Their assigned existing parameter YAML files
- Instruction to load relevant skills first

### Agent Split

| Agent Name | Type | Topic | Files to Update |
|------------|------|-------|----------------|
| **impl-rates** | `general-purpose` | Tax Rates, Brackets & Standard Deductions | `rates/main/rate.yaml`, `rates/main/reduction.yaml`, `deductions/standard.yaml` |
| **impl-tables** | `general-purpose` | Low Income Tax Tables | All 7 files under `rates/low_income_tax_tables/` |
| **impl-credits** | `general-purpose` | All Credits | Files under `credits/` (personal, inflationary relief, additional tax credit, CDCC, non_refundable.yaml, refundable.yaml) |
| **impl-exemptions** | `general-purpose` | Exemptions & Gross Income | Files under `exemptions/`, `gross_income/` |

### What Each Agent Does
1. Call `Skill` to load `/policyengine-parameter-patterns` and `/policyengine-period-patterns`
2. Read the working references doc for their section's 2025 values
3. Read PDF page screenshots to verify values visually
4. Read existing parameter YAML files
5. Add `2025-01-01` entries with correct values (following existing YAML structure)
6. Add reference metadata with PDF page numbers (`#page=XX`)
7. If a parameter's 2025 value is **unchanged** from the prior year, **do not add a new entry** (the prior value carries forward automatically)
8. **New/unmodeled programs — NOTE ONLY, do NOT build:**
   - **New for 2025:** If the PDF introduces a program/credit/deduction that didn't exist before 2025 → log it with: name, what it does, PDF page, and "NEW FOR 2025"
   - **Pre-existing but unmodeled:** If the PDF describes a program that existed before 2025 but isn't in the repo → log it with: name, what it does, PDF page, and "NOT IMPLEMENTED"
   - Agents collect these into a "Gaps" section at the end of their report. No new files, no new variables, no new parameters — just documentation.
   - User will decide which (if any) to implement after reviewing the gap list.

### External Form Escalation (applies to ALL phases)

Arkansas has many supplementary forms beyond the main AR1000F instructions. Known forms from [dfa.arkansas.gov](https://www.dfa.arkansas.gov/office/taxes/income-tax-administration/individual-income-tax/forms/):

| Form | Topic | Likely Needed By |
|------|-------|-----------------|
| AR3 | Itemized Deduction | impl-credits, impl-exemptions |
| AR4 | Interest and Dividend | impl-exemptions |
| AR1000ADJ | Adjustments Schedule | impl-exemptions |
| AR1000D | Capital Gains | impl-exemptions |
| AR1000DC | Disabled Individuals Certificate | impl-credits |
| AR1000DD | Developmental Disabilities Certificate | impl-credits |
| AR1000CE | Teachers Qualified Classroom Investment Expense | impl-credits |
| AR1000TC | Tax Credits | impl-credits |
| Low Income Tax Tables | Rate tables by filing status | impl-tables |

**Escalation workflow:**

1. **Agent flags need:** When an agent discovers it needs values from a form it doesn't have, it reports:
   ```
   EXTERNAL FORM NEEDED: "[Form Name]"
   - What I need: [specific value/table/rule]
   - Which parameter: [file path]
   - Why: [what the main instructions reference]
   ```
   The agent **continues working** on everything else it can — it does NOT block.

2. **Main Claude downloads the form:**
   ```bash
   curl -L -o /tmp/ar-2025-{form}.pdf "https://www.dfa.arkansas.gov/wp-content/uploads/{form_filename}"
   pdftotext /tmp/ar-2025-{form}.pdf /tmp/ar-2025-{form}.txt
   pdftoppm -png -r 300 /tmp/ar-2025-{form}.pdf /tmp/ar-2025-{form}-page
   ```

3. **Main Claude spawns a form-reader agent** (`general-purpose`) with:
   - The rendered form pages
   - The specific question from the original agent
   - Instructions to extract the needed values and report back

4. **Main Claude relays the answer** back to the original agent (or applies the value directly if the original agent already finished).

This is the same pattern as "EXTERNAL PDF NEEDED" from the audit plan template, but extended to the implementation phase.

### Regulatory Checkpoint 1
After all 4 agents complete (including any external form follow-ups), main Claude:
- Reads updated files
- Spot-checks a few values against PDF screenshots
- Resolves any pending external form requests
- Proceeds to Phase 1b only if satisfied

---

## Phase 1b: Tests (Sequential, after Phase 1)

| Agent Name | Type | Topic |
|------------|------|-------|
| **impl-tests** | `general-purpose` | Add 2025-period test cases |

### What This Agent Does
1. Call `Skill` to load `/policyengine-testing-patterns` and `/policyengine-period-patterns`
2. Read the working references doc
3. Read existing test YAML files under `tests/policy/baseline/gov/states/ar/tax/income/`
4. Add 2025-period test cases to existing test YAMLs (use PDF worksheet examples as test inputs)
5. If new parameters were added in Phase 1, create corresponding test files

---

## Phase 1c: Validation & Test Fixing (Sequential)

| Step | Agent | Type | What It Does |
|------|-------|------|-------------|
| 1 | **validator** | `complete:country-models:implementation-validator` | Checks naming conventions, folder structure, parameter formatting, code style across all modified files |
| 2 | **ci-fixer** | `complete:country-models:ci-fixer` | Runs `policyengine-core test` locally, fixes any test failures, iterates until all pass |

### Regulatory Checkpoint 2
After tests pass, main Claude:
- Reviews any fixes the ci-fixer made
- Ensures fixes didn't introduce hard-coded values or incorrect logic
- Runs `make format`

---

## Phase 2: Audit (Agent Team — 3 parallel agents, REPORT ONLY)

Follows the [state-tax-audit-plan.md](../memory/state-tax-audit-plan.md) template. **No file edits.**

### Agent Split

| Agent Name | Type | Topic | What to Verify |
|------------|------|-------|---------------|
| **audit-rates-deductions** | `general-purpose` | Rates, Brackets, Deductions, Low Income Tables | All rate/reduction/deduction/table 2025 values match PDF exactly |
| **audit-credits** | `general-purpose` | All Credits | Personal, inflationary relief, additional tax credit, CDCC values and logic match PDF |
| **audit-exemptions-gaps** | `general-purpose` | Exemptions, Gross Income & Gap Analysis | Exemption values correct; scan full PDF for anything NOT modeled in repo |

Plus one plugin agent:
| **ref-validator** | `complete:country-models:reference-validator` | Reference Page Numbers | Every `#page=XX` reference points to the correct PDF page |

### Each Audit Agent Receives
- PDF page screenshots (their assigned pages)
- The UPDATED parameter/variable files from Phase 1
- Standard audit report format: MATCHES / MISMATCHES / MISSING FROM REPO / MISSING FROM PDF

### Mismatch Verification
Any reported mismatch → re-render at 600 DPI → cross-reference with pdftotext → accept or reject

---

## Phase 3: Report & Finalize

1. Consolidate all audit findings into a summary:
   - Parameter value issues (mismatches with PDF citations)
   - Reference page corrections
   - Confirmed correct values
   - **Gap list (two categories):**
     - "NEW FOR 2025" — programs/credits/deductions introduced in 2025 that aren't in the repo
     - "NOT IMPLEMENTED" — pre-existing programs found in the PDF that we don't model
   - Each gap entry includes: name, description, PDF page reference
2. Fix any confirmed mismatches in existing parameters
3. `make format`
4. Update `changelog_entry.yaml`
5. **Present gap list to user** — user decides which (if any) to implement as follow-up work

---

## Key Files

### Parameters (to be updated)
- `policyengine_us/parameters/gov/states/ar/tax/income/rates/main/rate.yaml`
- `policyengine_us/parameters/gov/states/ar/tax/income/rates/main/reduction.yaml`
- `policyengine_us/parameters/gov/states/ar/tax/income/deductions/standard.yaml`
- `policyengine_us/parameters/gov/states/ar/tax/income/rates/low_income_tax_tables/` (7 files)
- `policyengine_us/parameters/gov/states/ar/tax/income/credits/` (~10 files)
- `policyengine_us/parameters/gov/states/ar/tax/income/exemptions/` (2+ files)
- `policyengine_us/parameters/gov/states/ar/tax/income/gross_income/` (5 files)

### Variables (may need updates if 2025 logic changed)
- `policyengine_us/variables/gov/states/ar/tax/income/` (45 files)

### Tests (to be updated/created)
- `policyengine_us/tests/policy/baseline/gov/states/ar/tax/income/` (11 existing files)

---

## Execution Summary

```
Pre-Work:  Download main PDF → extract text → render 300 DPI → create working_references.md
           ↓
Phase 1:   4 parallel impl agents (rates, tables, credits, exemptions)
           ↓  External form escalation (if agents flag EXTERNAL FORM NEEDED):
           │     Main Claude downloads form → spawns form-reader agent → relays answer
           ↓  Checkpoint 1
Phase 1b:  1 test agent (adds 2025 test cases)
           ↓
Phase 1c:  implementation-validator → ci-fixer → make format
           ↓  Checkpoint 2
Phase 2:   3 parallel audit agents + reference-validator (report only)
           │  (audit agents can also flag EXTERNAL FORM NEEDED → same escalation)
           ↓  Mismatch verification at 600 DPI
Phase 3:   Consolidated report → fix confirmed issues → gap list → changelog → done
```
