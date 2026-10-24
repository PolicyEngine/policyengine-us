from policyengine_us.model_api import *


class ut_heat_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Utah HEAT regular heating assistance eligibility"
    defined_for = StateCode.UT
    reference = (
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/Obsolete_Policy/Obsolete_200/Obsolete_202_(03_01_26_to_09_30_26)_Eligibility_Standards.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/Obsolete_Policy/Obsolete_200/Obsolete_208_(03_01_26_to_09_30_26)_Vulnerability.htm",
        "https://liheapch.acf.gov/docs/2026/state-plans/UT_Plan_2026.pdf#page=8",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.heat.eligibility
        has_adult = spm_unit.any(spm_unit.members("age", period) >= p.adult_age)
        size = spm_unit("ut_heat_household_size", period)
        income = spm_unit("ut_heat_countable_income", period)
        limit = spm_unit("ut_heat_income_limit", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        directly_paid = (
            spm_unit("has_heating_expense", period)
            | (spm_unit("heating_expense", period) > 0)
            | (spm_unit("pre_subsidy_electricity_expense", period) > 0)
        )
        fuel = spm_unit("heating_type", period)
        own_wood = fuel == fuel.possible_values.WOOD
        responsible = directly_paid | (heat_in_rent & ~subsidized) | own_wood
        housing_eligible = ~subsidized | directly_paid
        supported_fuel = spm_unit("ut_heat_energy_cost_standard", period) > 0
        # The annual potential award assumes no prior seasonal payment or
        # disqualifying utility credit balance. Emancipation, institutions,
        # tribal duplicate assistance and special RV rules are unobserved.
        # Self-supplied firewood qualifies without a bill. Subsidized housing
        # requires a separately paid utility; subsidies alone are not expenses.
        # The existing heating-cost flag can supply that separate obligation
        # when the primary fuel bill does not capture it.
        return (
            (size > 0)
            & has_adult
            & (income <= limit)
            & responsible
            & housing_eligible
            & supported_fuel
        )
