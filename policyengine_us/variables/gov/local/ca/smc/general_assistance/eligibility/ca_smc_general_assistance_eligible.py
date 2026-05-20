from policyengine_us.model_api import *


class ca_smc_general_assistance_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for San Mateo County General Assistance"
    definition_period = MONTH
    defined_for = "in_smc"
    reference = "https://www.smcgov.org/media/153295/download?inline=#page=1"

    def formula(spm_unit, period, parameters):
        immigration_eligible = (
            add(
                spm_unit,
                period,
                ["ca_smc_general_assistance_immigration_status_eligible_person"],
            )
            > 0
        )
        return (
            immigration_eligible
            & spm_unit("ca_smc_general_assistance_income_eligible", period)
            & spm_unit("ca_smc_general_assistance_property_eligible", period)
        )
