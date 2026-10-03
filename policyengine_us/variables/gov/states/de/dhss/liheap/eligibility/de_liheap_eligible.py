from policyengine_us.model_api import *


class de_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Delaware LIHEAP regular heating assistance"
    defined_for = StateCode.DE
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/DE_Plan_2026.pdf#page=9",
        # Historical manual sections 424 and 426, page 40.
        "https://bidcondocs.delaware.gov/HSS/HSS_15027Liheap_MAN.pdf#page=40",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("de_liheap_household_size", period)
        income = spm_unit("de_liheap_countable_income", period)
        limit = spm_unit("de_liheap_income_limit", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period)
        pays_for_heat = spm_unit("has_heating_expense", period)
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        supported_fuel = (
            (fuel != types.NONE) & (fuel != types.UNSPECIFIED) & (fuel != types.SOLAR)
        )
        # Full-rent households use the electric column even if the building's
        # fuel is unknown. Solar has no separately supported matrix mapping.
        heating_responsibility = where(
            heat_in_rent,
            ~subsidized & (fuel != types.NONE),
            pays_for_heat & supported_fuel,
        )
        # SPMUnit approximates the energy-sharing household. Application,
        # funding, boarder/absence exceptions and duplicate claims are not
        # represented by existing inputs; they are not automatic exclusions.
        return (size > 0) & (income <= limit) & heating_responsibility
