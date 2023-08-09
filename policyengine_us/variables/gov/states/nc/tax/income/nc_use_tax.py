from policyengine_us.model_api import *


class nc_use_tax(variable):
    value_type = float
    entity = TaxUnit
    label = "NC use tax"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states.nc.tax.use_tax.without_record
        return p.amount.calc(agi) + (p.rate.calc(agi) * agi)
