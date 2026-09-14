# Simulation isolation repairs (Astra review of country 2.0.1)

Branch `max/spm-runtime-isolation-20260914` off `upstream/main` (2.0.1).
Source: `astra-review-country-201.md`. PR A of two.

## State
- [x] Read review, read `policyengine_us/spm.py`, core `simulations/simulation.py`,
      `taxbenefitsystems/tax_benefit_system.py`, `reforms/reform.py`, `parameters/*`.
- [ ] Reproduce findings 1-5 + county-type + docs on this runtime.
- [ ] Fix.

## Findings to repair
1. P1 shared-policy contamination: later `apply_reform` mutates the shared parameter tree.
2. P1 clone alias routing: `clone.calc` is still bound to the original simulation.
3. P2 private registry vs shared Entity objects: `set_input` on a reform-added variable fails.
4. P2 tracer/cache misattribution on the shared parameter tree.
5. Low: `is_county_fips` stringifies, so integer 36061 passes.
6. Docs: `docs/usage/microsimulation.md` weight double-count + unsupported legacy claim.

## Next
- Measure `system.parameters.clone()` cost: it decides whether copy-on-write can
  detach unconditionally on every reform, or must be triggered only by reforms
  that actually reach the parameter tree (the country applies a structural
  reform to *every* simulation, so unconditional detach would rebuild the tree
  per household request).
