from openfisca_us.model_api import *


class snap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Final SNAP benefit amount, equal to net income minus food contribution"
    label = "SNAP"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = USD

    def formula(spm_unit, period, parameters):
        # Federal SNAP rules are defined in U.S.C Title 7, Chapter 51, which also
        # defines state powers to modify the rules.
        eligible = spm_unit("is_snap_eligible", period)
        expected_contribution = spm_unit("snap_expected_contribution", period)
        max_allotment = spm_unit("snap_max_allotment", period)
        normal_allotment = max_allotment - expected_contribution
        min_allotment = spm_unit("snap_min_allotment", period)
        allotment_if_eligible = max_(min_allotment, normal_allotment)
        # Calculate emergency allotment, which provides all eligible households the maximum.
        ea = parameters(period).usda.snap.emergency_allotment
        state = spm_unit("state", period)
        ea_in_effect = ea.in_effect[state]
        ea_minimum = ea.minimum[state]
        ea_amount_if_in_effect = max_(
            ea_minimum, max_allotment - allotment_if_eligible
        )
        ea_amount = ea_in_effect * ea_amount_if_in_effect
        return eligible * (allotment_if_eligible + ea_amount)
