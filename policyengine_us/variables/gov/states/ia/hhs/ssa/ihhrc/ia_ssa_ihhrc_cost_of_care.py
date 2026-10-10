from policyengine_us.model_api import *


class ia_ssa_ihhrc_cost_of_care(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA in-home health-related care monthly cost"
    unit = USD
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.177.pdf#page=2"
    )

    def formula(person, period, parameters):
        # Iowa pays the eligible service cost above client participation, up
        # to the per-person max payment of $480.55 (IAC 441—177.10(3); Iowa
        # HHS 2026 standards). Actual care cost is a per-recipient input we
        # do not track at the moment. When arrangement is known to be IHHRC
        # but cost is unavailable, impute the cap so the supplement is not
        # falsely zeroed; users can override with actual care-cost data.
        p = parameters(period).gov.states.ia.hhs.ssa.ihhrc
        arrangement = person("ia_ssa_living_arrangement", period)
        in_ihhrc = arrangement == arrangement.possible_values.IHHRC
        return where(in_ihhrc, p.max_cost_single, 0)
