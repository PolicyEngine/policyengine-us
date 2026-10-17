from policyengine_us.model_api import *


class SchoolMealTier(Enum):
    FREE = "Free"
    REDUCED = "Reduced price"
    PAID = "Paid"


class school_meal_tier(Variable):
    value_type = Enum
    label = "School meal tier"
    possible_values = SchoolMealTier
    default_value = SchoolMealTier.PAID
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "School meal tier that applies to both breakfast and lunch: federal "
        "eligibility plus state coverage of both meals (universal free meals, "
        "reduced-price copay coverage and free-meal income limits above the "
        "federal limit). State policies that cover only one meal apply in "
        "school_meal_breakfast_tier and school_meal_lunch_tier. FREE describes "
        "no family charge; it does not change the student's federal "
        "reimbursement category."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/245.2",
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_115C/GS_115C-264.html",
    )

    def formula(spm_unit, period, parameters):
        fpg_ratio = spm_unit("school_meal_fpg_ratio", period)
        p = parameters(period).gov.usda.school_meals
        p_income_limit = p.income.limit
        state = spm_unit.household("state_code_str", period)
        # Some states provide free meals above the federal free-meal income
        # limit; the higher of the two limits applies. Cast it to the ratio's
        # float32 precision so a ratio exactly at a limit such as 2.24 passes;
        # float32(2.24) is slightly above float64(2.24).
        free_income_limit = max_(
            p_income_limit.FREE, p.state_free_income_limit[state]
        ).astype(fpg_ratio.dtype)
        # Categorical eligibility provides free school meals.
        categorical_eligibility = spm_unit(
            "meets_school_meal_categorical_eligibility", period
        )
        # States with universal free meal policies provide the free tier
        # to all students regardless of household income.
        state_universal = spm_unit("state_has_universal_free_school_meals", period)
        # States that cover the reduced-price copay provide the free tier
        # to students who qualify for reduced-price meals.
        reduced_income_eligible = fpg_ratio <= p_income_limit.REDUCED
        state_covers_reduced_copay = p.state_covers_reduced_price_copay[state].astype(
            bool
        )
        return select(
            [
                (fpg_ratio <= free_income_limit)
                | categorical_eligibility
                | state_universal
                | (reduced_income_eligible & state_covers_reduced_copay),
                reduced_income_eligible,
            ],
            [SchoolMealTier.FREE, SchoolMealTier.REDUCED],
            default=SchoolMealTier.PAID,
        )
