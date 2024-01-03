from policyengine_us.model_api import *


class HUDIncomeLevel(Enum):
    ABOVE_MODERATE = "Above moderate"
    MODERATE = "Moderate"
    LOW = "Low"
    VERY_LOW = "Very low"
    ESPECIALLY_LOW = "Especially low"


class hud_income_level(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = HUDIncomeLevel
    default_value = HUDIncomeLevel.ABOVE_MODERATE
    label = "HUD income level"
    documentation = "Income level for HUD programs"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        # Get annual income.
        annual_income = spm_unit("hud_annual_income", period)
        # Get household size.
        size = spm_unit("spm_unit_size", period)
        # Get area median income.
        ami = spm_unit.household("ami", period)
        # avoid array divide-by-zero warning by not using where() function
        # see following GitHub issue for more details:
        # https://github.com/PolicyEngine/policyengine-us/issues/2496
        income_ami_ratio = np.zeros_like(ami)
        mask = ami != 0
        income_ami_ratio[mask] = annual_income[mask] / ami[mask]
        # Look up thresholds for each income level.
        p = parameters(period).gov.hud.ami_limit
        size_limit = p.family_size
        size_limit_excess = p.per_person_exceeding_4
        size_exceeding_4 = max_(size - 4, 0)
        size_capped_at_4 = min_(size, 4)
        moderate_threshold = (
            size_limit.MODERATE[size_capped_at_4]
            + size_limit_excess.MODERATE * size_exceeding_4
        )
        low_threshold = (
            size_limit.LOW[size_capped_at_4]
            + size_limit_excess.LOW * size_exceeding_4
        )
        very_low_threshold = (
            size_limit.VERY_LOW[size_capped_at_4]
            + size_limit_excess.VERY_LOW * size_exceeding_4
        )
        especially_low_threshold = (
            size_limit.ESPECIALLY_LOW[size_capped_at_4]
            + size_limit_excess.ESPECIALLY_LOW * size_exceeding_4
        )
        # Return the lowest matching one.
        return select(
            [
                income_ami_ratio <= especially_low_threshold,
                income_ami_ratio <= very_low_threshold,
                income_ami_ratio <= low_threshold,
                income_ami_ratio <= moderate_threshold,
            ],
            [
                HUDIncomeLevel.ESPECIALLY_LOW,
                HUDIncomeLevel.VERY_LOW,
                HUDIncomeLevel.LOW,
                HUDIncomeLevel.MODERATE,
            ],
            default=HUDIncomeLevel.ABOVE_MODERATE,
        )
