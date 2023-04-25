from policyengine_us.model_api import *


class ma_part_a_cg_excess_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A (short-term) capital gains excess exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemptions"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        part_a_agi = tax_unit("ma_part_a_agi", period)
        dividends = add(tax_unit, period, ["dividend_income"])
        stcg_agi = part_a_agi - dividends
        div_excess_exemption = tax_unit(
            "ma_part_a_div_excess_exemption", period
        )
        return max_(0, div_excess_exemption - stcg_agi)
