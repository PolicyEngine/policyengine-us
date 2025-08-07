from policyengine_us.model_api import *


class ssi_blind_or_disabled_working_student_exclusion(Variable):
    value_type = float
    entity = Person
    label = "SSI blind or disabled working student earned income exclusion"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1112#c_3"
    defined_for = "is_ssi_blind_or_disabled_working_student_exclusion_eligible"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.ssa.ssi.income.exclusions.blind_or_disabled_working_student
        monthly_earned_income = (
            person("ssi_earned_income", period) / MONTHS_IN_YEAR
        )
        max_amount = min_(p.amount, monthly_earned_income) * MONTHS_IN_YEAR
        return min_(max_amount, p.cap)
