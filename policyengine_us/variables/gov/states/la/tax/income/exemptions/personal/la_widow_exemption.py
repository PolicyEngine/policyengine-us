from policyengine_us.model_api import *


class la_surviving_spouse_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana qualifying surviving spouse exemption"
    reference = (
        "https://www.revenue.louisiana.gov/taxforms/6935(11_02)F.pdf#page=1"
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_surviving_spouse = tax_unit.any(
            person("is_surviving_spouse", period)
        )
        p = parameters(period).gov.states.la.tax.income.exemptions
        return is_surviving_spouse * p.surviving_spouse
