# South Carolina regular heating assistance

The accepted FY2026 plan governs the statewide regular-heating schedule: base
$200 plus the specified demographic, fuel, low-income and high-burden additions,
up to $850. The plan repeatedly uses 30% SMI and burden of 20% or more. Those
specific adopted definitions take precedence over the matrix's older-vintage
42% SMI and conflicting strict electric/tank-fill burden language. The matrix's
explicit gas/oil/kerosene/propane fuel definition is retained where consistent.

The model calculates countable income, the eligible household size, the annual
ceiling, eligibility and the regular heating award. The agency's approved 2026
WAP plan (physical page 23) expressly attributes to LIHEAP guidance the rule that
ineligible members' income counts but those members do not count toward household
size. The approved 2024 plan (physical page 21) states the same rule, supporting
continuity for FY2026. Only that explicitly attributed LIHEAP rule is used from
those plans; their weatherization eligibility and payment rules are not used.
The qualified-size ceiling and low-income threshold use this rule. Demographic
supplements retain the LIHEAP plan's explicit household-member conditions; that
plan does not restrict these conditions to qualified members. There is no
categorical income bypass or asset test in the adopted LIHEAP plan.

Income uses the accepted plan's checked categories. Minor earnings are excluded;
minor unearned income is counted because adult verification requirements are
not an express income exclusion. Monthly SSI aggregates once over the year.
Pension and Social Security aggregates include their components; military
retirement pay is separate and enters once. The cross-state military-survivor
aggregate migration remains deferred. Recurring
IRA/401k receipts enter through the separate retirement_distributions aggregate.
Annual inputs cannot distinguish excluded one-time retirement lump sums. Private
survivor receipts and farm rent are separate. Net business inputs receive no
second deduction. Received unearned sources are floored separately per person,
so a rental loss cannot cancel a positive pension or another receipt. UI uses
the shared reported-or-modeled unemployment amount. Cash from friends/relatives
uses financial_assistance. Legal
settlements lack an exact input. TANF, general assistance, interest/dividends,
strike, insurance, one-time lump sums and foster payments are not counted under
the current checklist. Social Security remains gross, including Medicare, as
the accepted plan specifies; no Medicare deduction is applied. Application-month
income timing and work-study embedded in wages remain input limitations.

The annual income ceiling reuses requested-year federal SMI. Rounding the
four-person 60% base and then flooring the size-adjusted result reproduces all
eight current agency annual limits, including sizes seven and eight. That order
is inferred from published amounts, not an explicit legal rounding direction.
The inconsistent one-person monthly figure is not used. The 30% supplement
boundary uses the plan percentage without rounding the income ratio.
A separate income gate preserves the strict federal 110% FPG protection using
the same actual qualified household size and prior-year guidelines. The state
SMI ceiling remains unchanged; exact 110% income has no federal protection.
Young-child supplements use completed age, retaining age-five children until
their sixth birthday.

Energy burden uses the sum of existing electric, gas and fuel bills. Water,
sewer, trash and telephone are excluded from home-energy cost. This reuses
represented bills more faithfully than primary heating cost alone, but annual
flows still approximate the current month and rent-embedded charges are missing.
Positive expenses at zero income qualify for high burden; zero expense does not
prove a burden. There is no general benefit-to-bill cap or subsidized-renter
exclusion in the supported schedule. Heating responsibility uses has_heating_expense or heat_expense_included_in_rent,
with an explicit NONE heating type always excluded. The existing responsibility
input supports cases where a household pays for secondary heating. There is no
extra exclusion for subsidized housing or heat included in rent. The model does
not split households across SPM units, adjudicate applications, or model local
CAA restrictions, priority and available funding.

Only FY2026 is researched. The revised FY2027 plan is a draft. Earlier parameter
backfills are unverified historical estimates. Crisis, cooling, weatherization
and equipment are outside this work. The SPM unit approximates the energy household. Application-month income and
expense data and detailed legal immigration facts remain limitations of existing
inputs; parameter backfilling does not verify earlier years.
