from policyengine_us.model_api import *


class ca_state_supplement_payment_standard(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California SSI state supplement eligibility"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        meets_resource_test = spm_unit("meets_ssi_resource_test", period)
        aged_blind_disabled = spm_unit("is_ssi_aged_blind_disabled", period)
        is_qualified_noncitizen = person("is_ssi_qualified_noncitizen", period)
        immigration_status = person("immigration_status", period)
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )
