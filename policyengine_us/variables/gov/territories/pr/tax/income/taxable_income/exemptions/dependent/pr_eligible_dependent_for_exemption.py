from policyengine_us.model_api import *


class pr_eligible_dependent_for_exemption(Variable):
    value_type = bool
    entity = Person
    label = "Puerto Rico eligible dependent for dependent exemption"
    reference = "https://hacienda.pr.gov/sites/default/files/inst_individuals_2023.pdf#page=28"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR

    def formula(person, period, parameters):
        student_eligible = person("pr_exemptions_is_eligible_student", period)
        non_student_eligible = person(
            "pr_exemptions_is_eligible_nonstudent", period
        )
        return student_eligible | non_student_eligible
