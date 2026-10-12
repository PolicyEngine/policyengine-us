from policyengine_us.model_api import *


class is_fl_sr_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the Florida School Readiness program"
    definition_period = MONTH
    defined_for = StateCode.FL
    reference = (
        "https://flrules.elaws.us/fac/6m-4.200",
        "https://www.law.cornell.edu/uscode/text/8/1641",
        "https://www.law.cornell.edu/cfr/text/45/98.20",
    )

    def formula(person, period, parameters):
        age_eligible = person("is_fl_sr_age_eligible", period)
        # Immigration eligibility uses the federal CCDF check (8 USC 1641,
        # 45 CFR 98.20); 6M-4.200 does not address immigration.
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
