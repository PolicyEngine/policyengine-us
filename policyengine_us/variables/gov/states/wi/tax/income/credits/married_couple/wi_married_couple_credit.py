from policyengine_us.model_api import *


class wi_married_couple_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin married couple credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=4"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=21"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=4"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=21"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        fstatus = tax_unit("filing_status", period)
        eligible = fstatus == fstatus.possible_values.JOINT
        p = parameters(period).gov.states.wi.tax.income.credits
        income = add(tax_unit.members, period, p.married_couple.income_sources)
        is_head = tax_unit.members("is_tax_unit_head", period)
        is_spouse = tax_unit.members("is_tax_unit_spouse", period)
        head_income = tax_unit.sum(is_head * income)
        spouse_income = tax_unit.sum(is_spouse * income)
        lower_income = min_(head_income, spouse_income)
        return min_(
            eligible * lower_income * p.married_couple.rate,
            p.married_couple.max,
        )
