from policyengine_us.model_api import *


class la_liheap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Louisiana LIHEAP regular cooling eligibility"
    defined_for = StateCode.LA
    reference = (
        # PDF pages 33, 41, 43, 46-47
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20FINAL%20-%20Effective%20April%201%2c%202026.pdf#page=33",
        # PDF pages 11-12
        "https://liheapch.acf.gov/docs/2026/state-plans/LA_Plan_2026.pdf#page=11",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("la_liheap_household_size", period)
        income_eligible = spm_unit("la_liheap_income_eligible", period)
        # Vulnerability: responsibility for a cooling bill, or energy costs
        # included in the rent (Section 3.6 E.1; plan section 3.3).
        utilities_in_rent = ~spm_unit.household("tenant_pays_utilities", period) & (
            add(spm_unit, period, ["rent"]) > 0
        )
        responsible = spm_unit("has_cooling_expense", period) | utilities_in_rent
        # A home with no heating or any known heating fuel qualifies; an
        # unspecified fuel is paid $0, as in every LIHEAP program (#9754).
        heating_type = spm_unit("heating_type", period)
        fuel_known = heating_type != heating_type.possible_values.UNSPECIFIED
        # As for heating, a subsidized household needs a positive total energy
        # cost: a cooling utility allowance greater than the bill makes it
        # ineligible (Section 4.1 C.1).
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        energy_cost_eligible = ~subsidized | (
            spm_unit("la_liheap_energy_cost", period) > 0
        )
        return (
            (size > 0)
            & income_eligible
            & responsible
            & fuel_known
            & energy_cost_eligible
        )
