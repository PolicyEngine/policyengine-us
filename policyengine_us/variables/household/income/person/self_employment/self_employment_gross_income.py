from policyengine_us.model_api import *


class self_employment_gross_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Gross self-employment income"
    documentation = (
        "Schedule C line 7 and Schedule F line 9 gross income (receipts after "
        "cost of goods sold and before other business expenses), reconstructed "
        "as net Schedule C (regular and SSTB) and Schedule F profit plus "
        "self_employment_expense. Covers sole-proprietor Schedule C and "
        "Schedule F businesses only; partnership_self_employment_net_earnings "
        "is excluded because partnership expenses are deducted on Form 1065, "
        "so consumers needing partnership earnings add it separately. Each "
        "source's gross income is at least its net profit floored at zero, so "
        "the result is never below the sum of those floors: a loss in one "
        "source does not offset another when expenses are omitted. With "
        "complete expenses the reconstruction is exact; with none, as in "
        "microsimulation, the result is the sum of the per-source floors. "
        "The non-farm sources are post-labor-supply-response."
    )
    reference = (
        "https://www.irs.gov/instructions/i1040sc",
        "https://www.irs.gov/instructions/i1040sf",
        "https://www.irs.gov/pub/irs-pdf/f1040sc.pdf#page=1",
        "https://www.irs.gov/pub/irs-pdf/f1040sf.pdf#page=1",
    )

    def formula(person, period, parameters):
        sources = [
            "self_employment_income",
            "sstb_self_employment_income",
            "farm_operations_income",
        ]
        # Add back the expenses deducted from net profit, preserving losses
        # until after the add-back.
        reconstructed = add(person, period, sources + ["self_employment_expense"])
        # Each source's gross income is at least its net profit floored at zero.
        source_floor = sum(max_(person(source, period), 0) for source in sources)
        return max_(reconstructed, source_floor)
