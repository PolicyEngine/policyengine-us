from policyengine_us.model_api import *


class al_dependent_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama dependent exemption"
    unit = USD
    # The Code of Alabama 1975 Section 40-18-19 (a)(9).
    documentation = "https://alison.legislature.state.al.us/code-of-alabama"
    definition_period = YEAR
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.al.tax.income.exemptions
        al_agi = tax_unit("al_agi", period)
        dependents = tax_unit("tax_unit_dependents", period)
        # The amount drops only once AGI is over a threshold ("equal to or
        # less than" $20,000 or $50,000 keeps $1,000).
        exemption_per_dependent = p.dependent.calc(al_agi, right=True)
        return dependents * exemption_per_dependent
