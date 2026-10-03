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

SPMUnit approximates the energy-sharing household. The historical official
manual supplies two detailed rules not restated or superseded in the FY2026
plan: only qualified members count in size while all members' countable income
is retained; all income of dependent full-time college students under 22 is
excluded. The current plan governs conflicting rules in that older manual,
including the income threshold, nominal SNAP payments and countable cash gifts.

Annual income flows approximate the application assessment period. Existing net
business income is used without a second expense deduction, and rental income
is assumed nonnegative. The historical manual classifies rental income as
earned. Social Security includes its survivor component; taxable and exempt
pensions are included through `pension_income`. Pension and military survivor
classifications are not added on top. The separate non-Social-Security
`survivor_benefits` input is counted. Monthly SSI and Delaware TANF are aggregated
to annual amounts; TANF is counted once for the household.

`spm_unit_paycheck_withholdings` plus Wilmington earned income tax approximates
federal, state and city payroll withholding. This estimates annual taxes, rather
than observing actual withholding. The shared helper already includes Delaware
employee paid-leave contributions. It can also include tax attributable to
excluded child or student income; adjusted income is bounded below by zero.
The household TANF amount does not identify a student's share. Medicare and
pension health deductions are deferred because actual withheld amounts are not
represented.

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
Separately paid solar heating has no verified matrix classification; neither it
nor an unspecified separately paid fuel is assigned an invented benefit.

## Sources

- [FY2026 accepted state plan](https://liheapch.acf.gov/docs/2026/state-plans/DE_Plan_2026.pdf#page=5), PDF pages 5-7, 9-10 and 43.
- [FY2026 Delaware benefit matrix](https://liheapch.acf.gov/docs/2026/benefits-matricies/CO_BenefitMatrix_Heating_2026.pdf#page=1), PDF page 1, approved April 28, 2025.
- [Historical official DEAP manual](https://bidcondocs.delaware.gov/HSS/HSS_15027Liheap_MAN.pdf#page=35), sections 418, 424, 426 and 429.2; PDF pages 35-36 and 40-42.
