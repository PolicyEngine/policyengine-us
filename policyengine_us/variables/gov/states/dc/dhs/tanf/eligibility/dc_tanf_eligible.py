from policyengine_us.model_api import *


class dc_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for DC Temporary Assistance for Needy Families (TANF)"
    definition_period = MONTH
    reference = "https://dhs.dc.gov/service/tanf-district-families"
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        # Financial/categorical eligibility is distinct from the continuing-case
        # work sanction. The applicant-side orientation / IRP state is not observed
        # in CPS, so we keep cash eligibility on the basic requirements and model
        # work noncompliance separately as a benefit reduction for enrolled cases.
        return spm_unit("dc_tanf_basic_eligibility_requirements", period)
