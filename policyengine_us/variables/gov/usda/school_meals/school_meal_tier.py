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
        "SPM unit's combined school meal tier. FREE includes state-paid copays "
        "at a covered participating school and describes no family charge; "
        "it does not change the student's federal reimbursement category."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/245.2",
        "https://www.federalregister.gov/documents/2026/04/09/2026-06842/child-nutrition-programs-income-eligibility-guidelines",
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_115C/GS_115C-264.html",
    )

    def formula(spm_unit, period, parameters):
        fpg_ratio = spm_unit("school_meal_fpg_ratio", period)
        state = spm_unit.household("state_code_str", period)
        territory = np.isin(state, ["GU", "PR", "VI"])
        if territory.any():
            # USDA uses the contiguous-state income guideline for these
            # territories. Keep the shared ratio unchanged: CSFP and other
            # programs also consume it and need separate policy review.
            fpg = parameters(period).gov.hhs.fpg
            size = spm_unit("spm_unit_size", period)
            guideline = (
                fpg.first_person.CONTIGUOUS_US
                + fpg.additional_person.CONTIGUOUS_US * (size - 1)
            )
            income = spm_unit("school_meal_countable_income", period)
            territory_ratio = (income / guideline).astype(fpg_ratio.dtype)
            fpg_ratio = where(territory, territory_ratio, fpg_ratio)
        p = parameters(period).gov.usda.school_meals
        p_income_limit = p.income.limit
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
                (fpg_ratio <= p_income_limit.FREE)
                | categorical_eligibility
                | state_universal
                | (reduced_income_eligible & state_covers_reduced_copay),
                reduced_income_eligible,
            ],
            [SchoolMealTier.FREE, SchoolMealTier.REDUCED],
            default=SchoolMealTier.PAID,
        )
