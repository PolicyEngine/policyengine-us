from policyengine_us.model_api import *


class md_meap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP regular heating eligibility"
    defined_for = StateCode.MD
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/07.03.21.03",
        "https://regs.maryland.gov/us/md/exec/comar/07.03.21.06",
        # PDF pages 11, 12, 16, 38, 39, 108.
        "https://dhs.maryland.gov/documents/OHEP/OHEP-Operations-Manual.pdf#page=11",
        "https://www.law.cornell.edu/uscode/text/42/8624",
    )
    documentation = (
        "Regular heating has no resource test. Application documentation, emancipation "
        "and program-year duplicate awards are not modeled. The regulation permits an "
        "annually announced medical-expense waiver, but no such regular-heating waiver "
        "was found in the FY2026 plan. At least one qualified member is required; a "
        "child counted regardless of status does not satisfy that requirement."
    )

    def formula(spm_unit, period, parameters):
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        dwelling = spm_unit("md_meap_dwelling_type", period)
        assisted_living = dwelling == dwelling.possible_values.ASSISTED_LIVING
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        income = spm_unit("md_meap_countable_income", period)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. The 60% SMI limit falls below that floor from
        # household size 29 in FY2025 to FY2027. md_meap_fpg already uses the
        # guideline of the calendar year before the model year.
        p_hhs = parameters(period).gov.hhs.liheap
        floor = np.round(spm_unit("md_meap_fpg", period) * p_hhs.fpg_floor, 2)
        # Manual page 38: categorical eligibility waives the income test but
        # not the other denials.
        income_eligible = (
            spm_unit("md_meap_categorically_eligible", period)
            | (income <= spm_unit("md_meap_income_limit", period))
            | (income < floor)
        )
        # Manual page 108: the household must have at least one eligible
        # (citizen or qualified alien) member.
        qualified_member = add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        return (
            income_eligible
            & qualified_member
            & (spm_unit("has_heating_expense", period) | heat_in_rent)
            & ~(heat_in_rent & subsidized)
            & ~assisted_living
        )
