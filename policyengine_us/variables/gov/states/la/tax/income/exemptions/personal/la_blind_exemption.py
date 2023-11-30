from policyengine_us.model_api import *


class la_blind_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana blind exemption"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.revenue.louisiana.gov/taxforms/6935(11_02)F.pdf#page=1",
        "https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf#page=2",
    ]
    # Even though the tax computation worksheet refers "blind exemption" as credits, the instructions for
    # preparing tax form line 6a-6b specifies it as exemption. (the legal code also mentions deaf and totally disabled conditions,
    # but they are not mentioned either in the tax computation worksheet or tax form.)
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.exemptions.personal
        blind_head = tax_unit("blind_head", period).astype(int)
        blind_spouse = tax_unit("blind_spouse", period).astype(int)
        return (blind_head + blind_spouse) * p.blind
