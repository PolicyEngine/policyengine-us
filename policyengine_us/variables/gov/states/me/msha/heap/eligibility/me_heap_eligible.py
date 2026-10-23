from policyengine_us.model_api import *


class me_heap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Maine HEAP regular heating eligibility"
    defined_for = StateCode.ME
    reference = (
        # PDF pages 2-3, 6, 10-11, 15-17
        "https://www.mainehousing.org/docs/default-source/msha-rules/ch24-home-energy-assistance-program-rule.pdf#page=2",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/346c024.docx",
        # PDF pages 1-2
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ME_BenefitMatrix_2026.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("me_heap_household_size", period)
        income = spm_unit("me_heap_income", period)
        limit = spm_unit("me_heap_income_limit", period)
        categorical = spm_unit("me_heap_categorically_eligible", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        # Rule 3(A)(4) requires a Direct Energy Cost (a heating bill the
        # household pays) or an Indirect Determinable Energy Cost (heat
        # included in rent), and the points matrix lists the fuels.
        energy_cost = spm_unit("has_heating_expense", period) | heat_in_rent
        # SOLAR with an electricity bill stands for a grid-tied home with
        # electric heat and uses the electricity row; an off-grid solar-only
        # home has no heating bill. NONE means the home has no heating.
        # Subsidized tenants with heat in rent receive the nominal benefit
        # without a listed fuel; OTHER and UNSPECIFIED are otherwise
        # ineligible because heating_type is a required input.
        fuel = spm_unit("heating_type", period)
        fuels = fuel.possible_values
        listed_fuel = (
            (fuel == fuels.ELECTRICITY)
            | (fuel == fuels.SOLAR)
            | (fuel == fuels.PROPANE)
            | (fuel == fuels.KEROSENE)
            | (fuel == fuels.FUEL_OIL)
            | (fuel == fuels.COAL)
            | (fuel == fuels.NATURAL_GAS)
            | (fuel == fuels.WOOD)
        )
        return (
            (size > 0)
            & ((income <= limit) | categorical)
            & energy_cost
            & (fuel != fuels.NONE)
            & (listed_fuel | (heat_in_rent & subsidized))
        )
