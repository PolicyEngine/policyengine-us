from policyengine_us.model_api import *
import numpy as np


class id_tafi(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho Temporary Assistance for Families in Idaho (TAFI)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.248",
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.252",
    )
    defined_for = "id_tafi_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.tanf
        grant_standard = spm_unit("id_tafi_grant_standard", period)
        # Per IDAPA 16.03.08.252: Grant is capped at maximum grant
        # and rounded down to the next lowest dollar
        capped_grant = min_(grant_standard, p.maximum_grant)
        floored_grant = np.floor(max_(capped_grant, 0))
        # Per IDAPA 16.03.08.254: No payment when grant is less than $10
        return where(floored_grant >= 10, floored_grant, 0)
