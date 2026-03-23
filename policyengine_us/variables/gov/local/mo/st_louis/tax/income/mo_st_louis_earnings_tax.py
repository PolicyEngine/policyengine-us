from policyengine_us.model_api import *


class mo_st_louis_earnings_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "St. Louis earnings tax"
    documentation = (
        "Net St. Louis earnings tax after optional credits supplied as inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.stlouis-mo.gov/government/departments/collector/"
        "earnings-tax/file-earnings-tax.cfm"
    )

    def formula(tax_unit, period, parameters):
        tax_before_credit = tax_unit("mo_st_louis_earnings_tax_before_credit", period)
        credits = tax_unit.sum(
            tax_unit.members("mo_st_louis_earnings_tax_credit", period)
        )
        return max_(0, tax_before_credit - credits)
