from policyengine_us.model_api import *


class self_employment_gross_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Gross self-employment income"
    reference = (
        "https://www.irs.gov/instructions/i1040sc",
        "https://www.irs.gov/instructions/i1040sf",
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
