from policyengine_us.model_api import *


class ma_part_a_taxable_dividend_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part A taxable income from dividends"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemptions"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        dividends = add(tax_unit, period, ["dividend_income"])
        part_b_excess_exemption = tax_unit(
            "ma_part_b_excess_exemption", period
        )
        return max_(0, dividends - part_b_excess_exemption)
