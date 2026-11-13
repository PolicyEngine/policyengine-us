from policyengine_us.model_api import *


def whole_dollar_ratio_limit(limit, fpg, dtype):
    """Return a federal school meal income limit as a poverty guideline ratio
    at its whole-dollar value.

    USDA multiplies the poverty guideline by the free (130%) and reduced-price
    (185%) income limits and rounds each product up to the next whole dollar
    (91 FR 17932, 17933); 7 CFR 245.3(a) adopts the guidelines USDA publishes
    by notice. Round the product to six decimal places before rounding up, so
    floating-point noise cannot add a dollar to a whole-dollar product while
    a fraction of a cent above a whole dollar, which projected guidelines can
    produce, still rounds up. Then divide the dollar limit by the guideline in
    the precision of school_meal_fpg_ratio, so a household exactly at the
    published limit passes. A zero guideline (the territories) keeps the
    unrounded limit.

    The product is rounded for each household size, the method the notice
    states. Above eight people, USDA's table instead adds a rounded
    per-member increment to the eight-person limit, which can differ by a
    dollar: for nine people in Hawaii in SY 2026-27 at 185%, the table gives
    $118,530 + $12,081 = $130,611, and the product gives
    ceil(1.85 * 70,600) = $130,610.
    """
    fpg = np.asarray(fpg, dtype=float)
    limit = np.broadcast_to(np.asarray(limit, dtype=float), fpg.shape)
    dollar_limit = np.ceil(np.round(limit * fpg, 6))
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
        "federal limit). The federal free (130%) and reduced-price (185%) "
        "income limits apply at the whole-dollar values USDA publishes: the "
        "poverty guideline times each limit, rounded up to the next whole "
        "dollar. State free-meal income limits are percentages of the poverty "
        "guideline set in state law and are compared with the poverty ratio "
        "exactly. State policies that cover only one meal apply in "
        "school_meal_breakfast_tier and school_meal_lunch_tier. FREE "
        "describes no family charge; it does not change the student's "
        "federal reimbursement category."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1758#b_1_A",
        "https://www.law.cornell.edu/cfr/text/7/245.2",
        "https://www.law.cornell.edu/cfr/text/7/245.3#a",
        "https://www.govinfo.gov/content/pkg/FR-2026-04-09/pdf/2026-06842.pdf#page=2",
        "https://pub.njleg.state.nj.us/Bills/2022/AL23/336_.HTM",
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_115C/GS_115C-264.html",
    )

    def formula(spm_unit, period, parameters):
        fpg_ratio = spm_unit("school_meal_fpg_ratio", period)
        fpg = spm_unit("spm_unit_fpg", period)
        p = parameters(period).gov.usda.school_meals
        p_income_limit = p.income.limit
        state = spm_unit.household("state_code_str", period)
        # The federal limits apply at USDA's published whole-dollar values.
        federal_free_income_limit = whole_dollar_ratio_limit(
            p_income_limit.FREE, fpg, fpg_ratio.dtype
        )
        reduced_income_limit = whole_dollar_ratio_limit(
            p_income_limit.REDUCED, fpg, fpg_ratio.dtype
        )
        # Some states provide free meals above the federal free-meal income
        # limit; the higher of the two limits applies. A state limit is the
        # percentage of the poverty guideline its law sets, such as New
        # Jersey's 224% under N.J.S.A. 18A:33-4(a), so compare it with the
        # ratio exactly, not at a dollar amount rounded up from it (backlog
        # id us-nj:school-meals-income-limit-rounding). Cast it to the
        # ratio's float32 precision so a ratio exactly at a limit such as
        # 2.24 passes; float32(2.24) is slightly above float64(2.24).
        state_free_income_limit = p.state_free_income_limit[state].astype(
            fpg_ratio.dtype
        )
        free_income_limit = max_(federal_free_income_limit, state_free_income_limit)
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
