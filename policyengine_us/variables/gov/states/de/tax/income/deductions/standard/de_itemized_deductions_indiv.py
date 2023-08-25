from policyengine_us.model_api import *


class de_itemized_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Delaware itemized deductions for individual couples"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=7"
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=11"
        "https://casetext.com/statute/delaware-code/title-30-state-taxes/part-ii-income-inheritance-and-estate-taxes/chapter-11-personal-income-tax/subchapter-ii-resident-individuals/section-1109-itemized-deductions-for-application-of-this-section-see-66-del-laws-c-86-section-8"
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        unit_deds = person.tax_unit("de_itemized_deductions_unit", period)
        return unit_deds * person("de_prorate_fraction", period)