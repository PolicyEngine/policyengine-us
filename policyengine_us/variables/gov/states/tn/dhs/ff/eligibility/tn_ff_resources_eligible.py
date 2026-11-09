from policyengine_us.model_api import *


class tn_ff_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Tennessee Families First resources eligible"
    definition_period = MONTH
    reference = "https://publications.tnsosfiles.com/rules/1240/1240-01/1240-01-50.20081124.pdf#page=1"
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Inputs are stored as float32, so compare whole cents with the limit.
        countable_resources = round_to_cents(
            spm_unit("tn_ff_countable_resources", period)
        )
        p = parameters(period).gov.states.tn.dhs.ff.resources
        return countable_resources <= p.limit
