from policyengine_us.model_api import *


class ny_college_tuition_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York itemized deduction for college tuition expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",  # (d)(4)
        "https://www.nysenate.gov/legislation/laws/TAX/606",  # (t)
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.tax.income.deductions.itemized.college_tuition
        allowable_expenses = tax_unit(
            "ny_allowable_college_tuition_expenses", period
        )
        return allowable_expenses * p.applicable_percentage
