from policyengine_us.model_api import *


class is_ssi_blind_or_disabled_working_student_exclusion_eligible(Variable):
    value_type = float
    entity = Person
    label = "Eligible for SSI blind or disabled working student earned income exclusion"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1112#c_3"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.ssa.ssi.income.exclusions.blind_or_disabled_working_student
        is_blind = person("is_blind", period)
        is_disabled = person("is_disabled", period)
        demographic_eligible = is_blind | is_disabled
        under_age_limit = person("age", period) < p.age_limit
        eligible_student = under_age_limit & person(
            "is_full_time_student", period
        )
        return eligible_student & demographic_eligible
