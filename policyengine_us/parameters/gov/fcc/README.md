# Federal Communications Commission (FCC)

## EBB and ACP annual amounts

The model retains annual dollar inputs and outputs for broadband costs, the
Emergency Broadband Benefit (EBB), and the Affordable Connectivity Program (ACP).
For these two benefits, it allocates the nonnegative annual cost after Lifeline
uniformly across 12 months and sums the lesser of that monthly cost and each
month's cap. This allocation assumes uniform bills; it does not reconstruct
actual bills, enrollment changes, or receipt. The existing Lifeline calculation
and annual qualification inputs remain unchanged. These formulas do not
calculate the statutory high-cost enhancement.

The formulas read caps at each month's end. They count May 2021 as an EBB billing
month after the May 12 launch, without daily proration. ACP legal enrollment
started December 31, 2021, but the FCC combined new-household discounts from
December 31 through January 31 into one January 2022 data-month cap. The model
therefore allocates no separate ACP cap to December 2021. See [FCC 22-2,
paragraphs 2-3](https://docs.fcc.gov/public/attachments/FCC-22-2A1.pdf#page=3) and
[DA 21-1654, paragraphs 7-8](https://docs.fcc.gov/public/attachments/DA-21-1654A1.pdf#page=3).

| Billing months | EBB monthly cap, non-Tribal / Tribal | ACP monthly cap, non-Tribal / Tribal |
| --- | --- | --- |
| 2015-2020 | $0 / $0 | $0 / $0 |
| January-April 2021 | $0 / $0 | $0 / $0 |
| May-December 2021 | $50 / $75 | $0 / $0 |
| January-February 2022 | $50 / $75 for the conditional legacy subset | $30 / $75 without EBB |
| March-December 2022 and all 2023 | $0 / $0 | $30 / $75 |
| January-April 2024 | $0 / $0 | $30 / $75 |
| May 2024 | $0 / $0 | $14 / $35 conditional public reimbursement |
| June 2024-December 2026 | $0 / $0 | $0 / $0 |

The legacy transition assumes both the statute's prior-qualification and
benefit-reduction conditions and the FCC's enrollment, continuing-eligibility,
and usage requirements. The model preserves its existing `enrolled_in_ebb`
input; that annual boolean cannot reconstruct those histories. The statute's
qualified class and the FCC enrollment cutoff do not establish identical classes
for every household. This component leaves that broader question unresolved.
See the [2021 statute and section 60502(b) transition
notes](https://www.govinfo.gov/content/pkg/USCODE-2021-title47/html/USCODE-2021-title47-chap16.htm),
[DA 21-1654, paragraphs 5-8](https://docs.fcc.gov/public/attachments/DA-21-1654A1.pdf#page=2),
and [FCC 22-2, footnote 22](https://docs.fcc.gov/public/attachments/FCC-22-2A1.pdf#page=5).

The FCC caps May 2024 public reimbursement at $14/$35 for continuing enrolled
households that opt in to service from providers that elect to pass through a
discount.
Those reimbursement ceilings do not replace the statutory $30/$75 amounts or
establish automatic receipt.
Providers could offer larger private discounts. The FCC identified April as the
last fully funded month and May as the last reimbursement month in
[DA 24-195, pages 1-3](https://docs.fcc.gov/public/attachments/DA-24-195A1.pdf#page=1)
and set the partial reimbursement ceilings in
[DA 24-342, pages 1-2](https://docs.fcc.gov/public/attachments/DA-24-342A1.pdf#page=1).

## Qualification, overrides and monthly requests

`is_acp_eligible` retains the existing categorical and financial qualification
routes. A positive annual EBB amount does not make that annual qualification
flag false. The ACP payment formula uses positive annual EBB as a timing
proxy and suppresses ACP only in months with a positive selected EBB cap. This
allows ACP after the legacy transition ends and prevents calculated EBB and ACP
from using the same month's allocated cost twice.

The formulas floor negative annual cost inputs at zero and leave explicit annual
cash overrides intact. Forced cash amounts do not establish lawful monthly
receipt or guarantee that total payments stay within cost. For calculated
amounts, the two benefits together cannot exceed the nonnegative annual cost.
Core still divides a YEAR amount by 12 when a caller requests MONTH; that result
averages the annual amount and does not report a particular month's payment.
This financial component does not reconstruct full program eligibility, provider
participation, or historical household receipt, and does not qualify a population
study.
