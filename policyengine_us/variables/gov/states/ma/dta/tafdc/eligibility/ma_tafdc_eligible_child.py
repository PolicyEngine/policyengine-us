from policyengine_us.model_api import *


class ma_tafdc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) eligible child"
    definition_period = YEAR
    reference = "https://www.masslegalservices.org/content/5-how-young-must-children-be-qualify"
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(
            period
        ).gov.states.ma.dta.tafdc.eligibility.age_threshold
        in_school = person("is_in_k12_school", period)
        age_under_19 = age < p.child_under_19
        return age < p.child | (in_school & age_under_19)

