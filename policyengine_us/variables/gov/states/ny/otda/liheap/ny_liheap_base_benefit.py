from policyengine_us.model_api import *
from policyengine_us.variables.household.expense.utilities.heating_fuel import (
    HeatingFuel,
)


class ny_liheap_base_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "NY HEAP base benefit amount"
    definition_period = YEAR
    defined_for = "ny_liheap_income_eligible"
    unit = USD
    documentation = "Base HEAP benefit amount before vulnerable supplement"

    def formula(spm_unit, period, parameters):
        # NY HEAP program year starts November 2024
        if period.start.year < 2025:
            return 0

        p = parameters(period).gov.states.ny.otda.liheap.benefit

        # Check housing type
        receives_housing_assistance = spm_unit(
            "receives_housing_assistance", period
        )
        heat_included_in_rent = spm_unit(
            "heat_expense_included_in_rent", period
        )

        # Get heating fuel type
        heating_fuel = spm_unit("heating_fuel", period)

        # Household size for rent with heat benefit
        household_size = spm_unit("spm_unit_size", period)

        # Calculate base benefit amount
        # TODO: Consider refactoring heating fuel benefits into a single
        # parameter file with breakdown by heating_fuel enum values
        return where(
            receives_housing_assistance,
            p.subsidized_housing,
            where(
                heat_included_in_rent,
                p.rent_with_heat.calc(household_size),
                select(
                    [
                        heating_fuel == HeatingFuel.NATURAL_GAS,
                        heating_fuel == HeatingFuel.ELECTRICITY,
                        heating_fuel == HeatingFuel.OIL,
                        heating_fuel == HeatingFuel.PROPANE,
                        heating_fuel == HeatingFuel.KEROSENE,
                        heating_fuel == HeatingFuel.WOOD,
                        heating_fuel == HeatingFuel.COAL,
                        heating_fuel == HeatingFuel.CORN,
                    ],
                    [
                        p.natural_gas,
                        p.electricity,
                        p.oil,
                        p.propane,
                        p.kerosene,
                        p.wood,
                        p.coal,
                        p.corn,
                    ],
                    default=0,
                ),
            ),
        )
