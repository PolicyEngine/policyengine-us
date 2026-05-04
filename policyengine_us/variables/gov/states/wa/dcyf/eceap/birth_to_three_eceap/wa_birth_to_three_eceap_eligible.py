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
        # separately at the moment, so we use SNAP eligibility or reported
        # SNAP receipt as the proxy.
        age_eligible = person("wa_birth_to_three_eceap_age_eligible", period)
        income_eligible = person("wa_birth_to_three_eceap_income_eligible", period)
        snap_eligible = person.spm_unit("is_snap_eligible", period)
        snap_reported = person.spm_unit("snap_reported", period) > 0
        return age_eligible & (income_eligible | snap_eligible | snap_reported)
