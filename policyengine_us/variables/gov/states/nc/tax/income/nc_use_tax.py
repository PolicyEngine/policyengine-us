from policyengine_us.model_api import *


class nc_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina use tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states.nc.tax.use_tax
        # Compute base amount, a dollar amount based on NC AGI.
        main_amount = p.base.calc(agi)
        # Switch to a percentage of income above the threshold.
        additional_amount = p.additional.calc(agi) * agi
        return main_amount + additional_amount
