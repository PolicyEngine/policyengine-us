# Supplied-record Social Security calculator

This opt-in route will calculate gross monthly retirement benefits from a supplied
unreformed eligibility-year AIME or PIA, and the restricted single-survivor case
from a supplied monthly benefit and composite ratio. Existing public benefit
inputs retain their current behavior.

Implementation plan:

1. Share one monthly PIA service across household and future history callers,
   with eligibility-year bend points, explicit applicability, baseline inversion,
   contributed formula paths and the S.770 section 2 preset.
2. Build an entitlement ledger with cohort claiming adjustments, statutory COLA
   and payment rounding, insured-status assertions and the annual earnings test.
3. Require an identified worker record and ordinary, non-WINDEX survivor basis;
   derive the death benchmark and propagate supplied-payment rounding intervals.
4. Expose separate calculated results until the benefit source-selector change
   merges. Wire those results into its AIME/PIA/survivor modes in one later step.
5. Validate published SSA examples, boundary cases, property invariants and
   equality of existing outputs with the calculator disabled.

The supported computation benchmark begins in 1983. History-derived AIME,
family benefits, disability computations and minimum PIAs are separate work.
