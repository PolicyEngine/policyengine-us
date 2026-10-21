# West Virginia modeled regular heating assistance

The household-size, countable-income, income-limit, income-eligibility and modeled
regular-payment components use the FY2026 state plan and operational manuals,
including the adopted October 2026 update for FY2027. The assistance group includes co-residents sharing
heating costs. Qualified members count in its size; nonqualified members' income
is not excluded. SPM membership approximates the physical sharing group. Prior
assistance in another group can exclude a member, but receipt history is absent
from existing inputs and is not inferred.

The plan specifies 60% of requested-year SMI through size seven, then 150% of
prior-calendar-year FPG from size eight. Nearest-dollar monthly rounding matches
all ten preserved FY2026 agency amounts. Applying the guideline before rounding also
matches the manual's size-eleven limit of $8,831; repeatedly adding the web page's
rounded $688 increment gives a conflicting $8,832. The adopted percentage and
manual calculation take precedence over that rounded web shorthand. This is a
numerically validated rounding convention, not an express rounding instruction.
The same calculation matches the current manual's FY2027 monthly limits for
sizes one through eleven. The payment grid's apparent size-twelve maximum of
$10,160 conflicts with the guideline-derived $9,805; payment cells do not replace
the stated income eligibility rule.
Fresh FY2027 public materials print $6,695 for eight people, while the
operational manual and 150% FPG calculation give $6,965. The model retains the
manual/guideline amount; this discrepancy does not authorize smoothing any
other printed payment-band bound.

Countable income follows the detailed operational manual, which current Board
of Review decisions apply, over unchecked summary-plan categories. This is an
explicit source-priority interpretation: minor earnings, TANF, general
assistance and recurring gifts count. RSDI and SSI do not. The manual distinguishes
excluded nonrecurring lump sums from recurring payments prorated over the period
they cover. Annual income fields approximate recurring application-month income.
Existing net business inputs receive no second 20% deduction, and business or
estate losses do not offset other sources under this modeling approximation. This does
not reproduce the source's gross-receipts calculation.

Pension, military retirement pay, retirement-account and non-Social-Security
survivor receipts each enter once through their separate existing inputs.
Each person's represented recurring source is floored at zero before aggregation;
rental losses cannot cancel pensions, wages or another member's receipts.
Unemployment uses the shared reported-or-modeled receipt amount. TANF uses the
shared take-up-gated receipt, annualizing monthly WV WORKS once at the household
level. Separate royalties and foster-care receipts are not identified
by existing inputs. Generic VA benefits cannot separate excluded Aid and
Attendance. The December 18, 2025 announcement broadly describes VA benefits
as excluded, in tension with the manual's specific Aid and Attendance
exclusion. Existing manual-priority treatment is retained; this source conflict
is not declared resolved. Employment cannot separate excluded work-study, CNCS or CSEP
wages. A work-study participation flag cannot determine which wages to subtract.
Aggregate child support, retirement, insurance, estate and gift inputs cannot
identify every recurring payment, arrearage or earmarked reimbursement. These
are input limitations, not blanket legal inclusions or exclusions. Standalone
capital gains, life-insurance death proceeds and gambling/lottery winnings are
treated as nonrecurring; an actual recurring installment needs a separately
identified receipt that existing inputs do not provide. The operative manual's
gross-income rule does not authorize a general Medicare premium deduction;
RSDI is already excluded in full, so its Medicare withholding is not subtracted
from other countable receipts.

The income-eligibility component requires a positive qualified household size
and countable income at or below the existing limit. The operational manual's
section 21.3.1.A explicitly denies groups above the income ceiling. Mail-out
reviews still require verification, and the manual's mixed SSI/employment
example requires verification of the employment income. The summary plan's
categorical checkboxes remain a source tension, but they do not establish an
unconstrained SNAP, TANF or SSI income-ceiling bypass. This follows the detailed
operational manual's income rule rather than inferring an exemption from
application streamlining.

The regular-payment output supports one through twenty qualified members. On
October 20, 2026, the user approved using the published upper income bounds as
continuous closed-top intervals, without rounding observed monthly income. This
resolves the overlapping first/second lower endpoints and fractional-dollar
gaps. Every other printed upper bound is retained, including irregular values;
the table is not smoothed. The existing income ceiling is still independently
applied. The source library preserves both literal grids and edition details,
including the earlier chart's stale FY2025 heading despite its FY2026 limits.

All 840 occupied cells across the two published grids exactly equal
`base_amount + amount_step * (size - 1 - band_index)`.
This is lossless compression of the published amounts, not permission to
extrapolate. The ordinary income limit confines eligible sizes one through
twenty to occupied cells. Fuel multipliers are applied once to the base amount.
Integer-dollar bases and three-decimal multipliers give exact dollar mills;
rounding those to cents half up reproduces the printed $70.79 and $147.02.
No unsupported actual-bill cap or proportional reduction for partial
responsibility is imposed. The combined regular/crisis ceiling and equipment
maximum are outside this regular payment calculation.

Heating responsibility reuses `has_heating_expense`. Its default requires a
matching positive primary-fuel bill and excludes heat bundled in rent. A
subsidized tenant paying direct heating costs can qualify. The existing flag
can be supplied for a known obligation that its default cannot infer, including
documented heating charges in rent or auxiliary electric costs with self-cut
wood. The heat-in-rent or subsidy flag alone cannot establish that obligation.
No blanket exclusion of subsidized renters is introduced. A default zero for
bundled rent without the responsibility fact is not a definitive legal denial.

Some facts remain unobserved: designated rent charges, anticipated surcharges,
traditional versus movable dwellings, portable-heater or alternate-fuel
approval, and prior-season duplicate assistance. The FY2027 manual explicitly
retains responsibility for a zero/minimal-income client whose own heating bill
is paid by an outsider; earlier wording differs. The model does not identify
every billholder or third-party arrangement and does not backdate that
exception. These are documented existing-input approximations, not new inputs
or a complete administrative housing predicate.

Payment coverage above twenty members and for UNSPECIFIED, SOLAR or OTHER fuel
remains unmodeled. Output zero for those cases means no modeled award, not legal
ineligibility. NONE affirmatively reports no heating. The registry remains
partial and omits `verified_years`; no fully verified program year is claimed.
Earlier backfilled results are unverified historical estimates. Crisis, cooling,
weatherization, equipment and the separate utility discount remain out of scope.
