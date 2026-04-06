from policyengine_us.model_api import *


class il_hbwd_employment_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities employment eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Per § 120.510(l)(1), employment is verified by current payment
        # under FICA or IMRF. We use earned income as a proxy for
        # employment with FICA contributions.
        #
        # Not currently modeled:
        # - § 120.510(l)(2)(A): Future employment exception (60 days)
        # - § 120.510(l)(2)(B): Medical inability grace period (90 days)
        # - § 120.510(l)(2)(C): Job loss grace period (30 days)
        earned_income = person("il_hbwd_gross_earned_income", period)
        return earned_income > 0
