# 'Above-the-line' deductions

Above-the-line deductions are deductions made from gross income to arrive at adjusted gross income. The Code refers to deductions by their section; below is an in-progress table of the sections and their deductions.

| Section | Deduction |
| --- | --- |
| [85](https://www.law.cornell.edu/uscode/text/26/85) | Unemployment compensation |
| [86](https://www.law.cornell.edu/uscode/text/26/86) | Social security |
| [135](https://www.law.cornell.edu/uscode/text/26/135) | Tuition fees |
| [137](https://www.law.cornell.edu/uscode/text/26/137) | Adoption expenses |
| [199](https://www.law.cornell.edu/uscode/text/26/199) | Domestic production activities (repealed) |
| [219](https://www.law.cornell.edu/uscode/text/26/219) | Retirement savings |
| [221](https://www.law.cornell.edu/uscode/text/26/221) | Education/student loan interest |
| [222](https://www.law.cornell.edu/uscode/text/26/222) | Qualified tuition expenses (repealed) |
| [223](https://www.law.cornell.edu/uscode/text/26/223) | Health savings accounts |
| [469](https://www.law.cornell.edu/uscode/text/26/469) | Passive activity |
| [911](https://www.law.cornell.edu/uscode/text/26/911) | Foreign earned income |
| [933](https://www.law.cornell.edu/uscode/text/26/933) | Income from Puerto Rico |
## Each person's deductions

Several state taxes and benefits need each spouse's own AGI on a joint return: Kentucky, Montana (through 2023), Delaware, Virginia and the District of Columbia, where spouses can file separately on one form; Ohio's joint filing credit; West Virginia's senior citizen and disability deduction; state withholding estimates; and Medicaid household income. `adjusted_gross_income_person` is each person's gross income less `above_the_line_deductions_person`. The head's and spouse's amounts add up to `above_the_line_deductions` and `adjusted_gross_income`.

| Deduction | Who takes it |
| --- | --- |
| Person-level deductions: IRA, educator expenses, early withdrawal penalty, student loan interest, adoption assistance, U.S. savings bonds for education | The person who has it. Student loan interest is the return's limited deduction, divided by the interest each spouse paid. |
| Self-employment tax, self-employed health insurance and retirement plans, alimony paid | The person who has it, through `<deduction>_person`. |
| Business and capital losses (`loss_ald`) | `loss_ald_person`: the return's business loss after Section 461(l), by each spouse's own business losses; the capital loss after the $3,000 limit (`limited_capital_loss_person`), by each spouse's own capital losses. A Form 4797 loss, recorded for the tax unit, counts equally for both. |
| HSA, tuition and fees, domestic production, possession income | Divided equally, since the input is the tax unit's. For an HSA, 26 USC 223(b)(5) divides a married couple's limit equally unless they agree otherwise. |

A tax unit dependent's deductions are on their own return, so they never lower the filer's AGI; the dependent's `above_the_line_deductions_person` is what they deduct on that return, and Medicaid uses it.

The states that read these amounts tell spouses to report their own income and deductions (Kentucky: KRS 141.180(3); Delaware: 30 Del. C. 1162(b)(1); the District: Schedule S, Calculation J; Virginia: the separate VAGI worksheet). Montana also has its own rule for capital losses: a loss clearly attributable to one spouse goes on that spouse's return, and otherwise it is split equally (MCA 15-30-2110(6), through 2023), which `mt_capital_loss_reallocation` applies.
