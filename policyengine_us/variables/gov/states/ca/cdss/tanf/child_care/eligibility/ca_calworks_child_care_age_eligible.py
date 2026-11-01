from policyengine_us.model_api import *


class ca_calworks_child_care_age_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Child Care SPMUnit Age Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/child-care/overview.html"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        child_age_eligible = person("ca_calworks_child_care_child_age_eligible", period)

        return spm_unit.any(child_age_eligible)
