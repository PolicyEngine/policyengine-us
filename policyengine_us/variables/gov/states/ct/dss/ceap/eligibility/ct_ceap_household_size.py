from policyengine_us.model_api import *


class ct_ceap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Connecticut CEAP household size"
    definition_period = YEAR
    defined_for = StateCode.CT
    # PDF pages 5,9
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/winter-heating-assistance/09012026/ffy-27-liheap-allocation-plan.pdf#page=5"
    # The SPM unit approximates the common energy household.

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        qualified = person("is_citizen_or_legal_immigrant", period)
        member = person("ct_ceap_household_member", period)
        return spm_unit.sum(qualified & member)
