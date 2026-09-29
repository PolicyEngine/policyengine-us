from policyengine_us.model_api import *


class self_employment_gross_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Gross self-employment income"
    documentation = (
        "Gross self-employment receipts, reconstructed as net Schedule C "
        "(regular and SSTB) and Schedule F profit plus work_expense, the "
        "business costs already deducted in arriving at that net profit. Covers "
        "sole-proprietor Schedule C and Schedule F businesses only; "
        "partnership_self_employment_net_earnings is excluded by design because "
        "partnership expenses are deducted on Form 1065 and that variable is not "
        "an additional gross source, so consumers needing partnership earnings "
        "add it separately. The zero floor applies to the combined farm plus "
        "non-farm sum. work_expense is the person-level counterpart of the "
        "SPM-unit SNAP input snap_self_employment_income_expense and is not "
        "derived from it. Omitted expenses are assumed to be zero, which biases "
        "the result downward and zeroes business losses; with no data source for "
        "work_expense, microsimulation yields max(net, 0). This variable reads "
        "total_self_employment_income, so it is post-labor-supply-response, "
        "unlike the pre-response snap_gross_self_employment_income_person."
    )
    reference = (
        "https://www.irs.gov/instructions/i1040sc",
        "https://www.irs.gov/instructions/i1040sf",
        "https://www.irs.gov/pub/irs-pdf/f1040sc.pdf",
        "https://www.irs.gov/pub/irs-pdf/f1040sf.pdf",
    )

    def formula(person, period, parameters):
        # Add back the same business expenses deducted from the reported net
        # income. Preserve losses until after expenses have been added back.
        # With no reported expenses, this assumes expenses are zero.
        gross = add(
            person,
            period,
            [
                "total_self_employment_income",
                "farm_operations_income",
                "work_expense",
            ],
        )
        return max_(gross, 0)
