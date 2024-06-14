from policyengine_us.model_api import *


class nj_snap_min_allotment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "NJ minimum snap payment"
    label = "NJ minimum snap payment"
    reference = (
        "https://www.nj.gov/humanservices/njsnap/apply/eligibility/"
    )
    unit = USD
    defined_for = StateCode.NJ

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.usda.snap.temporary_local_benefit.nj
        base_benefit = spm_unit('snap_reported', period)
        if base_benefit < p.amount:
            return p.amount
        else:
            return 0