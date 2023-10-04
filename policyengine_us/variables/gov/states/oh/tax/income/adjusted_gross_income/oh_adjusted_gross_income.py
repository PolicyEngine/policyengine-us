from policyengine_us.model_api import *


class oh_adjusted_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Alternative Adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20"

    def formula(tax_unit, period, parameters):
        gross_income = add(tax_unit, period, ["oh_irs_gross_income"])
        above_the_line_deductions = tax_unit(
            "above_the_line_deductions", period
        )
        agi = gross_income - above_the_line_deductions
        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            agi += add(tax_unit, period, ["basic_income"])
        return agi
