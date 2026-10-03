from policyengine_us.model_api import *


class sc_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "South Carolina LIHEAP eligible household size"
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = "https://oeo.sc.gov/managedsites/prd/oeo/documents/WAP%202026%20State%20Plan.pdf#page=23"

    def formula(spm_unit, period, parameters):
        # This agency plan expressly attributes the size exclusion, while
        # retaining all members' income, to South Carolina LIHEAP guidance.
        return spm_unit.sum(spm_unit.members("is_citizen_or_legal_immigrant", period))
