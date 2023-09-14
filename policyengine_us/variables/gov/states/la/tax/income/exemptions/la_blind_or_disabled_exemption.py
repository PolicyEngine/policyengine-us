from policyengine_us.model_api import *


class la_blind_or_disabled_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana blind or disabled exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.louisiana.gov/taxforms/6935(11_02)F.pdf"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        amount = parameters(
            period
        ).gov.states.la.tax.income.exemptions.blind_or_disabled
        blind_head = tax_unit("blind_head", period)
        disabled_head = tax_unit("disabled_head", period)
        head_eligible = (blind_head | disabled_head).astype(int)
        return head_eligible * amount
