from policyengine_us.model_api import *


class hi_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii CCAP countable monthly income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=19"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.bessd.ccap
        # Monthly gross income from all counted sources (HAR 17-798.2-10(b)).
        gross = add(spm_unit, period, p.income.countable_income.sources)
        # HAR 17-798.2-11(8): exclude the earnings of minor household members
        # who are at least half-time students. is_full_time_student is the
        # available proxy for a minor's at-least-half-time enrollment.
        person = spm_unit.members
        is_minor_student = (
            person("age", period.this_year) < p.age.minor_age_limit
        ) & person("is_full_time_student", period.this_year)
        minor_student_earnings = spm_unit.sum(
            is_minor_student
            * (
                person("employment_income", period)
                + person("self_employment_income", period)
            )
        )
        return gross - minor_student_earnings
