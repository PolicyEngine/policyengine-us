from policyengine_us.model_api import *
from policyengine_us.variables.gov.usda.school_meals.school_meal_tier import (
    SchoolMealTier,
    whole_dollar_ratio_limit,
)


class school_meal_breakfast_tier(Variable):
    value_type = Enum
    label = "School breakfast tier"
    possible_values = SchoolMealTier
    default_value = SchoolMealTier.PAID
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "School meal tier for breakfast. It starts from school_meal_tier, the "
        "tier for both meals, and gives the FREE tier to all students in "
        "states with universal free breakfast, to reduced-price students in "
        "states that cover only the reduced-price breakfast copay, and to "
        "students at or below a state's breakfast-only free-meal income limit, "
        "rounded up to the next whole dollar as in school_meal_tier."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1773#e_1_A",
        "https://www.law.cornell.edu/cfr/text/7/245.2",
        "https://www.govinfo.gov/content/pkg/FR-2026-04-09/pdf/2026-06842.pdf#page=2",
        "https://www.ncleg.gov/EnactedLegislation/SessionLaws/HTML/2011-2012/SL2011-342.html",
        "https://gc.nh.gov/rsa/html/XV/189/189-11-a.htm",
        "https://mgaleg.maryland.gov/2026RS/Statute_Web/ged/7-602.pdf#page=2",
        # PDF pages 702, 1005-1006
        "https://www.lbb.texas.gov/Documents/GAA/General_Appropriations_Act_2024_2025.pdf#page=702",
        "https://lawfilesext.leg.wa.gov/biennium/2005-06/Pdf/Bills/Session%20Laws/Senate/6386-S.SL.pdf#page=212",
        "https://lawfilesext.leg.wa.gov/biennium/2021-22/Pdf/Bills/Session%20Laws/Senate/5092-S.SL.pdf#page=997",
        # PDF pages 2-4
        "https://leg.colorado.gov/sites/default/files/images/olls/2007a_sl_229.pdf#page=2",
        # PDF pages 2, 175
        "https://lldc.mainelegislature.org/Open/Laws/2007/2007_PL_c539.pdf#page=2",
        "https://www.revisor.mn.gov/laws/2003/1/Session+Law/Chapter/9/",
        "https://www.oregonlegislature.gov/bills_laws/lawsstatutes/2009orLaw0885.html",
        # PDF pages 4-6
        "https://legislature.vermont.gov/Documents/2010/Docs/ACTS/ACT087/ACT087%20As%20Enacted.pdf#page=4",
        "https://pub.njleg.state.nj.us/Bills/2022/AL23/336_.HTM",
        "https://www.nj.gov/agriculture/divisions/fn/pdf/Form%20427%20Federal%20and%20State%20Income%20Eligibility%20Guidelines%20SY%202026-2027.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        # The tier for both meals already includes state coverage of both
        # meals, so only breakfast-specific state policies apply here.
        tier = spm_unit("school_meal_tier", period)
        universal_free_breakfast = spm_unit(
            "state_has_universal_free_school_breakfast", period
        )
        state = spm_unit.household("state_code_str", period)
        p = parameters(period).gov.usda.school_meals
        state_covers_reduced_copay = p.state_covers_reduced_price_copay_breakfast_only[
            state
        ].astype(bool)
        # Some states set a free-breakfast income limit above their limit for
        # both meals (0 means none). Apply it only where it is set, so a
        # school_meal_tier input still reaches breakfast unchanged elsewhere,
        # and compare it at its published whole-dollar value, as
        # school_meal_tier does.
        fpg_ratio = spm_unit("school_meal_fpg_ratio", period)
        breakfast_income_limit = p.state_free_income_limit_breakfast_only[state]
        breakfast_ratio_limit = whole_dollar_ratio_limit(
            breakfast_income_limit,
            spm_unit("spm_unit_fpg", period),
            fpg_ratio.dtype,
        )
        breakfast_income_eligible = (breakfast_income_limit > 0) & (
            fpg_ratio <= breakfast_ratio_limit
        )
        reduced = tier == tier.possible_values.REDUCED
        return select(
            [
                (tier == tier.possible_values.FREE)
                | universal_free_breakfast
                | (reduced & state_covers_reduced_copay)
                | breakfast_income_eligible,
                reduced,
            ],
            [SchoolMealTier.FREE, SchoolMealTier.REDUCED],
            default=SchoolMealTier.PAID,
        )
