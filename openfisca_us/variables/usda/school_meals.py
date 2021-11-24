from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.spm_unit import *
from openfisca_us.variables.demographic.household import *

# add new variable for enum tier


class spm_unit_school_meal_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "SPM unit's countable income for school meal program"


class spm_unit_school_meal_fpg_ratio(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "SPM unit's federal poverty ratio for school meal program"

    def formula(spm_unit, period, parameters):
        return spm_unit(
            "spm_unit_school_meal_countable_income", period
        ) / spm_unit("spm_unit_fpg", period)


class SchoolMealTier(Enum):
    FREE = "Free"
    REDUCED = "Reduced price"
    FULL = "Full"


class spm_unit_school_meal_tier(Variable):
    value_type = Enum
    possible_values = SchoolMealTier
    default_value = SchoolMealTier.FULL
    entity = SPMUnit
    definition_period = YEAR
    documentation = "SPM unit's school meal program tier"

    def formula(spm_unit, period, parameters):
        fpg_ratio = spm_unit("spm_unit_school_meal_fpg_ratio", period)
        p_income_limit = parameters(period).usda.school_meals.income_limit
        return select(
            [
                fpg_ratio <= p_income_limit.FREE,
                fpg_ratio <= p_income_limit.REDUCED,
                True,
            ],
            [SchoolMealTier.FREE, SchoolMealTier.REDUCED, SchoolMealTier.FULL],
        )


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
        poverty_ratio = spm_unit("spm_unit_school_meal_fpg_ratio", period)
        # Get parameters.
        p_school_meals = parameters(period).usda.school_meals
        tier = spm_unit("spm_unit_school_meal_tier")
        p_amount = p_school_meals.amount
        # Get NSLP and SBP per child for each SPM unit.
        nslp_per_child = p_amount.nslp[state_group][tier]
        sbp_per_child = p_amount.sbp[state_group][tier]
        # Add NSLP and SBP.
        school_meal_subsidy_per_child = nslp_per_child + sbp_per_child
        # Multiply by number of school days in the year and number of children.
        children = spm_unit.sum(spm_unit.members("age", period) < 18)
        return (
            school_meal_subsidy_per_child
            * children
            * p_school_meals.school_days
        )
