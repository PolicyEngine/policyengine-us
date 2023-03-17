from policyengine_us.model_api import *


class ks_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "KS Use Tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    """
    def formula(tax_unit, period, parameters):
        income = tax_unit("ks_agi", period)
        p = parameters(period).gov.states.ca.tax.income.use_tax
        # Compute main amount, a dollar amount based on KS AGI.
        main_amount = p.main.calc(income)
        # Switches to a percentage of income above the top main threshold.
        additional_amount = p.additional.calc(income) * income
        return main_amount + additional_amount
    """
