from policyengine_us.model_api import *


class ma_part_c_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part C taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemptions"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        part_c_agi = tax_unit("ma_part_c_agi", period)
        cg_excess_exemption = tax_unit("ma_part_a_cg_excess_exemption", period)
        return max_(0, part_c_agi - cg_excess_exemption)
