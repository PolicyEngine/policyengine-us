from policyengine_us.model_api import *


class la_dependents_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana qualified dependents exemption"
    reference = [
        "https://www.revenue.louisiana.gov/taxforms/6935(11_02)F.pdf#page=1",
        "https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf#page=2",
    ]
    # Even though the tax computation worksheet refers "dependent exemption" as credits, the instructions for
    # preparing tax form line 6a-6b specifies it as exemption.
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        dependents = tax_unit("tax_unit_dependents", period)
        p = parameters(period).gov.states.la.tax.income.exemptions
        return dependents * p.dependent
