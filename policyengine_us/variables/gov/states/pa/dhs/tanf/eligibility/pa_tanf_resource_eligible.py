from policyengine_us.model_api import *


class pa_tanf_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF resource eligibility"
    documentation = "Pennsylvania TANF limits countable resources (assets with cash value) to $1,000 per household."
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Chapter 178, working_references.md"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf

        # Get household assets (SPM unit level variable)
        household_assets = spm_unit("spm_unit_assets", period)

        # Check if assets are below the resource limit
        resource_limit = p.resource_limit
        return household_assets <= resource_limit
