from policyengine_us.model_api import *


def whole_dollar_ratio_limit(limit, fpg, dtype):
    """Return a poverty guideline ratio limit at its whole-dollar value.

    USDA multiplies the poverty guideline by each school meal income limit
    and rounds the result up to the next whole dollar (91 FR 17932, 17933),
    and states publish their limits the same way (New Jersey Form 427). Round
    the product to cents first so floating-point noise cannot add a dollar,
    then divide the dollar limit by the guideline in the precision of
    school_meal_fpg_ratio, so a household exactly at the published limit
    passes. A zero guideline (the territories) keeps the unrounded limit.
    """
    fpg = np.asarray(fpg, dtype=float)
    limit = np.broadcast_to(np.asarray(limit, dtype=float), fpg.shape)
    dollar_limit = np.ceil(np.round(limit * fpg, 2))
    return np.divide(
        dollar_limit.astype(dtype),
        fpg.astype(dtype),
        out=limit.astype(dtype),
        where=fpg > 0,
    )


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
        "federal limit). Income limits apply in whole dollars: the poverty "
        "guideline times each limit, rounded up to the next whole dollar, as "
        "USDA and the states publish them. State policies that cover only one "
        "meal apply in school_meal_breakfast_tier and school_meal_lunch_tier. "
        "FREE describes no family charge; it does not change the student's "
        "federal reimbursement category."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1758#b_1_A",
        "https://www.law.cornell.edu/cfr/text/7/245.2",
        "https://www.govinfo.gov/content/pkg/FR-2026-04-09/pdf/2026-06842.pdf#page=2",
        "https://www.nj.gov/agriculture/divisions/fn/pdf/Form%20427%20Federal%20and%20State%20Income%20Eligibility%20Guidelines%20SY%202026-2027.pdf#page=1",
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_115C/GS_115C-264.html",
    )

    def formula(spm_unit, period, parameters):
        fpg_ratio = spm_unit("school_meal_fpg_ratio", period)
        fpg = spm_unit("spm_unit_fpg", period)
        p = parameters(period).gov.usda.school_meals
        p_income_limit = p.income.limit
        state = spm_unit.household("state_code_str", period)
        # Some states provide free meals above the federal free-meal income
        # limit; the higher of the two limits applies. Compare each limit at
        # its published whole-dollar value, rounded up from the guideline
        # times the limit.
        free_income_limit = whole_dollar_ratio_limit(
            max_(p_income_limit.FREE, p.state_free_income_limit[state]),
            fpg,
            fpg_ratio.dtype,
        )
        reduced_income_limit = whole_dollar_ratio_limit(
            p_income_limit.REDUCED, fpg, fpg_ratio.dtype
        )
        # Categorical eligibility provides free school meals.
        categorical_eligibility = spm_unit(
            "meets_school_meal_categorical_eligibility", period
        )
        # States with universal free meal policies provide the free tier
        # to all students regardless of household income.
        state_universal = spm_unit("state_has_universal_free_school_meals", period)
        # States that cover the reduced-price copay provide the free tier
        # to students who qualify for reduced-price meals.
        reduced_income_eligible = fpg_ratio <= reduced_income_limit
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
