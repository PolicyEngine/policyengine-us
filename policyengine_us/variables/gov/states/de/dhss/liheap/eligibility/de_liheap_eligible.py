from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class de_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Delaware LIHEAP regular heating assistance"
    defined_for = StateCode.DE
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        "https://liheapch.acf.gov/docs/2026/state-plans/DE_Plan_2026.pdf#page=9",
        # Historical manual sections 424 and 426, page 40.
        "https://bidcondocs.delaware.gov/HSS/HSS_15027Liheap_MAN.pdf#page=40",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period)
        size = spm_unit("de_liheap_household_size", period)
        income = spm_unit("de_liheap_countable_income", period)
        limit = spm_unit("de_liheap_income_limit", period)
        guideline = fpg(
            max_(size, 1),
            spm_unit.household("state_group_str", period),
            period,
            parameters,
            year_lag=p.gov.states.de.dhss.liheap.eligibility.fpg_year_lag,
        )
        federal_floor = np.round(guideline * p.gov.hhs.liheap.fpg_floor, 2)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period)
        pays_for_heat = spm_unit("has_heating_expense", period)
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        known_fuel = (fuel != types.NONE) & (fuel != types.UNSPECIFIED)
        # Full-rent households use the electric column even if the building's
        # fuel is unknown. Solar with a matching supplemental-electric bill may
        # reach the fuel-independent subsidized flat award; its ordinary matrix
        # price remains unsupported.
        heating_responsibility = where(
            heat_in_rent,
            ~subsidized & (fuel != types.NONE),
            pays_for_heat & known_fuel,
        )
        # SPMUnit approximates the energy-sharing household. Application,
        # funding, boarder/absence exceptions and duplicate claims are not
        # represented by existing inputs; they are not automatic exclusions.
        return (
            (size > 0)
            & ((income <= limit) | (income < federal_floor))
            & heating_responsibility
        )
