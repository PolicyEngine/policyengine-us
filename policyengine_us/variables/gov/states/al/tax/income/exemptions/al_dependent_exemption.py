from policyengine_us.model_api import *


class al_dependent_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama dependent exemption"
    unit = USD
    # The Code of Alabama 1975 Section 40-18-19 (a)(9).
    documentation = "https://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/Coatoc.htm"
    definition_period = YEAR
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.exemptions
        agi = tax_unit("adjusted_gross_income", period)
        return p.dependent.calc(agi)
