from openfisca_us.model_api import *


class snap_minimum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Minimum benefit for SNAP"
    unit = USD

    def formula(spm_unit, period, parameters):
        # Parameters for the minimum benefit.
        snap = parameters(period).usda.snap
        min_benefit = snap.minimum_benefit
        # Calculate the relevant maximum benefit, defined as the maximum
        # benefit for a household of a certain size in their state.
        state_group = spm_unit.household("state_group_str", period)
        relevant_max_benefit = (
            snap.amount.main[state_group][
                str(min_benefit.relevant_max_benefit_household_size)
            ]
            * 12
        )
        # Minimum benefits only apply to households up to a certain size.
        household_size = spm_unit.nb_persons()
        min_share_of_max = where(
            household_size <= min_benefit.maximum_household_size,
            min_benefit.rate,
            0,
        )
        return relevant_max_benefit * min_share_of_max
