from policyengine_us.model_api import *


class wv_works_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "West Virginia WV Works resources eligible"
    definition_period = MONTH
    reference = "https://dhhr.wv.gov/bcf/Services/familyassistance/Documents/726/726%20ch11_1.pdf"
    defined_for = StateCode.WV

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.works.resources
        # spm_unit_assets is a YEAR variable
        countable_resources = spm_unit("spm_unit_assets", period.this_year)
        return countable_resources <= p.limit
