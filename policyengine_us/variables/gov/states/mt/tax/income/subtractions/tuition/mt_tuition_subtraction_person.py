from policyengine_us.model_api import *


class mt_tuition_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = "Montana tuition subtraction"
    definition_period = YEAR
    reference = "https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.subtractions.tuition
        individual_contributions = person(
            "investment_in_529_plan_indv", period
        )
        p = parameters(period).gov.states.mt.tax.income.subtractions.tuition
        capped_contributions = min_(individual_contributions, p.cap)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return capped_contributions * head_or_spouse
