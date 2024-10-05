from policyengine_us.model_api import *


class ma_part_a_div_excess_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A dividends excess exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemptions"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        dividends = add(tax_unit, period, ["dividend_income"])
        partb_excess_exemption = tax_unit("ma_part_b_excess_exemption", period)
        return max_(0, partb_excess_exemption - dividends)
