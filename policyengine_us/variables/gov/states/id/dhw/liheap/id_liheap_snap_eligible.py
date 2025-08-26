from policyengine_us.model_api import *


class id_liheap_snap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP SNAP presumptive eligibility"
    definition_period = YEAR
    reference = "https://www.eicap.org/our-programs/family-services/energy-assistance-winter-heating-program/"
    documentation = "SNAP participants are presumed eligible for LIHEAP"

    def formula(spm_unit, period, parameters):
        # Check if the household receives SNAP benefits
        snap_benefits = spm_unit("snap", period)
        return snap_benefits > 0