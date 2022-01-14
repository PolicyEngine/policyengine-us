from openfisca_us.model_api import *


class snap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Final SNAP benefit amount, equal to net income minus food contribution"
    label = "SNAP"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = USD

    def formula(spm_unit, period):
        # Federal SNAP rules are defined in U.S.C Title 7, Chapter 51, which also
        # defines state powers to modify the rules.
        eligible = spm_unit("is_snap_eligible", period)
        expected_contribution = spm_unit("snap_expected_contribution", period)
        max_benefit = spm_unit("snap_max_benefit", period)
        normal_benefit = max_benefit - expected_contribution
        min_benefit = spm_unit("snap_minimum_benefit", period)
        amount_if_eligible = max_(min_benefit, normal_benefit)
        return eligible * amount_if_eligible
