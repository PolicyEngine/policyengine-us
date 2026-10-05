from policyengine_us.model_api import *


class ca_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the California CalWORKs based on the available resources"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/calworks/property/property.html"

    def formula(spm_unit, period, parameters):
        resources = spm_unit("ca_tanf_resources", period)
        limit = spm_unit("ca_tanf_resources_limit", period)
        return resources <= limit
