from policyengine_us.model_api import *


class la_blind_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Louisiana blind exemption for each individual"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.revenue.louisiana.gov/taxforms/6935(11_02)F.pdf#page=1",
        "https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf#page=2",
    ]
    # Even though the tax computation worksheet refers "blind exemption" as credits, the instructions for
    # preparing tax form line 6a-6b specifies it as exemption. (the legal code also mentions deaf and totally disabled conditions,
    # but they are not mentioned either in the tax computation worksheet or tax form.)
    defined_for = "la_receives_blind_exemption"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.la.tax.income.exemptions
        blind = person("is_blind", period).astype(int)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        blind_head_or_spouse = head_or_spouse & blind
        return blind_head_or_spouse * p.blind
