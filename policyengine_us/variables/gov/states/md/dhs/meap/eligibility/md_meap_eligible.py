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
        "https://dhs.maryland.gov/documents/OHEP/OHEP-Operations-Manual.pdf#page=11,12,16,39",
    )
    documentation = "Regular heating has no resource test. Assisted-living residence, application documentation, emancipation, program-year duplicate awards and the optional medical waiver are not modeled. At least one qualified member is required."

    def formula(spm_unit, period, parameters):
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        income_eligible = spm_unit("md_meap_categorically_eligible", period) | (
            spm_unit("md_meap_countable_income", period)
            <= spm_unit("md_meap_income_limit", period)
        )
        return (
            income_eligible
            & (spm_unit("md_meap_household_size", period) > 0)
            & (spm_unit("has_heating_expense", period) | heat_in_rent)
            & ~(heat_in_rent & subsidized)
        )
