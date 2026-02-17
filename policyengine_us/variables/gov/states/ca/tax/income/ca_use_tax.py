from policyengine_us.model_api import *


class ca_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA Use Tax"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2025/2025-540-instructions.html"
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        income = tax_unit("ca_agi", period)
        p = parameters(period).gov.states.ca.tax.income.use_tax
        # Compute main amount, a dollar amount based on CA AGI.
        main_amount = p.main.calc(income)
        # Switches to a percentage of income above the top main threshold.
        additional_amount = p.additional.calc(income) * income
        return main_amount + additional_amount
