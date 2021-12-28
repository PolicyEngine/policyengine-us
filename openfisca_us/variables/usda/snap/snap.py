from openfisca_us.model_api import *


class snap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Final SNAP benefit amount, equal to net income minus food contribution"
    label = "SNAP benefit entitlement"
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    unit = "currency-USD"

    def formula(spm_unit, period):
        # Federal SNAP rules are defined in U.S.C Title 7, Chapter 51, which also
        # defines state powers to modify the rules.
        eligible = spm_unit("is_snap_eligible", period)
        expected_contribution = spm_unit("snap_expected_contribution", period)
        return eligible * max_(
            spm_unit("snap_minimum_benefit", period),
            spm_unit("snap_max_benefit", period) - expected_contribution,
        )
