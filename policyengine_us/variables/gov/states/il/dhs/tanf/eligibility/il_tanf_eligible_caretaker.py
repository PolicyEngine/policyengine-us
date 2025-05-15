from policyengine_us.model_api import *


class il_tanf_eligible_caretaker(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Temporary Assistance for Needy Families (TANF) eligible caretaker"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.67"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf.age_threshold
        has_eligible_child = (
            person.spm_unit.sum(person("il_tanf_eligible_child", period)) > 0
        )

        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_pregnant = person("is_pregnant", period)
        has_eligible_caretaker = is_head_or_spouse & is_pregnant

        age = person("monthly_age", period)
        under_age_18 = age < p.minor_parent_18
        is_married = person.spm_unit("spm_unit_is_married", period)
        special_minor_parent = is_head_or_spouse & under_age_18 & ~is_married
        # special minor parent only have 6 months benefit until they turn 18
        return has_eligible_child | has_eligible_caretaker
