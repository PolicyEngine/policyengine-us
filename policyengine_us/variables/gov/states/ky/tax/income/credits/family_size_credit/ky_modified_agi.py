from policyengine_us.model_api import *


class ky_modified_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky modified adjusted gross income for the family size tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=22"
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        fed_agi = tax_unit("adjusted_gross_income", period)
        # Lump sum distributions which are not included in federal AGI are added to the federal AGI
        # Tax exempt interest from municipal bonds (non-Kentucky) is also added but excluded in this calculation
        tax_exempt_lump_sum = tax_unit(
            "form_4972_lumpsum_distributions", period
        )
        total_fed_agi = fed_agi + tax_exempt_lump_sum
        ky_agi = add(tax_unit, period, ["ky_agi"])
        # Lump sum distributions which are not included in federal AGI are added to the state AGI
        total_ky_agi = ky_agi + tax_exempt_lump_sum
        return max_(total_fed_agi, total_ky_agi)
