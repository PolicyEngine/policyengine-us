from policyengine_us.model_api import *


class de_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Delaware TANF resources eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4002"
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Per DSSM 4002: Resource limit is $10,000
        p = parameters(period).gov.states.de.dhss.tanf
        # Inputs are stored as float32, so compare whole cents with the limit.
        resources = round_to_cents(spm_unit("spm_unit_cash_assets", period.this_year))

        return resources <= p.resource_limit
