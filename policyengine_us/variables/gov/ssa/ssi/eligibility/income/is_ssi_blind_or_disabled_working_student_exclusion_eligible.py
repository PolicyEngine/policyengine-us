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
        # "Blind or disabled" takes SSA's own meaning here: the exclusion
        # applies to a blind or disabled SSI claimant (20 CFR 416.1112(c)(3)),
        # so the SSI disability criteria govern rather than the generic
        # disability flag. The substantial gainful activity screen is left
        # out: it is an initial-entitlement test, and section 1619(a)
        # recipients keep SSI status while earning above SGA, so the
        # exclusion (also used by MSP and Medicaid income methodologies)
        # must not vanish above the SGA threshold.
        is_blind = person("is_blind", period)
        meets_disability_criteria = person("meets_ssi_disability_criteria", period)
        demographic_eligible = is_blind | meets_disability_criteria
        under_age_limit = person("age", period) < p.age_limit
        eligible_student = under_age_limit & person("is_full_time_student", period)
        return eligible_student & demographic_eligible
