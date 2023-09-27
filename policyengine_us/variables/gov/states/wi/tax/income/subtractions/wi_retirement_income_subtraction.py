from policyengine_us.model_api import *


class wi_retirement_income_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin retirement income subtraction from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB.pdf"
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB-inst.pdf#page=9"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSBf.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSB-Inst.pdf#page=7"
    )
    defined_for = "wi_retirement_income_subtraction_agi_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income
        psri = p.subtractions.retirement_income
        person = tax_unit.members
        age = person("age", period)
        age_eligible = age >= psri.min_age
        retirement_income = person("taxable_pension_income", period)
        head_or_spouse = ~person("is_tax_unit_dependent", period)
        uncapped_retinc = retirement_income * age_eligible * head_or_spouse
        capped_retinc = min_(psri.max_amount, uncapped_retinc)
        return tax_unit.sum(capped_retinc)
