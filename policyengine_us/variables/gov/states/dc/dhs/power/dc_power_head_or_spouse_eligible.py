from policyengine_us.model_api import *


class dc_power_head_or_spouse_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible for DC Program on Work, Employment, and Responsibility (POWER)"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.72",
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.72a",
    )
    defined_for = "is_tax_unit_head_or_spouse"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.dhs.power.age_threshold
        spm_unit = person.spm_unit
        is_parent = person("is_parent", period)
        is_pregnant = person("is_pregnant", period)
        age = person("monthly_age", period)

        # Parent of a minor child with incapacitated household member (includes self)
        # Covers both 4-205.72(b)(2) and 4-205.72a(a)(1)(A)
        has_incapable_of_self_care = spm_unit.any(
            person("is_incapable_of_self_care", period)
        )
        has_minor_child = spm_unit.any(person("dc_pap_eligible_child", period))
        parent_with_incapacitated = (
            is_parent & has_minor_child & has_incapable_of_self_care
        )

        # Parent of a minor child and experienced domestic violence (4-205.72a (a)(2)(A))(not modeled)
        # Pregnant or parenting teen under 19 (4-205.72a(a)(3))
        teen_parent = (is_pregnant | is_parent) & (age < p.younger)

        # Parent or caretaker who is 60 years of age or older (4-205.72a (a)(5))

        return parent_with_incapacitated | teen_parent | (age >= p.older)
