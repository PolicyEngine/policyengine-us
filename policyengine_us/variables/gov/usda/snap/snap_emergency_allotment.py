from policyengine_us.model_api import *


class snap_emergency_allotment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "SNAP emergency allotment"
    label = "SNAP emergency allotment"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = USD

    def formula(spm_unit, period, parameters):
        # Save time by only recalculating the EA parameters for each month,
        # rather than the whole parameter tree for each month.
        p = parameters.gov.usda.snap.emergency_allotment(period)
        if not p.allowed:
            return 0
        # Federal SNAP rules are defined in U.S.C Title 7, Chapter 51, which also
        # defines state powers to modify the rules.
        eligible = spm_unit("is_snap_eligible", period)
        max_allotment = spm_unit("snap_max_allotment", period)
        normal_allotment = spm_unit("snap_normal_allotment", period)
        # Calculate emergency allotment, which provides all eligible households the maximum.
        state = spm_unit.household("state_code", period)
        ea_in_effect = p.in_effect[state]
        ea_minimum = p.minimum
        ea_amount_if_in_effect = max_(
            ea_minimum, max_allotment - normal_allotment
        )
        return eligible * ea_in_effect * ea_amount_if_in_effect
