from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.spm_unit import *
from openfisca_us.variables.demographic.household import *

# add new variable for enum tier


class school_meal_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = ""

    def formula(spm_unit, period, parameters):
        # Get state and poverty ratio for SPM unit.
        state_group = spm_unit.value_from_first_person(
            spm_unit.members.household("state_group", period).decode_to_str()
        )
        poverty_ratio = spm_unit("poverty_ratio", period)
        # Get parameters.
        p_school_meals = parameters(period).benefit.school_meals
        p_income_limit = p_school_meals.income_limit
        # Look up the free/reduced/full subsidy tier for each SPM unit by
        # poverty ratio.
        tier = select(
            [
                poverty_ratio < p_income_limit.free,
                poverty_ratio < p_income_limit.reduced_price,
                poverty_ratio >= p_income_limit.reduced_price,
            ],
            ["free", "reduced_price", "paid"],
        )
        p_amount = p_school_meals.amount
        # Get NSLP and SBP per child for each SPM unit.
        nslp_per_child = p_amount.NSLP[state_group][tier]
        sbp_per_child = p_amount.SBP[state_group][tier]
        # Add NSLP and SBP.
        school_meal_subsidy_per_child = nslp_per_child + sbp_per_child
        # Multiply by number of school days in the year and number of children.
        return (
            school_meal_subsidy_per_child
            * spm_unit("children", period)
            * p_school_meals.school_days
        )
