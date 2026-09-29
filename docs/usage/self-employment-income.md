# Self-employment income

The shared variables reconstruct business gross income from existing net-income
amounts. Benefit programs apply their own deductions after that reconstruction.

| Variable | Meaning |
| --- | --- |
| `employment_income` | Employee wages, separate from business income. |
| `self_employment_income` | Non-farm, non-SSTB net self-employment income. |
| `sstb_self_employment_income` | Net income from a specified service trade or business. |
| `farm_operations_income` | Net income from active farming operations. |
| `self_employment_expense` | Expenses deducted to obtain the three net amounts above, excluding cost of goods sold. |
| `self_employment_gross_income` | Their reconstructed gross income after cost of goods sold and before other business expenses, subject to the floor below. |

These amounts are annual, person-level values. The two non-farm net-income
variables include labor-supply responses.

## Formula direction

The accounting reconstruction is:

```text
net_income = self_employment_income
           + sstb_self_employment_income
           + farm_operations_income

reconstructed_gross = net_income + self_employment_expense
```

The gross-income formula also enforces a floor equal to the sum of the three net
sources individually floored at zero. This is a fallback when expenses are
missing or incomplete. For example, $6,000 non-farm profit and a $10,000 farm loss
with no expenses supplied produce $6,000, rather than a negative gross amount.
This floor is a modeling assumption, not an IRS rule. Tax-reported gross income
can be negative, for example when cost of goods sold exceeds sales and other
income. Complete expense information therefore reproduces the tax-form gross
amount only when the floor does not bind and the reported net profit has not
already been adjusted by tax loss limitations.

The dependency goes from net income and expenses to gross income. Do not add a
reverse formula deriving the existing net-income variables from gross income:
that would create a circular dependency. Supplying gross income directly does
not infer net income or expenses; callers still supply net amounts for tax
calculations.

## Program deductions

For a program using a standard percentage deduction, the consumer follows this
pattern; these names are placeholders for program-specific variables:

```text
program_expense_deduction = applicable_gross_income * program_rate
program_countable_self_employment_income =
    max(0, applicable_gross_income - program_expense_deduction)
```

For example, net profit of $15,000 plus $25,000 of expenses reconstructs $40,000
of gross income. A 25% standard deduction leaves $30,000 of countable income.
The original $25,000 of expenses is not deducted a second time. The program's
rate belongs in its parameters.

Programs permitting actual expenses must identify the costs their own rules
allow. `self_employment_expense` contains tax-return expense add-backs and is not
a universal benefit-program deduction. Any actual-cost election, loss treatment,
averaging period, and later earned-income disregard also belong in the program
calculation. Combine wages and self-employment income only after applying their
respective rules.

## Coverage and missing information

- The expense input defaults to zero. An omitted answer is not evidence of zero
  actual expenses, so the derived amount should not be presented as verified
  gross income without the necessary source information.
- The gross amount is after cost of goods sold. It does not reconstruct gross
  receipts before that accounting step.
- The aggregate covers Schedule C and Schedule F income. It excludes
  `partnership_self_employment_net_earnings` and does not preserve a gross-income
  breakdown between farm and non-farm businesses. Consumers requiring those
  distinctions need additional information.
- The floor applies to the three income categories, not to each individual
  business within a category. It does not implement program-specific loss rules.

The accounting definitions follow [Schedule C](https://www.irs.gov/pub/irs-pdf/f1040sc.pdf)
and [Schedule F](https://www.irs.gov/pub/irs-pdf/f1040sf.pdf). Their tax definitions
do not determine which income and expenses a benefit program must count.
