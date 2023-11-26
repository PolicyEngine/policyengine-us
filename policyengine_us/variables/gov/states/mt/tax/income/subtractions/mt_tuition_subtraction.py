from policyengine_us.model_api import *


class mt_tuition_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana tuition subtraction"
    definition_period = YEAR
    reference = "https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.mt.tax.income.subtractions.tuition
        # investment_in_529_plan_indv = add(
        #     person, period, ["investment_in_529_plan"]
        # )
        investment_in_529_plan_indv = person.tax_unit(
            "investment_in_529_plan", period
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        head_or_spouse_inv = investment_in_529_plan_indv * head_or_spouse
        total_inv = where(
            head_or_spouse, head_or_spouse_inv, investment_in_529_plan_indv
        )
        capped_inv = min_(total_inv, p.cap)
        return tax_unit.sum(capped_inv)
