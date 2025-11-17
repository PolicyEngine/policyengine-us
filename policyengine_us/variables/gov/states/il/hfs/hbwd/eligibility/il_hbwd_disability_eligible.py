from policyengine_us.model_api import *


class il_hbwd_disability_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities disability eligible"
    definition_period = MONTH
    reference = (
        "https://ilga.gov/commission/jcar/admincode/089/089001200I05100R.html",
        "https://hfs.illinois.gov/medicalprograms/hbwd/eligibility.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Must meet Social Security Administration's definition of disability
        is_ssi_disabled = person("is_ssi_disabled", period)
        # Or currently receiving SSDI
        receives_ssdi = person("social_security_disability", period) > 0
        return is_ssi_disabled | receives_ssdi
