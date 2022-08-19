from openfisca_us.model_api import *


class md_total_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD total personal exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Get md_personal_exemption from tax_unit multiplied by tax_unit_size
        md_personal_exemption = tax_unit("md_personal_exemption", period)
        tax_unit_size = tax_unit("tax_unit_size", period)
        return md_personal_exemption * tax_unit_size
