from policyengine_us.model_api import *


class ssi_blind_or_disabled_working_student(Variable):
    value_type = float
    entity = Person
    label = "SSI blind or disabled student earned income exclusion"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1112#c_3"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.ssa.ssi.income.exclusions.blind_or_disabled_student
        is_blind = person("is_blind", period)
        is_disabled = person("is_disabled", period)
        demographic_eligible = is_blind | is_disabled
        under_age_limit = person("age", period) <= p.age_limit
        eligible_student = under_age_limit & person(
            "is_full_time_student", period
        )
        program_eligible = eligible_student & demographic_eligible
        monthly_earned_income = (
            person("ssi_earned_income", period) / MONTHS_IN_YEAR
        )
        max_amount = min_(p.amount, monthly_earned_income) * MONTHS_IN_YEAR
        capped_amount = min_(max_amount, p.cap)
        return where(program_eligible, capped_amount, 0)
