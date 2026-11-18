# S.770 section 8 split tax options

These independently enabled options model an NII rate add-on and an additional
active pass-through base. Both default off. Parameters are under
`gov.contrib.congress.s770.section_8`; each part has its own `in_effect`,
`start_year`, rate and custom OASDI share. The example rates are the proposed
bill's 12.4 percentage-point add-on and 16.2 percent active rate. No package
settings are encoded.

## Sources and dates

[S.770, 119th Congress, introduced text, sections 8–9](https://www.congress.gov/bill/119th-congress/senate-bill/770/text)
was retrieved October 23, 2026. Section 8(a)(1) replaces 3.8 percent with 16.2
percent. Section 8(b) broadens the investment-income definition, denies the
section 172 NOL deduction, and excludes income actually taxed under SECA or
FICA. Section 8(c) applies to “taxable years beginning after the date of enactment
of this Act”. There is no statutory fixed start year. The configurable 2026
defaults illustrate assumed enactment timing and have no effect while disabled.

Section 9(a) assigns 62 percent of all section 1411 tax to a merged Social
Security fund. Revenue appropriation starts with the first fiscal year beginning
after enactment; assets transfer on January 1 of the first calendar year beginning
after enactment.
`transfer.start_year` is a separate annual modeling choice. This liability model
does not estimate fiscal-year collection lags or prorate receipts.

## Signed base and tax accounting

Use the existing `niit_magi`, including its modeled estate and section 911
adjustments, and existing filing-status thresholds. Let `X=max(MAGI−threshold,0)`,
`N` be signed adjusted old-definition NII, and `A` the signed additional active
base (zero if that option is off):

```
L = min(max(N + A, 0), X)
n = min(max(N, 0), L)
a = L - n
tax = (existing_rate + enabled_addon_rate) * n + enabled_active_rate * a
```

Losses net before clipping. Both allocated shares are nonnegative; NII consumes
the limit first even when its add-on rate is zero. When active inclusion is on,
the existing 3.8 percent NIIT also uses `n`. The reform replaces
`net_investment_income_tax` with the entire resulting liability. The two named
component taxes are already included there and in federal income tax; adding
them again would double count.

With both options enabled, identical sources, exclusions, NOL treatment, MAGI,
thresholds and timing, and `existing_rate + addon_rate = active_rate = .162`,
this equals `.162 * L`
for all signed inputs. This is a conditional liability identity, not a claim
that the available fields implement every statutory category. For `N=−10,000`,
`A=20,000`, `X=50,000`, the tax is $1,620. For `N=20,000`, `A=−10,000`, the
tax is also $1,620. Active losses can therefore reduce liability relative to
the add-on alone ($3,240 in the latter example). Activation is monotone with
nonnegative active income, nonnegative rates and fixed signed NII/source rules,
including exclusions and NOL treatment. Changing source exclusions can lower
liability even when the active residual is nonnegative: removing $10,000 of
already-SE passive income from NII with no active residual reduces existing NIIT
from $380 to zero. Arbitrary signed active losses also defeat monotonicity.

## Pass-through classification and SECA/FICA interaction

The person-level total is `partnership_s_corp_income`, whose formula sums
`s_corp_income + partnership_income`. Subtract the passive subset and gross
already-SE active subset, then net signed results across head/spouse members.
Dependents' income belongs to their own return. This assumes the passive and
already-SE subsets are disjoint unless their validated intersection is supplied
in `s770_passive_se_income`. An intersection is removed from NII too. Signed
subsets are not independently floored. Cross-entity netting within the available
person totals is an approximation. Nonpassive status is only a proxy for material
participation, not a determination of each limited partner's legal status.

The already-SE exclusion uses `partnership_self_employment_net_earnings`, not a
capped OASDI base: existing SE earnings can still pay uncapped HI above that cap.
Separately paid wages are outside distributive entity income. If supplied totals
embed FICA-taxed amounts, use the validated `s770_active_fica_income` exclusion;
use `s770_nii_fica_seca_income` for other covered amounts already in NII, excluding
the separately supplied passive/SE intersection. These categories and exclusions
must be disjoint and supported by source data; the model cannot infer overlap.

For a future owners-draw reform, the `s770_draw_*` inputs are classification hooks
and do not impose SECA themselves. The supplier must connect actual taxed amounts:

* OASDI-only: exclude `s770_draw_oasdi_base / q`, where the draw base is after
  wages, existing SE earnings and applicable cap room. Above-room profits remain
  in `A` because no SECA applies to them.
* Uncapped draw HI: exclude the full actual `s770_draw_gross`.

Here `q=1−employer_share*(SE_OASDI_rate+SE_HI_rate)`, currently .9235, using
existing parameters. The undrawn phase-in share and floor-rejected planned draw
remain in `A`. The supplying reform must apply its phase-in and reporting floor
and provide the actual floor-accepted draw and taxed base; an undrawn or
floor-rejected draw supplies zero for both hooks, including when HI is selected.
These hooks do not calculate the draw, phase-in or reporting floor themselves.
No independent owners-draw policy is enabled by these hooks.

## Literal-bill category audit and NOL support

| Statutory category | Available treatment and limitation |
| --- | --- |
| Interest, dividends, annuities, royalties and rents, including ordinary-course business sources after §8(b)(1)(A) | Existing NII sources are reused. Separate ordinary-course/SECA/FICA classification, annuity and royalty completeness are not established. |
| Trade/business income under amended §1411(c)(1)(A)(ii) | Active pass-through residual is added. All other business categories and material-participation determinations are not inferred. |
| Net property-disposition gains, including business property after §8(b)(1)(C) | Existing capital-gain sources are reused. Full business-property gain and associated exclusion classification is unsupported. |
| §172 deduction denial under §8(b)(2) | No federal §172 NOL deduction input/formula exists in the baseline NII source list. Indiana NOL variables are state-specific. |
| Items actually taxed by §1401 or §3101 | Already-SE fields and explicit validated overlap/FICA/draw hooks provide exclusions, not a complete statutory source classifier. |

`s770_niit_nol_deduction` is an explicit TaxUnit input for a validated deduction
**already subtracted from supplied NII**. When active inclusion and `deny_nol`
are on, it is added back to `N` before unified allocation, changing broadened NII
and the existing NIIT component too. Do not supply an AGI-only deduction or treat
ordinary business losses as an NOL deduction. Baseline formulas deduct no federal
NOL from NII, so the default input is zero. Complete literal-bill coverage needs
a validated federal deduction/data route and the missing category classification;
neither a zero input nor matching rates/transfers establishes that coverage.

## OASDI transfers

Transfers are separate from liability. `transfer.mode` selects:

| Mode | Existing NIIT | NII add-on | Active tax |
| --- | --- | --- | --- |
| `0` = `custom` (default) | 0 | `nii_addon.oasdi_share` | `active_business.oasdi_share` |
| `1` = `combined_rate_share` | OASDI rate / combined NII rate | Same combined share | OASDI rate / active rate |
| `2` = `all_addon` | 0 | 100% | `active_business.oasdi_share` |
| `3` = `bill` | `transfer.bill_share` | Same bill share | Same bill share |

The mode parameter uses integer codes because core does not support string
parameter scalars.

The [OACT 2025 F8 description](https://www.ssa.gov/OACT/solvency/provisions_tr2025/coverage.html)
allocates the active tax attributable to 12.4 of its 16.2 percentage points to
OASDI. That convention is approximately 76.5432 percent, distinct from the
bill's 62 percent. Here it is also available for the combined NII rate as a
custom transfer convention. A combined-rate share requires an OASDI rate no
larger than each positive tax rate to which it applies; a zero tax has zero
transfer. When the NII add-on is off or its rate is zero, this custom mode
transfers no existing NIIT, while the active transfer remains independent.
`bill` selects the bill's **transfer rule**, not unsupported category
coverage. Custom part shares default to .62; custom mode does not transfer the
existing 3.8 percent component. Bill mode does, through the separately reported
`s770_existing_niit_revenue_oasdi`. All transfers are zero when both options are
off or before the transfer start year.

`s770_nii_addon_revenue_oasdi`, `s770_active_business_income_revenue_oasdi`, and
`s770_existing_niit_revenue_oasdi` sum to `s770_revenue_oasdi`. Each is its selected
mode's share times the corresponding tax. Aggregate each TaxUnit once alongside
`tob_revenue_oasdi`. Liability equivalence does not establish allocation equivalence.

## Scoring-data limitation

The certified pre-repair artifact forces `s_corp_income` to zero, puts combined
income carrying passive mass in `partnership_income`, and omits
`passive_partnership_s_corp_income` (which therefore defaults to zero). The active
formula runs on those fields, but (b) overstates active income while (a)
understates NII because passive pass-through income is missing. Microcosm #1251
repairs total/passive fields; #1261 splits the entities. Scoring remains
provisional until the selected artifact actually contains both repairs and its
stored fields are checked. No population effects are asserted here.

## Test structure

The YAML examples are grouped by reform configuration across four variable-named
files. Each file stays within the existing five-combination memory budget;
the Congress batcher can therefore release cached reform models between files.
Keep that grouping when adding cases rather than combining the files. Python
properties exercise the vector helpers, with one shared household simulation
checking dated registration, source aggregation and revenue-variable integration.
