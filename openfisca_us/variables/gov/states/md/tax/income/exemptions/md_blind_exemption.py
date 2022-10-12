from policyengine_us.model_api import *


class md_blind_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD blind exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://govt.westlaw.com/mdc/Document/NF59A76006EA511E8ABBEE50DE853DFF4?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        amount = parameters(period).gov.states.md.tax.income.exemptions.blind
        # Count number of is_blind from tax_unit
        blind_head = tax_unit("blind_head", period).astype(int)
        blind_spouse = tax_unit("blind_spouse", period) * 1
        return (blind_head + blind_spouse) * amount
