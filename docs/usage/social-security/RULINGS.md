# Restricted-survivor modeling ruling

For the contributed S.770 section 2 preset, a worker who died before 2026,
before attaining 62, and without prior disability eligibility receives the 95%
first factor at the death-based computation benchmark. The parameter
`recompute_pre2026_death_before_eligibility` controls **only** the 18% increase
to that benchmark's first bend point. False therefore retains the 95% factor;
true applies both changes. Deaths after 2025 and workers with accepted
authoritative prior-disability eligibility are outside this switch.

Every survivor record requires an explicit prior-eligibility answer:
`ss_calculator_prior_disability_eligibility=1` asserts that the worker initially
became eligible through disability before death; 0 asserts no prior eligibility.
The default -1 is unspecified and raises `ValueError`; other values also fail.
The pure `SurvivorBasis.prior_disability_eligibility` field accepts the same
answers as `True`/`False`, with `None` unspecified. Prior eligibility requires
an authoritative computation basis; no prior eligibility permits a benchmark
derived from death and age-62 attainment. An authoritative year alone never
establishes prior eligibility.

Section 2(c)(2)(B) covers workers who “initially became eligible for old-age or
disability insurance benefits before January 1, 2026”. Prior disability is
initial eligibility, so the 18% increase applies at that earlier benchmark
regardless of this switch.

For deaths without prior initial eligibility, this is an explicit scenario
interpretation, not a statutory conclusion. The switch defaults false and
must be recorded with the scenario. For AIME above the increased first bend
point, the raw monthly gain is .05 * original BP1 with the switch false, or
.1634 * original BP1 with it true.

Source: [119th Congress S.770, section 2(a) and (c)](https://www.congress.gov/bill/119th-congress/senate-bill/770/text).
