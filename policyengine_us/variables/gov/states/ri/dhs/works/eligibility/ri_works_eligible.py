from policyengine_us.model_api import *


class ri_works_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Rhode Island Works"
    definition_period = MONTH
    reference = (
        "https://rules.sos.ri.gov/Regulations/part/218-20-00-2",
        "https://dhs.ri.gov/programs-and-services/ri-works-program/eligibility-how-apply",
    )
    defined_for = StateCode.RI

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("ri_works_income_eligible", period)
        resource_eligible = spm_unit("ri_works_resource_eligible", period)
        demographic_eligible = (
            spm_unit("is_demographic_tanf_eligible", period) > 0
        )
        return income_eligible & resource_eligible & demographic_eligible
