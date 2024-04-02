from policyengine_us.model_api import *


class ca_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the California CalWORKs"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        financial_eligibile = spm_unit("ca_tanf_financial_eligible", period)
        resources_eligible = spm_unit("ca_tanf_resources_eligible", period)
        vehicle_value_eligible = spm_unit(
            "ca_tanf_vehicle_value_eligible", period
        )

        return (
            demographic_eligible
            & financial_eligibile
            & resources_eligible
            & vehicle_value_eligible
        )
