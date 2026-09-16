from policyengine_us.model_api import *


class hi_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii CCAP countable monthly income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.HI
    reference = (
        # HAR 17-798.3-10 (counted sources) and -11 (exclusions), eff.
        # 2021-08-06; "gross income" is defined in 17-798.3-2 as all
        # non-excluded earned and unearned income.
        "https://humanservices.hawaii.gov/bessd/files/2021/09/CHAPTER-17-798.3-Child-Care-Payments.pdf#page=24",
        # Superseded HAR 17-798.2-10 and -11, with the same source list,
        # exclusions, and 17-798.2-2 definition.
        "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=19",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.bessd.ccap
        # Monthly gross income from all counted sources (HAR 17-798.3-10(b);
        # identically 17-798.2-10(b) before August 6, 2021).
        gross = add(spm_unit, period, p.income.countable_income.sources)
        # HAR 17-798.3-11(8) (17-798.2-11(8) before August 6, 2021): exclude
        # the earnings of minor household members who are at least half-time
        # students. is_full_time_student is the available proxy for a
        # minor's at-least-half-time enrollment.
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
