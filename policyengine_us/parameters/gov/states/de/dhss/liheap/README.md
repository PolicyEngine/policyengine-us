# Delaware regular heating assistance

The FY2026 benefit matrix and accepted state plan support regular heating-bill
assistance. Crisis, cooling, weatherization, equipment and funding rationing are
outside this implementation. Parameters start on October 1, 2025. Earlier
backfilled results are unverified historical estimates. FY2027 has not been
verified.

The federal Clearinghouse incorrectly names the Delaware matrix `CO` in its URL.
The document title, Delaware income figures and approval date identify it as the
Delaware FY2026 matrix. All eight income bands and five distinct fuel schedules
are represented; kerosene shares the oil schedule. The matrix already accounts
for statewide fuel costs and energy burden. No additional expense cap is imposed.

The income limit reuses the requested year's federal SMI amount and household
adjustment factors. Rounding the four-person 60% amount before truncating the
size-adjusted limit reproduces all 12 published limits. Flooring the income
limit times each band's normalized upper rate reproduces all 96 printed income
boundaries. These are reproducible numerical conventions, not express legal
rounding instructions. The source does not resolve applicant income with cents.
The income gate also preserves the strict federal 110% FPG protection, using
the same actual qualified household size and the prior-year guidelines. The
printed state limit and benefit bands remain intact; protected income above
that limit uses the supported final benefit band. Exact 110% income has no
federal protection.

SPMUnit approximates the energy-sharing household. The historical official
manual supplies two detailed rules not restated or superseded in the FY2026
plan: only qualified members count in size while all members' countable income
is retained; all income of dependent full-time college students under 22 is
excluded. The current plan governs conflicting rules in that older manual,
including the income threshold, nominal SNAP payments and countable cash gifts.

Annual income flows approximate the application assessment period. Existing net
business and rental income retain their existing net treatment without a
second expense deduction. The historical manual classifies rental income as
earned. Social Security includes its survivor component; taxable and exempt
pensions are included through `pension_income`; ongoing IRA/401k receipts enter
through the separate `retirement_distributions` aggregate. Annual inputs do not
identify excluded one-time retirement lump sums. Military retirement pay is
counted separately once; pension-survivor classification is not added on top.
The cross-state military-survivor aggregate migration remains deferred.
The separate non-Social-Security
`survivor_benefits` input is counted. Monthly SSI and take-up-gated TANF are
aggregated to annual amounts; TANF counts once for the household. UI uses the
shared reported-or-modeled unemployment-compensation amount.

`spm_unit_paycheck_withholdings` plus Wilmington earned income tax approximates
federal, state and city payroll withholding. This estimates annual taxes, rather
than observing actual withholding. The shared helper already includes Delaware
employee paid-leave contributions. Identifiable Social Security, Medicare,
Delaware paid-leave, Delaware income and Wilmington taxes on excluded earnings
are removed from the aggregate deductions, each bounded below by zero. Remaining
supplied deductions are preserved. The person-level Delaware income-tax estimate
retains tax on a minor's counted unearned income; excluded earnings use IRS wages
after pre-tax contributions and existing person business adjustments. Federal
income tax, additional Medicare and other shared tax-unit adjustments
are tax-unit aggregates without person allocations; their attribution remains
an annual-estimate limitation. Adjusted income is bounded below by zero.
The household TANF amount does not identify a student's share. Each person's
Social Security is net of their existing out-of-pocket Medicare Part B premium,
bounded at zero. That premium variable accepts an actual supplied amount or
uses the shared enrolled/MSP calculation. The separate reported-only premium
field is not wired here. Generic ordinary and payroll premiums do not establish
pension-health withholding, which remains unobserved and is not deducted.

Contract earnings use existing employment or business inputs; royalties are
represented only to the extent included in rental income. Work-study or other
excluded payments embedded in reported wages cannot be distinguished. The model
does not infer boarder status, institutional residence, temporary absence,
optional exclusion of students attending out of state, legal-separation proof,
duplicate applications, application timing or funding priority. These missing
facts are limitations, not automatic eligibility exclusions.

Heat included in full unsubsidized rent uses the electric schedule. Subsidized
heat-in-rent is ineligible. Subsidized households paying separately for heat
receive the flat amount when actual tenant rent is within the published ceiling.
Solar with a positive supplemental-electric bill can receive the fuel-independent
subsidized flat award. Ordinary solar pricing has no verified matrix mapping,
so it remains eligible with a zero ordinary matrix amount; an unspecified
separately paid fuel establishes no matching bill.

## Sources

- [FY2026 accepted state plan #page 5-7,9-10,43](https://liheapch.acf.gov/docs/2026/state-plans/DE_Plan_2026.pdf#page=5), PDF pages 5-7, 9-10 and 43.
- [FY2026 Delaware benefit matrix](https://liheapch.acf.gov/docs/2026/benefits-matricies/CO_BenefitMatrix_Heating_2026.pdf), PDF page 1, approved April 28, 2025.
- [Historical official DEAP manual #page 35-38,40-42](https://bidcondocs.delaware.gov/HSS/HSS_15027Liheap_MAN.pdf#page=35), sections 418, 424, 426 and 429.2; PDF pages 35-36 and 40-42.
