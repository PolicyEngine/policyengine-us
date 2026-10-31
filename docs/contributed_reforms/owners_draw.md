# Owners' draw SECA reform

This contributed reform brings eligible pass-through profits into the SECA
OASDI base. It is off by default. The example configuration phases in a share
of 0.1 in 2027, rising by 0.1 annually to 1 in 2036. These are custom example
settings, not enacted law or a complete implementation of an OACT provision.
Population scoring uses the tax side only.

## Parameters

All settings are under `gov.contrib.ssa.owners_draw`.

| Parameter | Default | Meaning |
| --- | --- | --- |
| `in_effect` | `false` | Enable the reform. |
| `start_year` | `2027` | First affected calendar year. |
| `phase_in_years` | `10` | Positive duration of the linear phase-in. |
| `phase_in_share` | `-1` | Derive the linear share; an annual value in [0, 1] overrides it. |
| `net_earnings_factor` | `0` | Derive the standard SECA factor; a value in (0, 1] overrides it. |
| `material_participation_only` | `true` | Use nonpassive income as the participation proxy. |
| `include_hi` | `false` | Also tax adjusted draw earnings at the uncapped SECA HI rate. |
| `benefit_credit` | `true` | Add adjusted annual draw earnings to the existing AIME earnings history before its annual cap. |
| `half_seca_deduction` | `true` | Apply the existing section 164(f) deductible share to added SECA. |
| `room_cap_basis` | `0` | Preserve the current-law OASDI cap; `1` removes the draw ceiling. |

The derived share is `min(max((year - start_year + 1) / phase_in_years, 0), 1)`.
Activation and start-year checks still apply to explicit share overrides.
The current-law cap is copied before user reforms, so removing the general
payroll cap does not silently remove this draw ceiling.

## Input contract and signed losses

For each Person, define total signed entity income
`T = s_corp_income + partnership_income`, passive subset
`Q = passive_partnership_s_corp_income`, and already-SE partnership subset
`K = partnership_self_employment_net_earnings`. Both Q and K are already in T;
K is a gross source amount before SECA's net-earnings adjustment.

With disjoint passive and already-SE subsets, the signed active residual is
`G = T - Q - K`. If both subsets are nonzero, either supply
`owners_draw_subsets_are_disjoint: true` or the signed intersection in
`owners_draw_passive_se_overlap`. The latter yields
`K_active = K - overlap` and `G = T - Q - K_active`. Ambiguous classifications
raise an error. If either subset is zero, disjointness follows without an
additional assertion. With `material_participation_only: false`, include the
passive subset and subtract the entire already-SE K instead.

Signed profits and losses net within the owner's supplied entity totals
before flooring the residual. This is an approximation without entity-level
detail. A negative residual does not offset wages or existing SE earnings.
[26 U.S.C. 1402(a)](https://www.law.cornell.edu/uscode/text/26/1402#a)
provides the comparable income-minus-deductions approach for net SE earnings;
its existing exclusions are not a legal basis for this contributed expansion.
Nonpassive status is a material-participation proxy and does not identify
every legal limited-partner class.

## Gross draw, adjusted earnings, and cap priority

The planned gross draw is `D_planned = share * max(G, 0)`. The default
netting factor is the existing model expression:

```text
q = 1 - gov.irs.ald.misc.employer_share
        * (gov.irs.self_employment.rate.social_security
           + gov.irs.self_employment.rate.medicare)
```

Current rates produce 0.9235. Rate reforms flow through q, including when HI
on the incremental draw is off. An explicit factor override is available.
The planned adjusted draw `q * D_planned` must independently meet the existing
`gov.irs.self_employment.net_earnings_exemption` ($400 at current settings).
Otherwise actual gross draw D and adjusted earnings N_D are both zero.
This independent floor preserves existing SE computations; it is a specific
modeling choice rather than an integrated new SECA statute.

Let W be existing taxable wages, S the already adjusted and capped existing
`social_security_taxable_self_employment_income`, and C the preserved cap.
For the default cap basis:

```text
room = max(C - W - S, 0)
draw_oasdi_base = min(N_D, room)
added_OASDI = draw_oasdi_base * SECA_OASDI_rate
```

Wages have priority, then existing SE earnings, then the draw. The independent
draw outputs leave the existing SE base intact. Added tax enters the existing
SECA liability variables, so payroll and OASDI accounting include it once.
HI inclusion adds `N_D * SECA_HI_rate` without the OASDI ceiling. The deduction
uses `gov.irs.ald.self_employment_tax.percent_deductible`, distinct from the
employer-share parameter used to derive q, and retains nondependent aggregation.
No second copy of the source income is added to gross income or AGI.

Outputs include `owners_draw_active_income`, `owners_draw_planned_gross`,
`owners_draw_gross`, `owners_draw_net_earnings_factor`,
`owners_draw_net_earnings`, `owners_draw_oasdi_room`,
`owners_draw_oasdi_base`, `owners_draw_oasdi_tax`, and `owners_draw_hi_tax`.

For the current-law cap basis, the taxed draw is nonnegative and no larger
than remaining room, adjusted earnings, or actual gross draw. Adding the
draw cannot push otherwise capped covered earnings beyond C. Increasing the
phase-in share cannot reduce draw tax when other inputs and settings stay
fixed. Already-SE income is removed before computing the draw, and disabled
years retain baseline tax and deduction behavior. The `1` cap option
intentionally permits earnings above C.

## Benefit credit and active NIIT interaction

`owners_draw_credited_earnings` exposes N_D when benefit credit is enabled,
and zero otherwise. The flag has no tax effect. The reform passes these
annual earnings to the existing `ss_aime` earnings-history helper and adds
them before applying each year's wage-base cap. A supplied positive
`ss_aime_input` retains its baseline precedence. This reform does not append
an amount to final AIME or alter reported benefits. This bridge inherits
main's AIME lookback, age rules and separate
`gov.ssa.social_security.wage_base` path. The processed current-law wage-indexed
paths now extend through 2100; tax-cap and benefit-cap reforms remain separate
policy choices. The opt-in [annual-history calculator](social_security_history.md)
uses the same per-year owners' draw kernel, retains earnings through the year
before claiming, and carries the adjusted draw into both conventional AIME
and annual mini-PIAs. Its ledger also coordinates separate above-cap credit.

`owners_draw_niit_exclusion` is the matching gross-profit exclusion for a
S.770 active-business NIIT option. With OASDI only it is
`draw_oasdi_base / q`: only profits whose adjusted earnings actually face
SECA are excluded. With HI enabled it is the entire actual gross draw D,
because N_D faces uncapped HI. Profits beyond OASDI room remain in the active
base when HI is off. The undrawn share and any floor-rejected planned draw
also remain. Existing already-SE gross K_active must separately be excluded
regardless of the OASDI cap because existing SE earnings face uncapped HI.
When both reforms are active, `s770_active_business_income` consumes this
calculated exclusion, including an explicit net-factor override. When owners
draw is disabled, before its start year, or uninstalled, the S.770 manual
draw hooks retain their original behavior.

The automatic joint route requires `material_participation_only: true`.
Passive-inclusive draws remain supported by the standalone owners' draw
reform, but the joint active-business calculation raises an explicit error
for that setting: the aggregate draw does not identify which taxed profits
belong in the active residual or in NII. Supporting that combination requires
a validated source allocation, including NII's separate
`s770_nii_fica_seca_income` hook. Subtracting the entire passive-inclusive draw
from active profits would misallocate the remaining bases between tax rates.

## Data limitations

The intended field contract is separate S-corporation and partnership totals,
with the combined section 469 passive subset subtracted once and the
already-SE partnership subset removed without double counting.

Current production exports force `s_corp_income` to zero and put combined
nonpassive S-corporation and partnership donor income into `partnership_income`.
Calibration carries passive income mass into that combined column, while
`passive_partnership_s_corp_income` is absent and defaults to zero.
`partnership_self_employment_net_earnings` is present. An absent passive
column does not establish that passive income is zero. This can overstate the
active residual and makes population results provisional.

[Microcosm #1251](https://github.com/PolicyEngine/microcosm/pull/1251) repairs
the total/passive contract, and
[#1261](https://github.com/PolicyEngine/microcosm/pull/1261) separates entity
totals. Nonprovisional population scoring requires a pinned artifact containing
these repairs and a receipt validating the stored columns and their meanings.
No population impact is measured by this PR; the hub will measure it.

## Comparable OACT provisions

OACT's current [coverage provision F12](https://www.ssa.gov/OACT/solvency/provisions/coverage.html)
says, “make all distributions to all pass-through business owners up to the
earnings cap subject to the SECA tax”. Its current table starts in 2029 and
requires material participation. This reform's example 2027–2036 phase-in
and default OASDI-only treatment are distinct choices.

OACT's current [payroll-tax provisions](https://www.ssa.gov/OACT/solvency/provisions/payrolltax.html)
separate rate increases, taxation above the taxable maximum, and partial
taxation above it. The older E5 label belongs to the
[legacy contribution-and-benefit-base table](https://www.ssa.gov/OACT/solvency/provisions/wagebase.html),
which uses the 2008 Trustees assumptions. E5 says, “Raise the taxable maximum
amount (the contribution and benefit base) to include 90 percent of total
OASDI covered earnings.” Its phased higher cap also earns benefit credit.
It is not a current 2026 E5 category. Cap changes and benefit-credit choices
are distinct from expanding the owners' draw base.
