# Agent Lessons Learned

Accumulated from /encode-policy-v2 and /backdate-program runs across all contributors.
Loaded by implementation agents on future runs.

## New Lessons from Alabama UI Implementation (2026-05-14)

### PARAMETER
- Restrict parameter descriptions to the authorized verb set (limits/provides/sets/excludes/deducts/uses); reject synonyms like "requires" even when grammatically correct.
- Drop explanatory tails from parameter descriptions after the canonical "X provides this Y under the Z program." form; trailing "to determine..." or "based on..." clauses are noise.
- Strip trailing zeros from decimal parameter values (e.g., 44.50 to 44.5) so the YAML matches the canonical numeric form.
- Include the program acronym in parameter labels (e.g., "Alabama UI state unemployment rate" not "Alabama state unemployment rate") so labels are unambiguous when multiple programs share a state.

### VARIABLE
- Remove inline statute-restatement comments when the class-level `reference` already cites the same authority; keep inline comments only for non-obvious idioms (e.g., half-down rounding) or non-obvious parameter timing.
- Replace hard-coded weeks-per-year integers (52) with framework constants like `WEEKS_IN_YEAR`; the same rule applies to other calendar constants.
- Inline single-use intermediates (e.g., `uncapped_mba = ...; return np.round(uncapped_mba)`) into the return expression when the intermediate name adds no clarity over the operations.

### FORMULA
- Do not wrap a partial-benefit calculation that already returns 0 at the unemployed boundary in a redundant `where(earnings < WBA, partial, WBA)` selector; the wrapper silently pays full WBA when earnings meet or exceed WBA.
- Test the partial-benefit boundary explicitly at earnings = WBA and earnings > WBA expecting 0; passing tests on earnings < WBA do not exercise the formula's exit branch.

### REFERENCE
- A procedural Admin Code section (filing mechanics, deadlines, recordkeeping) cannot serve as the citation authority for a substantive amount or rate; cite the substantive statute or rule that establishes the value.
- When an Admin Code rule has not been republished since a later statutory amendment changed the value, follow the statute and cite it; document the staleness so future contributors do not "fix" the model back to the obsolete admin-code figure.
- USDOL Comparison-of-State-UI-Laws "Minimum Wages Needed to Qualify" columns are derived illustrative figures (assumes equal-quarter wage pattern), not statutory floors; do not encode them as parameters.

### TEST
- Reform-helper Python modules that set parameter-driven enum or bracket values for YAML tests belong alongside the YAML tests in the test directory; document the unusual placement in a header comment so future readers do not move them.
- After fixing a formula bug discovered post-implementation, add the missing boundary test in the same commit so the regression is locked in immediately.

### WORKFLOW
- When the reference implementation for a new program lives in a sibling PR not yet merged, read it from the parent repo path rather than expecting it on the current worktree base; coordinate this in the implementation spec.
- Clean `__pycache__` directories between worktrees that share a parent path to avoid `conftest.py` collisions that intermittently block test collection.
- When two reviewers conflict on statute-vs-admin-code authority, resolve via the more recent enactment date and the substantive-vs-procedural distinction; record the rationale in the PR so the next contributor inherits the decision.
- Honor user-driven historical-scope simplifications (e.g., "2020 onward only") by collapsing pre-scope dated entries and trimming reference research to the in-scope window; do not silently encode out-of-scope history.

