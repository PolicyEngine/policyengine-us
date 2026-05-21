from policyengine_us.model_api import *


class az_ccap_copay_exempt(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arizona Child Care Assistance Program copay exempt"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        "https://des.az.gov/sites/default/files/dl/CCA-0229AFY26.pdf#page=1",
        "https://des.az.gov/services/child-and-family/child-care/how-apply-for-child-care-assistance",
        "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=33",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        protective_services = spm_unit.any(
            person("receives_or_needs_protective_services", period.this_year)
        )
        foster_care = spm_unit.any(person("is_in_foster_care", period))
        return tanf_enrolled | protective_services | foster_care
