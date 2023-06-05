from policyengine_us.model_api import *


class az_blind_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona blind exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.exemptions

        blind_head = tax_unit("blind_head", period)
        head_eligible = (blind_head).astype(int)

        blind_spouse = tax_unit("blind_spouse", period)
        spouse_eligible = (blind_spouse).astype(int)

        return (head_eligible + spouse_eligible) * p.blind
