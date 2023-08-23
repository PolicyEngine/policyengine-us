from policyengine_us.model_api import *


class de_net_income(Variable):
    value_type = float
    entity = Person
    label = "Delaware net income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=7"
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=11"
        "https://casetext.com/statute/delaware-code/title-30-state-taxes/part-ii-income-inheritance-and-estate-taxes/chapter-11-personal-income-tax/subchapter-ii-resident-individuals/section-1109-itemized-deductions-for-application-of-this-section-see-66-del-laws-c-86-section-8"
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        gross_income = person("de_gross_income", period)
        income_adjustments = person("de_income_adjustments", period)
        net_income = gross_income - income_adjustments
        # allocate any dependent net_income to tax unit head
        is_dependent = person("is_tax_unit_dependent", period)
        sum_dep_net_income = person.tax_unit.sum(is_dependent * net_income)
        is_head = person("is_tax_unit_head", period)
        return ~is_dependent * net_income + is_head * sum_dep_net_income
