# Child care hours and schedules

Issue [#9524](https://github.com/PolicyEngine/policyengine-us/issues/9524)
uses full-time/full-day pricing when a child receives care but the applicable
hours are unknown. This is a modeling assumption, not a finding that the child
attends full time or has a full-time authorization.

The shared numeric hours inputs default to zero. Therefore omitted hours and
explicit zero hours have the same meaning for classification. Positive hours
use the state's existing daily or weekly threshold. A supplied state schedule
or authorization overrides its formula, including an explicit part-time choice.
No new schedule variables or enum choices are required.

Classification alone does not establish participation. Supply each child's
billable care days and expenses when hours are unknown. A child with no care
hours, care days, or expenses must not receive a subsidy solely because the
schedule falls back to full time. The seven-state payment changes below recognize positive child-level
daily/weekly hours or monthly/weekly care days as care participation. A household expense total alone cannot identify which siblings receive
care. Daily rate programs continue to require their existing billable monthly
days; the fallback does not invent paid days or hourly reimbursement quantities.

Use the hours measure required by the state. Where payment follows an existing
authorization, supply that authorization rather than trying to infer it from a
short period of observed attendance. The fallback does not change eligibility,
provider rules, expense caps, historical thresholds, or special schedule rules.
For example, South Carolina's Head Start override remains half time.

## Revised implementation scope

The September 2026 review covers all 50 states and DC. The implementation batch
covers 13 states with a clear binary category in the relevant payment path:
Alabama, Arkansas, Florida, Kentucky, Mississippi, New Jersey, North Dakota,
Pennsylvania, South Carolina, Tennessee, Virginia, Wisconsin, and Wyoming.

The daily classification changes cover Arkansas, Florida, Kentucky,
Pennsylvania, Virginia, and Wyoming. Florida's family copay considers only
children with positive daily hours or billable monthly days, so an inactive
sibling's fallback cannot select the full-time fee. Virginia retains explicit full-day authorizations, including exceptions
when part-day care is unavailable.

The companion payment changes cover Alabama, Mississippi, New Jersey,
North Dakota, South Carolina, Tennessee, and Wisconsin. They coordinate
classification with care participation, reimbursement and copay calculations.
Wisconsin retains its existing statutory conversion hours; no reported hours
are imputed. North Dakota's provider bonuses also require a child in care.

The following table records the other jurisdictions. Exclusion from this batch
does not certify every aspect of the program or resolve the entire issue.

| Jurisdiction | Reason for no change in this batch |
| --- | --- |
| Alaska | Provider billing selects monthly or daily units as well as full/part time; preserve the input. |
| Arizona | The existing daily rate/day-count path has no binary hour classification. |
| California | Billing units and provider-specific reimbursement coefficients require a separate review. |
| Colorado | Hours affect a parent-fee scale; this is not a binary schedule fix. |
| Connecticut | Four care bands require a separate policy and unit review. |
| DC | Traditional, extended and nontraditional schedules cannot be inferred from total hours. |
| Delaware | [School-age extended authorization](https://dhss.delaware.gov/wp-content/uploads/sites/11/dss/pdf/PurchaseofCareProviderHandbook_FINAL1_25_2023.pdf#page=25) combines school days and holidays; preserve pending authorization review. |
| Georgia | Before/after-school is a distinct schedule; preserve the input. |
| Hawaii | Authorized monthly hours and before/after-school rules require activity and calendar information. |
| Idaho | The existing child-hours proxy stands in for parental activity authorization; a two-choice enum alone is insufficient. |
| Illinois | Multiple daily units, extended care and NONE need a separate unit/participation review. |
| Indiana | Existing weekly full-time rate path has no modeled binary hour split. |
| Iowa | Reimbursement uses half-day units and unit caps rather than a simple category. |
| Kansas | Hourly payment requires authorized monthly quantities; do not invent them. |
| Louisiana | Monthly and weekly attendance reconciliation is a separate care-unit problem. |
| Maine | [Authorization](https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=28) uses parental activity; school-age payments also account for school calendars. |
| Maryland | Three service units require their own payment and copay review. |
| Massachusetts | Preserve the full-time fallback and provider/schedule exceptions from #9489. |
| Michigan | Authorization follows parental activity and biweekly blocks. |
| Minnesota | Hourly/daily/weekly pricing and legal nonlicensed providers require explicit units. |
| Missouri | Full/half/part-time bands are outside this binary-category batch. |
| Montana | The model prices [monthly authorization](https://dphhs.mt.gov/assets/ecfsd/childcare/documentsandresources/BBSProviderRatesMonthly.pdf); the cited daily threshold is not sufficient to infer that authorization. |
| Nebraska | A full-day fallback already exists; in-home hourly units are a separate issue. |
| Nevada | Part-day adjustments are not modeled; no narrow default correction is established. |
| New Hampshire | Service level follows parental authorized activity hours. |
| New Mexico | Split-custody/two-provider service units cannot be inferred from hours alone. |
| New York | Weekly/daily/part-day units and excess-care additions require separate review. |
| Ohio | Hourly/part/full-time pricing requires a unit and participation review. |
| Oklahoma | Existing full-time fallback already preserves the positive daily-hours threshold. |
| Oregon | Care quantities follow parental need, travel and authorization rules. |
| Rhode Island | Four authorized care bands are outside this binary-category batch. |
| South Dakota | Three weekly bands and a dated model start require separate review. |
| Texas | Preserve FULL_TIME/PART_TIME/BLENDED as inputs. Short daily care does not identify blended authorization; #9536 was closed. |
| Utah | Existing monthly/expense path has no modeled binary hour split. |
| Vermont | Three care bands and a separate no-care participation problem need their own review. |
| Washington | Authorization and provider-specific monthly units require more than a daily threshold. |
| West Virginia | Existing daily rate/day-count path has no modeled binary hour split. |

## Batch inputs

Core currently treats a supplied variable as an input for its whole population
array. If one person supplies a schedule or weekly hours and another omits it,
the omitted row receives the variable's default rather than running its formula.
For mixed household/batch requests, supply that variable consistently for every
relevant child. These state changes do not redesign that core input behavior.

Partner contract tests are unchanged. The revised behavior can affect both
reimbursement ceilings and copays for callers who omit hours; neither direction
is uniformly conservative for the final benefit.
