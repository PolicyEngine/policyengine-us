from openfisca_us.model_api import *


class is_md_income_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "MD income tax exempt"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        agi = tax_unit("md_agi", period)
        threshold = tax_unit("md_income_tax_exemption_threshold", period)
        return agi <= threshold
