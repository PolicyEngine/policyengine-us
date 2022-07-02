from openfisca_us.model_api import *


class md_aged_blind_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD aged blind exemptions"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        blind = parameters(period).gov.states.md.tax.income.exemptions.blind
        # Count number of is_blind from tax_unit
        blind_head = tax_unit("blind_head", period) * 1
        blind_spouse = tax_unit("blind_spouse", period) * 1

        return (blind_head + blind_spouse) * blind

    # Get blind exemption parameter
