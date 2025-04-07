from policyengine_us.model_api import *


class mo_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Sum of itemized deductions applicable to Missouri taxable income calculation"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-A_2021.pdf",
        "https://dor.mo.gov/forms/4711_2021.pdf#page=11",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.141&bid=7212",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mo.tax.income
        deduction_value = add(tax_unit, period, p.deductions.itemized)
        net_state_income_taxes = tax_unit("mo_net_state_income_taxes", period)
        return max_(0, deduction_value - net_state_income_taxes)
