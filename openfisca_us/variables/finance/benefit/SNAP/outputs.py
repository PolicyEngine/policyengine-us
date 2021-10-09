from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.entity.household import *
from variables.finance.benefit.SNAP.inputs import housing_cost
from variables.finance.benefit.SNAP.intermediate import (
    snap_expected_contribution_towards_food,
)  # not sure what I need here


class snap_monthly_benefit(Variable):

    value_type = int
    entity = household
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):

        SNAP_max_monthly_benefits = parameters(
            period
        ).benefits.SNAP.max_allotment

        state_group = spm_unit("state_group")

        household_size = spm_unit("household_size")

        return SNAP_max_monthly_benefits[household_size][
            state_group
        ] - spm_unit(snap_expected_contribution_towards_food)
