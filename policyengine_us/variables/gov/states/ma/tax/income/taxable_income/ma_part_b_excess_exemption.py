from policyengine_us.model_api import *


class ma_part_b_excess_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part B excess exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemption"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        taxinc_before_exemption = tax_unit(
            "ma_part_b_taxable_income_before_exemption", period
        )
        total_exemption = tax_unit(
            "ma_part_b_taxable_income_exemption", period
        )
        return max_(0, total_exemption - taxinc_before_exemption)
