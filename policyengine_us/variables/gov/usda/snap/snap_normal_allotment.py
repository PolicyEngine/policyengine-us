from policyengine_us.model_api import *


class snap_normal_allotment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "Normal SNAP benefit amount, equal to net income minus food contribution"
    label = "SNAP normal allotment"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = USD
    defined_for = "is_snap_eligible"

    def formula(spm_unit, period, parameters):
        # Federal SNAP rules are defined in U.S.C Title 7, Chapter 51, which
        # also defines state powers to modify the rules.
        expected_contribution = spm_unit("snap_expected_contribution", period)
        max_allotment = spm_unit("snap_max_allotment", period)
        normal_allotment = max_allotment - expected_contribution
        min_allotment = spm_unit("snap_min_allotment", period)
        return max_(min_allotment, normal_allotment)
