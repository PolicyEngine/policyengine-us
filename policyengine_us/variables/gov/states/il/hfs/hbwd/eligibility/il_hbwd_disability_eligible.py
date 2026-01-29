from policyengine_us.model_api import *


class il_hbwd_disability_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities disability eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Must meet Social Security Administration's definition of disability.
        # Per DB101 Illinois "For HBWD, Social Security's disability
        # rules related to earned income do not apply" - so we use is_disabled
        # (medical definition) instead of is_ssi_disabled (which includes SGA test).
        # See: https://il.db101.org/il/programs/health_coverage/how_health/program2b.htm
        is_disabled = person("is_disabled", period.this_year)
        # Or currently receiving SSDI
        receives_ssdi = person("social_security_disability", period) > 0
        return is_disabled | receives_ssdi
