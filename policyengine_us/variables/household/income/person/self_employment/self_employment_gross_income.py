from policyengine_us.model_api import *


class self_employment_gross_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Gross self-employment income"
    documentation = (
        "Gross income after cost of goods sold and before other business "
        "expenses (tax year 2025 Schedule C line 7 and Schedule F line 9), "
        "reconstructed from regular, SSTB, and farm net income plus "
        "self_employment_expense. Excludes separately reported partnership "
        "earnings. The result is floored at the sum of the three net sources "
        "individually floored at zero; this modeling fallback can differ from "
        "tax-reported gross income and is not an IRS rule. Non-farm net income "
        "includes labor-supply responses."
    )
    reference = (
        "https://www.irs.gov/pub/irs-prior/f1040sc--2025.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/f1040sf--2025.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/f1040sf--2025.pdf#page=2",
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
