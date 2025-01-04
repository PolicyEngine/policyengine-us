from policyengine_us.model_api import *


class ny_college_tuition_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY college tuition credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (t)
    defined_for = "ny_college_tuition_credit_eligible"

    def formula(tax_unit, period, parameters):
        tuition = tax_unit("ny_allowable_college_tuition_expenses", period)
        p = parameters(period).gov.states.ny.tax.income.credits.college_tuition
        # Apply a tiered rate structure.
        amount_pre_percentage = p.rate.calc(tuition)
        return amount_pre_percentage * p.applicable_percentage
