from policyengine_us.model_api import *


class wv_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia personal exemption"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21/"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wv.tax.income.exemptions
        tax_unit_size = tax_unit("tax_unit_size", period)
        return where(
            tax_unit_size == 0, p.base_personal, p.personal * tax_unit_size
        )
