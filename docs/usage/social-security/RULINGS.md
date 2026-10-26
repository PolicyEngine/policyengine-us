# Restricted-survivor modeling ruling

For the contributed S.770 section 2 preset, a worker who died before 2026,
before attaining 62, and without prior disability eligibility receives the 95%
first factor at the death-based computation benchmark. The parameter
`recompute_pre2026_death_before_eligibility` controls **only** the 18% increase
to that benchmark's first bend point. False therefore retains the 95% factor;
true applies both changes. Deaths after 2025 and workers with accepted
authoritative prior-disability eligibility are outside this switch.

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
