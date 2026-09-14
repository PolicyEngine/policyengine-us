# Simulation isolation repairs (Astra review of country 2.0.1)

Branch `max/spm-runtime-isolation-20260914` off `upstream/main` (2.0.1).
Source: `astra-review-country-201.md`. PR A of two.

## State
- [x] Read review; read `policyengine_us/spm.py`, core `simulations/simulation.py`,
      `taxbenefitsystems/tax_benefit_system.py`, `reforms/reform.py`, `parameters/*`.
- [x] Measured `system.parameters.clone()`: **1.5-2.0 s** against a 0.03 s warm
      household build and a 0.16 s warm calculate. Detaching on every simulation
      (the structural reform is re-applied to *every* one) was therefore not an
      option; copy-on-write had to be genuinely lazy.
- [x] Reproduced findings 1-5 on this runtime and turned each into a regression
      test. Every new test fails on the parent commit `e24e655a04`.
- [x] Fix findings 1-4 in `policyengine_us/spm.py`.
- [x] Fix finding 5 (county input type) and the two documentation defects.
- [ ] Full core/unit + microsimulation + representative YAML runs, then draft PR.

## Design decisions
1. **Copy-on-write parameter tree.** `share_spm_policy` returns an instance of a
   per-base `SharedParameter<Base>` subclass whose `parameters` is a property.
   `SPMSimulationMixin.apply_reform` and the shared system's own
   `apply_reform_set` arm a read barrier for the duration of the reform; the
   first read inside that window clones the tree through core and gives this
   system a cold private at-instant cache, leaving the lender's tree and warm
   caches untouched. `modify_parameters`, `load_extension` and
   `add_abolition_parameters` - the three core methods that edit the live tree
   in place - detach outright. A variable-only reform never reads `parameters`,
   so the structural reform re-applied at each simulation's start instant still
   pays nothing. Measured: household build stays 0.05 s; a parameter reform pays
   1.24 s once. Branches created with `clone_system=False` are moved onto the
   detached tree, because they share their parent's policy deliberately.
2. **Clone alias routing.** Core keeps `self.calc = self.calculate` and
   `self.df = self.calculate_dataframe` as bound methods in the instance dict and
   copies them verbatim when cloning. `clone()` now rebinds every copied bound
   method by method name, so an alias core adds later is repaired too.
3. **Private entities.** `share_spm_policy` shallow-copies the entities and binds
   them to the private system, keeping one object per key across `entities`,
   `person_entity` and `group_entities` (`clone_spm_system` now does the same).
   An entity resolves variable names through the system it is bound to, so this
   is what makes `set_input` find a reform-added variable.
4. **Traced parameter receipts.** Only the *root* node carries core's
   request-specific `trace`/`tracer`/`branch_name` and caches the resulting
   `TracingParameterNodeAtInstant`; children are wrapped on the fly. So a traced
   simulation gets a shallow private root with its own at-instant cache
   (microseconds, not a 1.5 s tree clone), primed as traced - core marks the tree
   in `_run_formula`, but `_calculate` reads `gov.abolitions` first, so on
   core 3.30.2 nothing was ever recorded. Two traced simulations now each record
   their own four `spm_unit_fpg` parameter accesses, and the shared tree is left
   untraced.
5. **County input type.** Tightening `is_county_fips` alone would have been
   inert: `value_type = str` maps to the numpy `object` dtype, so the model
   stores an integer column as integers, and both readers stringify before
   asking the provider. The provider now records which counties arrived as
   something other than text - at the one point that still sees the type - and
   rejects them when a county measurement needs them, before its own memo. A
   caller who never asks for a county is still never asked for one.

## Hardening carried from the blast-radius audit
- A shared-policy system clones through an ordinary copy: core's clone writes
  the cloned tree into the instance dictionary, where the property would shadow
  it and hand back a "clone" still sharing the lender's tree.
- The shared-policy class is published under its own name, so systems built on
  it still pickle.
- `tools/pinned_tbs.py` keys its cache on the parameter tree as well as the
  system, because a shared system keeps its identity while detaching a tree.

## Notes
- Installed core here is **3.30.2**, not the 3.32.5 Astra reviewed. `calc`/`df`
  sit at `simulation.py:223-224` and the clone copy loop at 1381-1416, matching
  Astra's citations.
- Astra's finding 1 sub-case "an existing unrelated simulation changes after
  cache invalidation" needs a real invalidation: `delete_arrays("income_tax")`
  alone leaves the cached standard deduction, so the contaminated tree is not
  reached. The regression test uses `_invalidate_all_caches()`, the same purge
  `apply_reform` performs.
- Astra's finding 4 count ("four accesses, then zero") does not reproduce
  literally on core 3.30.2, where a traced simulation recorded *no* parameter
  accesses at all: `_calculate` reads `gov.abolitions` and caches a non-tracing
  at-instant node before `_run_formula` marks the tree. Priming the private root
  as traced repairs that as well, and the test asserts the four accesses per
  simulation that Astra described.
