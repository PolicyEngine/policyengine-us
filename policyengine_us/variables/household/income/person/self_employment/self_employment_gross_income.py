from policyengine_us.model_api import *


class self_employment_gross_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Gross self-employment income"
    documentation = (
        "Schedule C line 7 and Schedule F line 9 gross income (after cost of "
        "goods sold and before other business expenses), reconstructed "
        "as net Schedule C (regular and SSTB) and Schedule F profit plus "
        "self_employment_expense. Covers sole-proprietor Schedule C and "
        "Schedule F businesses only; partnership_self_employment_net_earnings "
        "is excluded because partnership expenses are deducted on Form 1065, "
        "so consumers needing partnership earnings handle it separately. "
        "A modeling floor prevents the result from falling below the sum of "
        "the three net sources individually floored at zero: a loss in one "
        "source does not offset another when expenses are omitted. Complete "
        "expenses matching the reported net amounts reconstruct tax-reported "
        "gross income only when this floor does not bind. The floor is not "
        "an IRS rule; tax-reported gross income can be negative. With no "
        "expenses supplied, the result is the sum of the per-source floors. "
        "The non-farm sources are post-labor-supply-response. This calculation "
        "does not change net self-employment income or employment income. "
        "Consumers apply their own expense deductions to the appropriate "
        "gross-income base, then combine countable self-employment income "
        "with separately treated wages."
    )
    reference = (
        "https://www.irs.gov/instructions/i1040sc",
        "https://www.irs.gov/instructions/i1040sf",
        "https://www.irs.gov/pub/irs-pdf/f1040sc.pdf#page=1",
        "https://www.irs.gov/pub/irs-pdf/f1040sf.pdf#page=1",
    )

    def formula(person, period, parameters):
        net_income_sources = [
            "self_employment_income",
            "sstb_self_employment_income",
            "farm_operations_income",
        ]
        # Add back the expenses deducted from net profit, preserving losses
        # until after the add-back.
        net_income = add(person, period, net_income_sources)
        expenses = person("self_employment_expense", period)
        reconstructed = net_income + expenses
        # Apply the modeling fallback separately to each net-income source.
        source_floor = 0
        for source in net_income_sources:
            source_floor = source_floor + max_(person(source, period), 0)
        return max_(reconstructed, source_floor)
