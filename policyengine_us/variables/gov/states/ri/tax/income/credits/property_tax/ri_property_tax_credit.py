from policyengine_us.model_api import *


class ri_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://webserver.rilin.state.ri.us/Statutes/TITLE44/44-33/44-33-9.htm"
    )
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.credits.property_tax
        agi = tax_unit("adjusted_gross_income", period)
        num_household = tax_unit("tax_unit_size", period)
        credit = where(num_household == 1, p.rate1.calc(agi), p.rate2.calc(agi))
        return min_(credit, p.max_amount)
