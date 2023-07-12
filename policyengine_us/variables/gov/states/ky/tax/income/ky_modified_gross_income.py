from policyengine_us.model_api import *


class ky_modified_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky modified gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    
    def formula(tax_unit, period, parameters):
        household_size = tax_unit("tax_unit_size", period)
        return parameters(period).gov.states.ky.tax.income.modified_gross_income.sources.calc(household_size)