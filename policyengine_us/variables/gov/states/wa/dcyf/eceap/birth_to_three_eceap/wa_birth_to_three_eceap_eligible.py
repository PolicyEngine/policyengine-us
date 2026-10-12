from policyengine_us.model_api import *


class wa_birth_to_three_eceap_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Washington Birth to Three ECEAP"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = "https://app.leg.wa.gov/RCW/default.aspx?cite=43.216.578"

    def formula(person, period, parameters):
        # RCW 43.216.578 differs from RCW 43.216.505: Birth to Three's only
        # categorical pathway is Basic Food (federal SNAP or state FAP); it
        # does NOT include the homeless or IEP pathways from standard ECEAP.
        # FAP serves SNAP-ineligible legal immigrants and is not modeled
        # separately at the moment, so we use SNAP eligibility or an
        # explicitly provided SNAP benefit as the proxy for receipt.
        #
        # Early Head Start coordination: DCYF ECEAP Performance Standards
        # PAO-38(10) prohibit simultaneous enrollment in B-3 ECEAP and Early
        # Head Start, but we do not subtract early_head_start receipt here
        # because early_head_start in PolicyEngine is an imputed state-average
        # value rather than a per-child enrollment signal — subtracting it
        # would understate B-3 ECEAP for kids the model probabilistically
        # imputes as taking up Early Head Start. To avoid double-counting
        # at the aggregate level, wa_birth_to_three_eceap is intentionally
        # omitted from household_benefits and household_state_benefits.
        age_eligible = person("wa_birth_to_three_eceap_age_eligible", period)
        income_eligible = person("wa_birth_to_three_eceap_income_eligible", period)
        snap_eligible = person.spm_unit("is_snap_eligible", period)
        snap_receipt = (person.spm_unit("snap", period) > 0) | (
            add(person.spm_unit, period, ["receives_snap"]) > 0
        )
        return age_eligible & (income_eligible | snap_eligible | snap_receipt)
